from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from api import get_access
from payments import get_balance
from bot.ui.keyboards import back_button

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    query = update.callback_query
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    registered = "неизвестно"
    if a.get("registered_at"):
        try:
            reg_date = datetime.strptime(a["registered_at"], "%Y-%m-%d %H:%M:%S")
            registered = reg_date.strftime("%d.%m.%Y")
        except:
            registered = a["registered_at"][:10]
    
    persona_names = {
        "friendly": "😊 Общительный",
        "fun": "😂 Весёлый",
        "smart": "🧐 Умный",
        "strict": "😐 Строгий"
    }
    
    lang_names = {
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
        "kk": "🇰🇿 Қазақша",
        "tr": "🇹🇷 Türkçe",
        "uk": "🇺🇦 Українська",
        "fr": "🇫🇷 Français"
    }
    
    text = (
        f"👤 **ПРОФИЛЬ**\n\n"
        f"🆔 ID: `{uid}`\n"
        f"📅 В боте с: {registered}\n\n"
        f"📊 **СТАТИСТИКА**\n"
        f"💬 Сообщений: {a.get('total_messages', 0)}\n"
        f"🖼 Картинок: {a.get('total_images', 0)}\n"
        f"⭐ Потрачено звезд: {a.get('total_stars_spent', 0)}\n"
        f"💰 Баланс: {balance} ⭐\n\n"
        f"⚙️ **ТЕКУЩЕЕ**\n"
        f"🎭 Характер: {persona_names.get(a.get('persona'), 'friendly')}\n"
        f"🌐 Язык: {lang_names.get(a.get('lang'), 'ru')}\n"
        f"💳 FREE: {'✅ Да' if a.get('is_free') else '❌ Нет'}\n"
        f"⛔ Блок: {'✅ Нет' if not a.get('is_blocked') else '❌ Да'}"
    )
    
    await query.message.edit_text(text, reply_markup=back_button(), parse_mode="Markdown")