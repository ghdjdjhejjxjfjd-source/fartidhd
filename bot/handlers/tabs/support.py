from telegram import Update
from telegram.ext import ContextTypes

from bot.menu import tab_kb, TAB_TEXT
from bot.utils import set_last_menu, send_fresh_menu

async def show_support(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """💬 Поддержка"""
    text = TAB_TEXT.get("support", "💬 Поддержка\n\nРаздел в разработке.")
    
    try:
        await query.message.edit_text(text, reply_markup=tab_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)