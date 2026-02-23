from telegram import Update
from telegram.ext import ContextTypes

from api import set_user_lang, set_user_persona, set_use_mini_app
from .utils import update_user_menu


async def handle_set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, lang: str):
    """Обработка смены языка"""
    set_user_lang(uid, lang)
    
    await query.message.edit_text(
        f"✅ Язык изменен",
        reply_markup=tab_kb(uid)
    )
    await update_user_menu(context.bot, uid)


async def handle_set_persona(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, persona: str):
    """Обработка смены характера"""
    set_user_persona(uid, persona)
    
    persona_names = {
        "friendly": "😊 Общительный",
        "fun": "😂 Весёлый",
        "smart": "🧐 Умный",
        "strict": "😐 Строгий"
    }
    
    await query.message.edit_text(
        f"✅ Характер изменен на: {persona_names.get(persona, persona)}",
        reply_markup=tab_kb(uid)
    )


async def handle_switch_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, mode: str):
    """Обработка переключения режима"""
    use_mini_app = (mode == "miniapp")
    set_use_mini_app(uid, use_mini_app)
    
    mode_text = "Mini App" if use_mini_app else "встроенный"
    await query.message.edit_text(
        f"✅ Режим переключен на {mode_text}!",
        reply_markup=tab_kb(uid)
    )
    await update_user_menu(context.bot, uid)


def tab_kb(user_id: int):
    from .menu import tab_kb as menu_tab_kb
    return menu_tab_kb(user_id)