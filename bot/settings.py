# bot/settings.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from telegram import Update
from telegram.ext import ContextTypes
from api import set_user_lang, set_user_persona, set_use_mini_app, get_ai_mode, increment_groq_persona
from .utils import update_user_menu
from .menu import tab_kb
from .locales import get_text


async def handle_set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, lang: str):
    """Обработка смены языка"""
    set_user_lang(uid, lang)
    
    await query.message.edit_text(
        get_text(uid, "lang_changed"),
        reply_markup=tab_kb(uid)
    )
    await update_user_menu(context.bot, uid)


async def handle_set_persona(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, persona: str):
    """Обработка смены характера"""
    ai_mode = get_ai_mode(uid)
    
    if ai_mode == "quality":
        await query.message.edit_text(
            get_text(uid, "persona_locked"),
            reply_markup=tab_kb(uid)
        )
        return
    
    increment_groq_persona(uid)
    set_user_persona(uid, persona)
    
    persona_names = {
        "friendly": get_text(uid, "persona_friendly"),
        "fun": get_text(uid, "persona_fun"),
        "smart": get_text(uid, "persona_smart"),
        "strict": get_text(uid, "persona_strict")
    }
    
    await query.message.edit_text(
        get_text(uid, "persona_changed").format(persona=persona_names.get(persona, persona)),
        reply_markup=tab_kb(uid)
    )


async def handle_switch_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, mode: str):
    """Обработка переключения режима работы"""
    use_mini_app = (mode == "miniapp")
    set_use_mini_app(uid, use_mini_app)
    
    mode_text = get_text(uid, "mode_miniapp") if use_mini_app else get_text(uid, "mode_inline")
    
    await query.message.edit_text(
        get_text(uid, "mode_changed").format(mode=mode_text),
        reply_markup=tab_kb(uid)
    )
    await update_user_menu(context.bot, uid)