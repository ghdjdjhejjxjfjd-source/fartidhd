from telegram import Update
from telegram.ext import ContextTypes

from api import set_user_lang, set_user_persona, set_use_mini_app, set_ai_mode
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
    """Обработка переключения режима работы (Mini App / Встроенный)"""
    use_mini_app = (mode == "miniapp")
    set_use_mini_app(uid, use_mini_app)
    
    mode_text = "Mini App" if use_mini_app else "встроенный"
    await query.message.edit_text(
        f"✅ Режим работы переключен на {mode_text}!",
        reply_markup=tab_kb(uid)
    )
    await update_user_menu(context.bot, uid)


# =========================
# НОВАЯ ФУНКЦИЯ ДЛЯ РЕЖИМА ИИ
# =========================
async def handle_set_ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, query, uid: int, ai_mode: str):
    """Обработка смены режима ИИ (Быстрый / Качественный)"""
    set_ai_mode(uid, ai_mode)
    
    mode_names = {
        "fast": "🚀 Быстрый (0.3 ⭐)",
        "quality": "💎 Качественный (1 ⭐)"
    }
    
    mode_text = mode_names.get(ai_mode, ai_mode)
    
    # Показываем цены в зависимости от выбора
    price_info = ""
    if ai_mode == "fast":
        price_info = "\n\nТеперь каждый запрос будет стоить 0.3 ⭐"
    else:
        price_info = "\n\nТеперь каждый запрос будет стоить 1 ⭐"
    
    await query.message.edit_text(
        f"✅ Режим ИИ изменен на: {mode_text}{price_info}",
        reply_markup=tab_kb(uid)
    )
    # Не обновляем меню сразу, так как режим ИИ не влияет на главное меню


def tab_kb(user_id: int):
    from .menu import tab_kb as menu_tab_kb
    return menu_tab_kb(user_id)