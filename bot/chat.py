# bot/chat.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С ЛОКАЛИЗАЦИЕЙ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

from api import (
    get_access, get_user_persona, get_user_lang, get_user_ai_lang, 
    get_user_style, get_ai_mode, increment_messages, add_stars_spent,
    mem_get, mem_add, build_memory_prompt, clear_last_menu, set_last_menu
)
from payments import get_balance, spend_stars
from groq_client import ask_groq
from openai_client import ask_openai
from .config import send_log_http
from .menu import main_menu_for_user
from .utils import send_fresh_menu, delete_prev_menu
from .locales import get_text, get_button_text, get_mode_name, get_style_name, get_lang_name, get_persona_name

# Глобальное хранилище ID последнего сообщения с кнопкой
last_bot_message_with_button = {}

async def inline_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    ai_mode = get_ai_mode(uid)
    cost = 0.3 if ai_mode == "fast" else 1.0
    
    if a.get("is_blocked"):
        await query.message.reply_text(get_text(uid, "blocked"))
        return
    
    if not a.get("is_free") and balance < cost:
        await query.message.reply_text(get_text(uid, "need_stars_chat"))
        return
    
    current_style = get_user_style(uid)
    
    context.user_data["invite_message_id"] = query.message.message_id
    
    # Текст приглашения
    if ai_mode == "fast":
        current_ai_lang = get_user_ai_lang(uid)
        text = get_text(uid, "chat_start_fast").format(
            mode=get_mode_name(uid, ai_mode),
            ai_lang=get_lang_name(uid, current_ai_lang),
            style=get_style_name(uid, current_style),
            cost=cost
        )
    else:
        text = get_text(uid, "chat_start_quality").format(
            mode=get_mode_name(uid, ai_mode),
            style=get_style_name(uid, current_style),
            cost=cost
        )
    
    # КНОПКА НАЗАД на стартовом экране
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_button_text(uid, "back"), callback_data="exit_chat_from_start")]
    ])
    
    sent_msg = await query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )
    
    # Запоминаем ID стартового сообщения
    context.user_data["start_message_id"] = sent_msg.message_id
    context.user_data["in_chat_mode"] = True
    print(f"✅ Чат режим включен для {uid}")

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, text: str):
    a = get_access(uid)
    ai_lang = get_user_ai_lang(uid)
    persona = get_user_persona(uid)
    style = get_user_style(uid)
    ai_mode = get_ai_mode(uid)
    cost = 0.3 if ai_mode == "fast" else 1.0
    
    if a.get("is_blocked"):
        await update.message.reply_text(get_text(uid, "blocked"))
        context.user_data["in_chat_mode"] = False
        return
    
    balance = get_balance(uid)
    if not a.get("is_free") and balance < cost:
        await update.message.reply_text(get_text(uid, "need_stars_chat"))
        context.user_data["in_chat_mode"] = False
        return
    
    # ===== УДАЛЯЕМ КНОПКУ СО СТАРТОВОГО ЭКРАНА =====
    if "start_message_id" in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=uid,
                message_id=context.user_data["start_message_id"]
            )
            print(f"✅ Стартовое сообщение удалено {context.user_data['start_message_id']}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
        
        del context.user_data["start_message_id"]
    
    mem_add(uid, "user", text)
    
    # Отправляем сообщение "Печатает..." (оно будет удалено)
    typing_msg = await update.message.reply_text(get_text(uid, "typing"))
    
    try:
        history = mem_get(uid, limit=20)
        prompt_with_memory = build_memory_prompt(history, text)
        
        if ai_mode == "fast":
            reply = ask_groq(prompt_with_memory, lang=ai_lang, persona=persona, style=style)
        else:
            reply = ask_openai(prompt_with_memory, lang=ai_lang, persona=persona, style=style)
        
        if reply:
            # ===== УДАЛЯЕМ СООБЩЕНИЕ "Печатает..." =====
            await typing_msg.delete()
            print(f"✅ Сообщение 'Печатает...' удалено")
            
            mem_add(uid, "assistant", reply)
            
            # Удаляем кнопку с предыдущего ответа ИИ
            if uid in last_bot_message_with_button:
                try:
                    await context.bot.edit_message_reply_markup(
                        chat_id=uid,
                        message_id=last_bot_message_with_button[uid],
                        reply_markup=None
                    )
                    print(f"✅ Кнопка удалена с прошлого ответа {last_bot_message_with_button[uid]}")
                except Exception as e:
                    print(f"⚠️ Не удалось убрать кнопку с прошлого ответа: {e}")
            
            # Отправляем новый ответ С КНОПКОЙ
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(get_button_text(uid, "back"), callback_data="exit_chat")]
            ])
            
            sent_msg = await context.bot.send_message(
                chat_id=uid,
                text=reply,
                reply_markup=keyboard
            )
            
            # Запоминаем это сообщение как последнее с кнопкой
            last_bot_message_with_button[uid] = sent_msg.message_id
            
            if not a.get("is_free"):
                spend_stars(uid, cost)
                add_stars_spent(uid, cost)
            
            increment_messages(uid)
            
            # ===== ПОДРОБНЫЙ ЛОГ =====
            from api.config import send_log_to_group
            
            user = update.effective_user
            username = f"@{user.username}" if user.username else "—"
            first_name = user.first_name or "—"
            
            new_balance = get_balance(uid)
            
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_text = (
                f"🕒 {time_str}\n"
                f"👤 {first_name} (@{username})\n"
                f"🆔 {uid}\n"
                f"💰 Баланс: {new_balance} ⭐\n"
                f"\n"
                f"💬 Запрос:\n"
                f"{text}\n"
                f"\n\n\n\n\n"
                f"🤖 Ответ:\n"
                f"{reply}\n"
                f"\n\n\n\n\n"
                f"⚡ Режим: {get_mode_name(uid, ai_mode)}, стоимость: {cost} ⭐\n"
                f"🎭 Характер: {get_persona_name(uid, persona)}\n"
                f"📝 Стиль: {get_style_name(uid, style)}"
            )
            
            send_log_to_group(log_text)
            
    except Exception as e:
        await typing_msg.delete()
        await update.message.reply_text(get_text(uid, "error").format(error=str(e)[:100]))
        context.user_data["in_chat_mode"] = False

