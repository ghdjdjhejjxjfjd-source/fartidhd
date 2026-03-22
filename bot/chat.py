# bot/chat.py - ПОЛНАЯ ВЕРСИЯ С ЛОКАЛИЗАЦИЕЙ
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
from .locales import get_text

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
        await query.message.reply_text(get_text(uid, "blocked_access"))
        return
    
    if not a.get("is_free") and balance < cost:
        text = get_text(uid, "insufficient_stars").format(cost=cost)
        await query.message.reply_text(text)
        return
    
    mode_names = {
        "fast": get_text(uid, "ai_mode_fast"),
        "quality": get_text(uid, "ai_mode_quality")
    }
    
    style_names = {
        "short": get_text(uid, "style_short"),
        "steps": get_text(uid, "style_steps"),
        "detail": get_text(uid, "style_detail")
    }
    
    lang_names = {
        "ru": get_text(uid, "lang_ru"),
        "en": get_text(uid, "lang_en"),
        "kk": get_text(uid, "lang_kk"),
        "tr": get_text(uid, "lang_tr"),
        "uk": get_text(uid, "lang_uk"),
        "fr": get_text(uid, "lang_fr")
    }
    
    current_style = get_user_style(uid)
    
    context.user_data["invite_message_id"] = query.message.message_id
    
    # Текст приглашения
    if ai_mode == "fast":
        current_ai_lang = get_user_ai_lang(uid)
        text = get_text(uid, "inline_chat_start_fast").format(
            mode=mode_names[ai_mode],
            lang=lang_names.get(current_ai_lang, get_text(uid, "lang_ru")),
            style=style_names.get(current_style, get_text(uid, "style_steps")),
            cost=cost
        )
    else:
        text = get_text(uid, "inline_chat_start_quality").format(
            mode=mode_names[ai_mode],
            style=style_names.get(current_style, get_text(uid, "style_steps")),
            cost=cost
        )
    
    # КНОПКА НАЗАД на стартовом экране
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(uid, "back_btn"), callback_data="exit_chat_from_start")]
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
    
    # Названия для режима ИИ
    ai_mode_names = {
        "fast": get_text(uid, "ai_mode_fast"),
        "quality": get_text(uid, "ai_mode_quality")
    }
    
    # Названия для характера
    persona_names = {
        "friendly": get_text(uid, "persona_friendly"),
        "fun": get_text(uid, "persona_fun"),
        "smart": get_text(uid, "persona_smart"),
        "strict": get_text(uid, "persona_strict")
    }
    
    # Названия для стиля
    style_names = {
        "short": get_text(uid, "style_short"),
        "steps": get_text(uid, "style_steps"),
        "detail": get_text(uid, "style_detail")
    }
    
    if a.get("is_blocked"):
        await update.message.reply_text(get_text(uid, "blocked_access"))
        context.user_data["in_chat_mode"] = False
        return
    
    balance = get_balance(uid)
    if not a.get("is_free") and balance < cost:
        text_msg = get_text(uid, "insufficient_stars").format(cost=cost)
        await update.message.reply_text(text_msg)
        context.user_data["in_chat_mode"] = False
        return
    
    # Удаляем кнопку со стартового экрана
    if "start_message_id" in context.user_data:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=uid,
                message_id=context.user_data["start_message_id"],
                reply_markup=None
            )
            print(f"✅ Кнопка удалена со стартового экрана {context.user_data['start_message_id']}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку со старта: {e}")
    
    mem_add(uid, "user", text)
    typing_msg = await update.message.reply_text("⏳ Печатает...")
    
    try:
        history = mem_get(uid, limit=20)
        prompt_with_memory = build_memory_prompt(history, text)
        
        if ai_mode == "fast":
            reply = ask_groq(prompt_with_memory, lang=ai_lang, persona=persona, style=style)
        else:
            reply = ask_openai(prompt_with_memory, lang=ai_lang, persona=persona, style=style)
        
        if reply:
            await typing_msg.delete()
            mem_add(uid, "assistant", reply)
            
            # Удаляем кнопку с предыдущего ответа ИИ
            if uid in last_bot_message_with_button:
                try:
                    await context.bot.edit_message_reply_markup(
                        chat_id=uid,
                        message_id=last_bot_message_with_button[uid],
                        reply_markup=None
                    )
                except Exception as e:
                    print(f"⚠️ Не удалось убрать кнопку с прошлого сообщения: {e}")
            
            # Отправляем новый ответ С КНОПКОЙ
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(uid, "back_btn"), callback_data="exit_chat")]
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
                f"⚡ Режим: {ai_mode_names.get(ai_mode, ai_mode)}, стоимость: {cost} ⭐\n"
                f"🎭 Характер: {persona_names.get(persona, persona)}\n"
                f"📝 Стиль: {style_names.get(style, style)}"
            )
            
            send_log_to_group(log_text)
            
    except Exception as e:
        await typing_msg.edit_text(f"❌ Ошибка")
        context.user_data["in_chat_mode"] = False


async def exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Выход из чата в главное меню (только одно меню)"""
    
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
    
    # 2. Очищаем стартовое сообщение из памяти если есть
    if "start_message_id" in context.user_data:
        del context.user_data["start_message_id"]
    
    # 3. Выходим из режима чата
    context.user_data["in_chat_mode"] = False
    
    # 4. Отправляем/обновляем меню (send_fresh_menu сам удалит старое)
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Меню отправлено для {uid}")


async def exit_chat_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Выход из чата со стартового экрана"""
    
    print(f"🚪 Выход со стартового экрана для {uid}")
    
    # Удаляем стартовое сообщение
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
            print(f"✅ Стартовое сообщение удалено")
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    # Очищаем данные
    if "start_message_id" in context.user_data:
        del context.user_data["start_message_id"]
    
    context.user_data["in_chat_mode"] = False
    
    # Отправляем/обновляем меню (send_fresh_menu сам удалит старое)
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Меню отправлено для {uid}")