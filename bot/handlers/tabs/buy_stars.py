from telegram import Update
from telegram.ext import ContextTypes

from payments import get_package
from bot.menu import tab_kb, stars_kb, TAB_TEXT
from bot.utils import set_last_menu, send_fresh_menu

async def show_buy_stars(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """⭐ Купить звезды - показать список пакетов"""
    text = TAB_TEXT.get("buy_stars", "⭐ Пакеты звезд\n\nВыберите пакет для пополнения:")
    
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
        
        await query.message.edit_text(
            f"✅ Вы выбрали пакет {package['name']}\n"
            f"⭐ {stars} звезд за ${price}\n\n"
            f"Оплата через Telegram Stars будет доступна позже.",
            reply_markup=tab_kb(uid)
        )
    else:
        await query.message.edit_text("❌ Пакет не найден", reply_markup=tab_kb(uid))