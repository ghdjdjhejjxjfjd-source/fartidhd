from telegram import Update
from telegram.ext import ContextTypes

from bot.utils import edit_to_menu
from .router import navigation_stack  # импортируем стек из router.py

async def back_to_previous(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int):
    """Вернуться на предыдущий уровень"""
    if uid in navigation_stack:
        prev_tab = navigation_stack[uid]
        del navigation_stack[uid]
        
        # Импортируем open_tab внутри чтобы избежать цикла
        from .router import open_tab
        await open_tab(context, query, uid, prev_tab)
    else:
        await edit_to_menu(context, query, uid)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int):
    """Принудительно в главное меню"""
    if uid in navigation_stack:
        del navigation_stack[uid]
    await edit_to_menu(context, query, uid)

async def ignore(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int):
    """Ничего не делать"""
    await query.answer()