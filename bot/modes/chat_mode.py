# bot/modes/chat_mode.py
from telegram import Update
from telegram.ext import ContextTypes

from api import get_access, get_user_persona, get_user_lang, increment_messages, add_stars_spent
from payments import get_balance, spend_stars
from bot.config import send_log_http
from groq_client import ask_groq

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск режима чата"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < 1:
        await query.message.reply_text(
            "❌ Недостаточно звезд.\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await query.message.reply_text(
        "💬 Напиши сообщение для ИИ.\n"
        "Отправь текст, и я отвечу.\n\n"
        "Для отмены напиши /cancel"
    )
    
    context.user_data["mode"] = "chat"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обработка сообщения в чате"""
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    lang = get_user_lang(uid)
    persona = get_user_persona(uid)
    
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    balance = get_balance(uid)
    if not a.get("is_free") and balance < 1:
        await update.message.reply_text(
            "❌ Недостаточно звезд.\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await update.message.reply_text("🤔 Думаю...")
    
    try:
        # Используем Groq
        reply = ask_groq(text, lang=lang, persona=persona)
        
        if reply:
            await update.message.reply_text(reply)
            
            # Списываем звезды
            if not a.get("is_free"):
                spend_stars(uid, 1)
                add_stars_spent(uid, 1)
            
            increment_messages(uid)
            send_log_http(f"💬 Чат: {uid} -> {text[:50]}...")
        else:
            await update.message.reply_text("❌ Ошибка получения ответа")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")