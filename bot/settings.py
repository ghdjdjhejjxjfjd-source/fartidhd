from telegram import Update
from telegram.ext import ContextTypes
from api import set_user_lang, set_user_persona, set_use_mini_app, get_ai_mode
from .utils import update_user_menu
from .menu import tab_kb

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
    ai_mode = get_ai_mode(uid)
    
    # Если качественный режим - блокируем смену характера
    if ai_mode == "quality":
        await query.message.edit_text(
            "❌ В качественном режиме (OpenAI) характер недоступен.\n"
            "Переключитесь на быстрый режим (Groq) чтобы изменить характер.",
            reply_markup=tab_kb(uid)
        )
        return
    
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
    await update_user_menu(context.bot, uid)

async def handle_switch_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, mode: str):
    """Обработка переключения режима работы (Mini App / Встроенный)"""
    use_mini_app = (mode == "miniapp")
    set_use_mini_app(uid, use_mini_app)
    
    mode_text = "Mini App" if use_mini_app else "встроенный"
    await query.message.edit_text(
        f"✅ Режим работы переключен на {mode_text}!",
        reply_markup=tab_kb(uid)
    )
    await update_user_menu(context.bot, uid)