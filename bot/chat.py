from telegram import Update
from telegram.ext import ContextTypes

from api import get_access, get_user_persona, get_user_lang
from payments import get_balance, spend_stars
from groq_client import ask_groq
from .config import send_log_http


async def inline_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало чата в Telegram"""
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
    
    # Запоминаем что пользователь в режиме чата
    context.user_data["in_chat_mode"] = True


async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, text: str):
    """Обработка сообщения для чата"""
    a = get_access(uid)
    lang = get_user_lang(uid)
    persona = get_user_persona(uid)
    
    await update.message.reply_text("🤔 Думаю...")
    
    try:
        reply = ask_groq(text, lang=lang, persona=persona)
        await update.message.reply_text(reply)
        
        # Списываем звезду если не FREE
        if not a.get("is_free"):
            spend_stars(uid, 1)
            
        # Логируем
        send_log_http(f"💬 Чат: {uid} -> {text[:50]}...")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")