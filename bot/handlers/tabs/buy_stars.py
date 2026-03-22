from telegram import Update
from telegram.ext import ContextTypes

from payments import get_package
from bot.menu import tab_kb, stars_kb
from bot.utils import set_last_menu, send_fresh_menu
from bot.locales import get_text, get_button_text

async def show_buy_stars(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """⭐ Купить звезды - показать список пакетов"""
    text = get_text(user_id, "buy_stars")
    
    try:
        await query.message.edit_text(text, reply_markup=stars_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)

async def buy_stars_package(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, package_id: str):
    """Обработка выбора конкретного пакета"""
    package = get_package(package_id)
    
    if package:
        stars = package["stars"]
        price = package["price_usd"]
        
        text = get_text(uid, "package_selected").format(
            name=package['name'],
            stars=stars,
            price=price
        )
        
        await query.message.edit_text(
            text=text,
            reply_markup=tab_kb(uid)
        )
    else:
        await query.message.edit_text(
            get_text(uid, "package_not_found"),
            reply_markup=tab_kb(uid)
        )