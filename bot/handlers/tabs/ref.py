from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.menu import tab_kb, TAB_TEXT
from bot.utils import set_last_menu, send_fresh_menu
from api.db import db_connection
from payments import get_balance

BOT_USERNAME = "@NextAIO_Bot"  # ← замени на свой юзернейм

async def show_ref(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """🎁 Рефералы"""
    
    # Получаем статистику рефералов
    stats = get_referral_stats(user_id)
    
    # Генерируем реферальную ссылку
    ref_link = f"https://t.me/{BOT_USERNAME[1:]}?start=ref_{user_id}"
    
    text = (
        f"🎁 **РЕФЕРАЛЫ**\n\n"
        f"📊 **Статистика**\n"
        f"👥 Приглашено друзей: {stats['count']}\n"
        f"⭐ Заработано звезд: {stats['bonus']}\n\n"
        f"🔗 **Твоя реферальная ссылка:**\n"
        f"{ref_link}\n\n"
        f"👇 Нажми на ссылку чтобы скопировать"
    )
    
    # Клавиатура только с кнопкой поделиться и назад
    keyboard = [
        [InlineKeyboardButton("📤 Поделиться", switch_inline_query=f"🎁 Присоединяйся ко мне в NextAI! {ref_link}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")]
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