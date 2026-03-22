from telegram import Update
from telegram.ext import ContextTypes

from api import get_user_ai_lang, set_user_ai_lang
from bot.menu import ai_lang_settings_kb, tab_kb
from bot.utils import set_last_menu, send_fresh_menu

async def show_ai_lang_settings(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """🌐 Настройки языка ответов ИИ"""
    text = "🌐 Язык ответов ИИ\n\nВыбери на каком языке будет отвечать ИИ:"
    
    try:
        await query.message.edit_text(text, reply_markup=ai_lang_settings_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)

async def set_ai_lang(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, lang: str):
    """Обработка смены языка ответов ИИ"""
    set_user_ai_lang(uid, lang)
    
    lang_names = {
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
        "kk": "🇰🇿 Қазақша",
        "tr": "🇹🇷 Türkçe",
        "uk": "🇺🇦 Українська",
        "fr": "🇫🇷 Français"
    }
    
    await query.message.edit_text(
        f"✅ Язык ответов ИИ изменен на: {lang_names.get(lang, lang)}",
        reply_markup=tab_kb(uid)
    )