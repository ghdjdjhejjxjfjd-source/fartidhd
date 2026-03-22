from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.menu import tab_kb
from bot.utils import set_last_menu, send_fresh_menu
from bot.locales import get_text, get_button_text
from api.db import db_connection
from payments import get_balance

BOT_USERNAME = "@NextAIO_Bot"  # ← замени на свой юзернейм

async def show_ref(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """🎁 Рефералы"""
    
    # Получаем статистику рефералов
    stats = get_referral_stats(user_id)
    
    # Генерируем реферальную ссылку
    ref_link = f"https://t.me/{BOT_USERNAME[1:]}?start=ref_{user_id}"
    
    # Текст с локализацией
    text = get_text(user_id, "ref_template").format(
        count=stats['count'],
        bonus=stats['bonus'],
        ref_link=ref_link
    )
    
    # Клавиатура с кнопкой поделиться и назад
    keyboard = [
        [InlineKeyboardButton(get_button_text(user_id, "share"), switch_inline_query=get_text(user_id, "share_text").format(ref_link=ref_link))],
        [InlineKeyboardButton(get_button_text(user_id, "back"), callback_data="back_to_previous")]
    ]
    
    try:
        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Рефералы показаны для {user_id}")
        
    except Exception as e:
        print(f"⚠️ Ошибка при показе рефералов: {e}")
        await send_fresh_menu(context.bot, user_id)

def get_referral_stats(user_id: int) -> dict:
    """Получить статистику рефералов пользователя"""
    with db_connection() as conn:
        cur = conn.cursor()
        
        # Количество приглашенных
        cur.execute(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?",
            (user_id,)
        )
        count = cur.fetchone()[0] or 0
        
        # Сумма полученных бонусов
        cur.execute(
            "SELECT SUM(bonus_given) FROM referrals WHERE referrer_id = ?",
            (user_id,)
        )
        bonus = cur.fetchone()[0] or 0
    
    return {
        "count": count,
        "bonus": bonus
    }