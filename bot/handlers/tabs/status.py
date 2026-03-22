# bot/handlers/tabs/status.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from telegram import Update
from telegram.ext import ContextTypes

from bot.menu import tab_kb
from bot.utils import set_last_menu, send_fresh_menu
from bot.locales import get_text


async def show_status(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """📌 Статус"""
    text = get_text(user_id, "status")
    
    try:
        await query.message.edit_text(text, reply_markup=tab_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)