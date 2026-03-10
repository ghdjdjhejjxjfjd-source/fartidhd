# bot/modes/chat_mode.py
from telegram import Update
from telegram.ext import ContextTypes
from api import get_access, get_user_persona, get_user_lang, increment_messages, add_stars_spent
from payments import get_balance, spend_stars
from groq_client import ask_groq

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await query.message.reply_text("❌ Недостаточно звезд. Купи в меню.")
        return
    
    await query.message.reply_text("💬 Напиши сообщение. /cancel для отмены")
    context.user_data["mode"] = "chat"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
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
        await update.message.reply_text("❌ Недостаточно звезд.")
        return
    
    await update.message.reply_text("🤔 Думаю...")
    
    try:
        reply = ask_groq(text, lang=lang, persona=persona)
        if reply:
            await update.message.reply_text(reply)
            if not a.get("is_free"):
                spend_stars(uid, 1)
                add_stars_spent(uid, 1)
            increment_messages(uid)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")