from telegram import Update
from telegram.ext import ContextTypes

from bot.utils import send_fresh_menu
from bot.config import build_start_log, send_log_http

navigation_stack = {}  # временно тут, потом перенесем

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    # Очищаем навигацию при старте
    if uid in navigation_stack:
        del navigation_stack[uid]
    
    await send_fresh_menu(context.bot, uid)