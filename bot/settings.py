from telegram import Update
from telegram.ext import ContextTypes
from api import set_user_lang, set_user_persona, set_use_mini_app, get_ai_mode, increment_groq_persona
from .utils import update_user_menu
from .menu import tab_kb
from .locales import get_text, get_button_text, get_persona_name, get_work_mode_name

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
    
    # Если качественный режим - блокируем смену характера
    if ai_mode == "quality":
        await query.message.edit_text(
            get_text(uid, "persona_not_available_quality"),
            reply_markup=tab_kb(uid)
        )
        return
    
    # Увеличиваем счетчик лимита
    increment_groq_persona(uid)
    
    set_user_persona(uid, persona)
    
    await query.message.edit_text(
        get_text(uid, "persona_changed").format(persona=get_persona_name(uid, persona)),
        reply_markup=tab_kb(uid)
    )
    # Убираем update_user_menu, чтобы не уходить в меню

async def handle_switch_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, mode: str):
    """Обработка переключения режима работы (Mini App / Встроенный)"""
    use_mini_app = (mode == "miniapp")
    set_use_mini_app(uid, use_mini_app)
    
    mode_text = get_work_mode_name(uid, "miniapp" if use_mini_app else "inline")
    await query.message.edit_text(
        get_text(uid, "mode_changed_work").format(mode=mode_text),
        reply_markup=tab_kb(uid)
    )
    await update_user_menu(context.bot, uid)