# bot/handlers/tabs/ref.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.utils import set_last_menu, send_fresh_menu
from bot.locales import get_text
from api.db import db_connection

BOT_USERNAME = "@NextAIO_Bot"


async def show_ref(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """🎁 Рефералы"""
    
    stats = get_referral_stats(user_id)
    ref_link = f"https://t.me/{BOT_USERNAME[1:]}?start=ref_{user_id}"
    
    text = get_text(user_id, "ref_stats").format(
        count=stats['count'],
        bonus=stats['bonus']
    ) + f"\n\n🔗 {ref_link}"
    
    keyboard = [
        [InlineKeyboardButton("📤 Поделиться", switch_inline_query=f"🎁 Присоединяйся ко мне в NextAI! {ref_link}")],
        [InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")]
    ]
    
    try:
        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        set_last_menu(user_id, user_id, query.message.message_id)
        
    except Exception as e:
        print(f"⚠️ Ошибка при показе рефералов: {e}")
        await send_fresh_menu(context.bot, user_id)


def get_referral_stats(user_id: int) -> dict:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
        count = cur.fetchone()[0] or 0
        cur.execute("SELECT SUM(bonus_given) FROM referrals WHERE referrer_id = ?", (user_id,))
        bonus = cur.fetchone()[0] or 0
    return {"count": count, "bonus": bonus}