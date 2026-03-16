from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from api import (
    get_access, get_user_persona, get_user_lang, get_user_ai_lang, 
    get_user_style, get_ai_mode, increment_messages, add_stars_spent,
    mem_get, mem_add, build_memory_prompt
)
from payments import get_balance, spend_stars
from groq_client import ask_groq
from openai_client import ask_openai
from .config import send_log_http
from .menu import main_menu_for_user
from .utils import send_fresh_menu

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
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < cost:
        await query.message.reply_text(
            f"❌ Недостаточно звезд (нужно {cost}⭐).\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    # Названия режимов
    mode_names = {
        "fast": "🚀 Быстрый", 
        "quality": "💎 Качественный"
    }
    
    style_names = {
        "short": "📏 Коротко", 
        "steps": "📋 По шагам", 
        "detail": "📚 Подробно"
    }
    
    lang_names = {
        "ru": "🇷🇺 Русский", "en": "🇬🇧 English", "kk": "🇰🇿 Қазақша",
        "tr": "🇹🇷 Türkçe", "uk": "🇺🇦 Українська", "fr": "🇫🇷 Français"
    }
    
    current_style = get_user_style(uid)
    
    # ✅ Запоминаем ID сообщения-приглашения
    context.user_data["invite_message_id"] = query.message.message_id
    print(f"📝 Запомнили ID приглашения: {query.message.message_id} для {uid}")
    
    # Кнопка для выхода из чата
    exit_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="exit_chat")]
    ])
    
    # Формируем текст в зависимости от режима
    if ai_mode == "fast":
        current_ai_lang = get_user_ai_lang(uid)
        text = (
            f"💬 Напиши сообщение.\n\n"
            f"Режим: {mode_names[ai_mode]}\n"
            f"Язык ответов: {lang_names.get(current_ai_lang, 'Русский')}\n"
            f"Стиль: {style_names.get(current_style, 'По шагам')}\n"
            f"Стоимость: {cost}⭐"
        )
    else:
        text = (
            f"💬 Напиши сообщение.\n\n"
            f"Режим: {mode_names[ai_mode]}\n"
            f"Стиль: {style_names.get(current_style, 'По шагам')}\n"
            f"Стоимость: {cost}⭐"
        )
    
    # Редактируем меню в приглашение (с кнопкой)
    await query.message.edit_text(text, reply_markup=exit_keyboard)
    
    context.user_data["in_chat_mode"] = True
    print(f"✅ Чат режим включен для {uid}")

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, text: str):
    
    # ===== ВЫХОД ИЗ ЧАТА =====
    # Проверяем на /cancel для обратной совместимости
    if text.lower().strip() == "/cancel":
        print(f"🚪 Выход из чата для {uid} (через /cancel)")
        context.user_data["in_chat_mode"] = False
        
        # Удаляем сообщение "/cancel"
        try:
            await update.message.delete()
        except:
            pass
        
        # Удаляем приглашение
        invite_msg_id = context.user_data.get("invite_message_id")
        if invite_msg_id:
            try:
                await context.bot.delete_message(chat_id=uid, message_id=invite_msg_id)
                print(f"🗑️ Удалено приглашение {invite_msg_id} для {uid}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить приглашение: {e}")
        
        await send_fresh_menu(context.bot, uid)
        return
    
    # ===== ОБЫЧНОЕ СООБЩЕНИЕ =====
    a = get_access(uid)
    ai_lang = get_user_ai_lang(uid)
    persona = get_user_persona(uid)
    style = get_user_style(uid)
    ai_mode = get_ai_mode(uid)
    cost = 0.3 if ai_mode == "fast" else 1.0
    
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        context.user_data["in_chat_mode"] = False
        return
    
    balance = get_balance(uid)
    if not a.get("is_free") and balance < cost:
        await update.message.reply_text(
            f"❌ Недостаточно звезд (нужно {cost}⭐).\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        context.user_data["in_chat_mode"] = False
        return
    
    # СОХРАНЯЕМ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ
    mem_add(uid, "user", text)
    
    typing_msg = await update.message.reply_text("⏳ Печатает...")
    
    try:
        history = mem_get(uid, limit=20)
        prompt_with_memory = build_memory_prompt(history, text)
        
        if ai_mode == "fast":
            reply = ask_groq(
                prompt_with_memory,
                lang=ai_lang,
                persona=persona,
                style=style
            )
        else:
            reply = ask_openai(
                prompt_with_memory,
                lang=ai_lang,
                persona=persona,
                style=style
            )
        
        if reply:
            await typing_msg.delete()
            
            mem_add(uid, "assistant", reply)
            
            # Кнопка для выхода под каждым ответом
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="exit_chat")]
            ])
            
            await context.bot.send_message(
                chat_id=uid,
                text=reply,
                reply_markup=keyboard
            )
            
            if not a.get("is_free"):
                spend_stars(uid, cost)
                add_stars_spent(uid, cost)
            
            increment_messages(uid)
            send_log_http(f"💬 Чат в боте ({ai_mode}): {uid} -> {text[:50]}...")
            
        else:
            await typing_msg.edit_text("❌ Ошибка получения ответа")
            
    except Exception as e:
        error_msg = str(e)
        if "insufficient_stars" in error_msg:
            await typing_msg.edit_text("❌ Недостаточно звезд. Купите в меню.")
        elif "network" in error_msg.lower():
            await typing_msg.edit_text("📡 Проблема с интернетом. Попробуйте позже.")
        else:
            await typing_msg.edit_text(f"❌ Ошибка: {error_msg[:100]}")
        
        context.user_data["in_chat_mode"] = False