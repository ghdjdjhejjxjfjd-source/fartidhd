import os
import time
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update
from bot.handlers import start, on_button, handle_message, handle_photo
from bot_admin import *

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()

async def post_init(app: Application):
    await app.bot.set_my_commands([("start", "🚀 Запустить")])

def start_bot():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("free", cmd_free))
    app.add_handler(CommandHandler("paid", cmd_paid))
    app.add_handler(CommandHandler("block", cmd_block))
    app.add_handler(CommandHandler("unblock", cmd_unblock))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("addstars", cmd_addstars))
    app.add_handler(CommandHandler("balance", cmd_balance))
    
    print("🤖 Бот запущен")
    app.run_polling()