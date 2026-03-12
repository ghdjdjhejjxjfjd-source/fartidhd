from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from api import (
    get_access, get_user_persona, get_user_lang, 
    get_use_mini_app, get_ai_mode, get_ai_mode_changes
)
from payments import get_balance
from bot.menu import tab_kb, TAB_TEXT
from bot.utils import set_last_menu, send_fresh_menu


async def show_profile(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Показать профиль пользователя"""
    a = get_access(user_id)
    balance = get_balance(user_id)
    persona = get_user_persona(user_id)
    lang = get_user_lang(user_id)
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    changes_left = await get_ai_mode_changes(user_id)
    
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
    
    ai_mode_names = {
        "fast": "🚀 Быстрый (0.3 ⭐)",
        "quality": "💎 Качественный (1 ⭐)"
    }
    
    registered = "неизвестно"
    if a.get("registered_at"):
        try:
            reg_date = datetime.strptime(a["registered_at"], "%Y-%m-%d %H:%M:%S")
            registered = reg_date.strftime("%d.%m.%Y")
        except:
            registered = a["registered_at"][:10]
    
    text = TAB_TEXT["profile"].format(
        user_id=user_id,
        registered=registered,
        messages=a.get("total_messages", 0),
        images=a.get("total_images", 0),
        spent=a.get("total_stars_spent", 0),
        balance=balance,
        persona=persona_names.get(persona, persona),
        lang=lang_names.get(lang, lang),
        mode="📱 Mini App" if use_mini_app else "💬 Встроенный",
        ai_mode=f"{ai_mode_names.get(ai_mode, ai_mode)} (осталось смен: {changes_left}/8)",
        free="✅ Да" if a.get("is_free") else "❌ Нет",
        blocked="✅ Нет" if not a.get("is_blocked") else "❌ Да"
    )
    
    try:
        await query.message.edit_text(text, reply_markup=tab_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)