# bot/chat.py
from telegram import Update
from telegram.ext import ContextTypes

from api import get_access, get_user_persona, get_user_lang, get_ai_mode, increment_messages, add_stars_spent
from payments import get_balance, spend_stars
from groq_client import ask_groq
from openai_client import ask_openai
from .config import send_log_http

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
    
    mode_names = {"fast": "🚀 Быстрый (Groq)", "quality": "💎 Качественный (OpenAI)"}
    await query.message.reply_text(
        f"💬 Напиши сообщение для ИИ.\n"
        f"Режим: {mode_names.get(ai_mode, 'Быстрый')}\n"
        f"Стоимость: {cost}⭐ за сообщение\n\n"
        f"Отправь текст, и я отвечу.\n"
        f"Для отмены напиши /cancel"
    )
    
    context.user_data["in_chat_mode"] = True

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, text: str):
    a = get_access(uid)
    lang = get_user_lang(uid)
    persona = get_user_persona(uid)
    ai_mode = get_ai_mode(uid)
    cost = 0.3 if ai_mode == "fast" else 1.0
    
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    balance = get_balance(uid)
    if not a.get("is_free") and balance < cost:
        await update.message.reply_text(
            f"❌ Недостаточно звезд (нужно {cost}⭐).\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await update.message.reply_text("🤔 Думаю...")
    
    try:
        # Выбираем AI в зависимости от режима
        if ai_mode == "fast":
            # Groq - можно использовать характер
            reply = ask_groq(
                user_text=text,
                lang=lang,
                persona=persona,
                style="steps"  # или можно тоже из настроек
            )
        else:
            # OpenAI - характер не используется
            reply = ask_openai(
                user_text=text,
                lang=lang,
                style="steps"
            )
        
        if reply:
            await update.message.reply_text(reply)
            
            # Списываем звезды
            if not a.get("is_free"):
                spend_stars(uid, cost)
                add_stars_spent(uid, cost)
            
            increment_messages(uid)
            send_log_http(f"💬 Чат в боте ({ai_mode}): {uid} -> {text[:50]}...")
        else:
            await update.message.reply_text("❌ Ошибка получения ответа")
            
    except Exception as e:
        error_msg = str(e)
        if "insufficient_stars" in error_msg:
            await update.message.reply_text("❌ Недостаточно звезд. Купите в меню.")
        elif "network" in error_msg.lower():
            await update.message.reply_text("📡 Проблема с интернетом. Попробуйте позже.")
        else:
            await update.message.reply_text(f"❌ Ошибка: {error_msg[:100]}")