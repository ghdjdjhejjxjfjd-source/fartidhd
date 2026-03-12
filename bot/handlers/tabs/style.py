from telegram import Update
from telegram.ext import ContextTypes

from api import get_user_style, set_user_style, get_ai_mode
from bot.menu import style_settings_kb, tab_kb
from bot.utils import set_last_menu, send_fresh_menu

async def show_style_settings(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """📝 Настройки стиля ответа"""
    ai_mode = get_ai_mode(user_id)
    mode_text = "🚀 Быстрый" if ai_mode == "fast" else "💎 Качественный"
    
    text = f"📝 Стиль ответа\n\nРежим: {mode_text}\n\nВыбери как ИИ будет отвечать:"
    
    try:
        await query.message.edit_text(text, reply_markup=style_settings_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)

async def set_style(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, style: str):
    """Обработка смены стиля"""
    set_user_style(uid, style)
    
    style_names = {
        "short": "📏 Коротко",
        "steps": "📋 По шагам",
        "detail": "📚 Подробно"
    }
    
    await query.message.edit_text(
        f"✅ Стиль изменен на: {style_names.get(style, style)}",
        reply_markup=tab_kb(uid)
    )