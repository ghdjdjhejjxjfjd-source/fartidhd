# bot/handlers/tabs/ai_lang.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from telegram import Update
from telegram.ext import ContextTypes

from api import get_user_ai_lang, set_user_ai_lang
from bot.menu import ai_lang_settings_kb, tab_kb
from bot.utils import set_last_menu, send_fresh_menu
from bot.locales import get_text


async def show_ai_lang_settings(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """🌐 Настройки языка ответов ИИ"""
    text = get_text(user_id, "ai_lang_settings")
    
    try:
        await query.message.edit_text(text, reply_markup=ai_lang_settings_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)


async def set_ai_lang(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, lang: str):
    """Обработка смены языка ответов ИИ"""
    set_user_ai_lang(uid, lang)
    
    lang_names = {
        "ru": get_text(uid, "lang_ru"),
        "en": get_text(uid, "lang_en"),
        "kk": get_text(uid, "lang_kk"),
        "tr": get_text(uid, "lang_tr"),
        "uk": get_text(uid, "lang_uk"),
        "fr": get_text(uid, "lang_fr")
    }
    
    await query.message.edit_text(
        get_text(uid, "ai_lang_changed").format(lang=lang_names.get(lang, lang)),
        reply_markup=tab_kb(uid)
    )