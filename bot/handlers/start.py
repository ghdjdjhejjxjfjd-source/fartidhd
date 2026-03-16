# bot/handlers/start.py
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils import send_fresh_menu
from bot.config import build_start_log, send_log_http

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    print(f"🚀 /start от пользователя {uid}")
    
    # Всегда отправляем свежее меню (старое удалится автоматически)
    await send_fresh_menu(context.bot, uid)