async def exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """
    Выход из чата в главное меню.
    Удаляем кнопку с последнего ответа ИИ, затем удаляем СТАРОЕ меню и отправляем НОВОЕ.
    """
    
    print(f"🚪 Выход из чата для {uid}")
    
    # 1. Удаляем кнопку с последнего ответа ИИ (НО НЕ САМО СООБЩЕНИЕ)
    if uid in last_bot_message_with_button:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=uid,
                message_id=last_bot_message_with_button[uid],
                reply_markup=None
            )
            print(f"✅ Кнопка удалена с сообщения {last_bot_message_with_button[uid]}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку: {e}")
        
        del last_bot_message_with_button[uid]
    
    # 2. Очищаем данные из контекста
    context.user_data.pop("start_message_id", None)
    context.user_data.pop("in_chat_mode", None)
    
    # 3. Удаляем СТАРОЕ меню пользователя
    await delete_prev_menu(context.bot, uid)
    
    # 4. Отправляем НОВОЕ меню
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Новое меню отправлено для {uid}")

async def exit_chat_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """
    Выход из чата со стартового экрана (до отправки сообщения).
    """
    
    print(f"🚪 Выход со стартового экрана для {uid}")
    
    query = update.callback_query
    
    # Удаляем стартовое сообщение
    if query and query.message:
        try:
            await query.message.delete()
            print(f"✅ Стартовое сообщение удалено")
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    # Очищаем данные
    context.user_data.pop("start_message_id", None)
    context.user_data.pop("in_chat_mode", None)
    
    # Удаляем СТАРОЕ меню
    await delete_prev_menu(context.bot, uid)
    
    # Отправляем НОВОЕ меню
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Новое меню отправлено для {uid}")