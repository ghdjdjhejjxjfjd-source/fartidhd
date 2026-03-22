# bot/handlers/tabs/style.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from telegram import Update
from telegram.ext import ContextTypes

from api import get_user_style, set_user_style, get_ai_mode, increment_groq_style, increment_openai_style
from bot.menu import style_settings_kb, tab_kb
from bot.utils import set_last_menu, send_fresh_menu
from bot.locales import get_text


async def show_style_settings(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """📝 Настройки стиля ответа"""
    ai_mode = get_ai_mode(user_id)
    mode_text = get_text(user_id, "ai_mode_fast") if ai_mode == "fast" else get_text(user_id, "ai_mode_quality")
    
    text = f"{get_text(user_id, 'style_settings')}\n\nРежим: {mode_text}"
    
    try:
        await query.message.edit_text(text, reply_markup=style_settings_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)


async def set_style(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, style: str):
    """Обработка смены стиля"""
    ai_mode = get_ai_mode(uid)
    
    if ai_mode == "fast":
        increment_groq_style(uid)
    else:
        increment_openai_style(uid)
    
    set_user_style(uid, style)
    
    style_names = {
        "short": get_text(uid, "style_short"),
        "steps": get_text(uid, "style_steps"),
        "detail": get_text(uid, "style_detail")
    }
    
    await query.message.edit_text(
        get_text(uid, "style_changed").format(style=style_names.get(style, style)),
        reply_markup=tab_kb(uid)
    )