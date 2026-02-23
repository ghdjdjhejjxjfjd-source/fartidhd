from telegram import Update
from telegram.ext import ContextTypes

from api import (
    get_access, get_last_menu, set_last_menu, clear_last_menu,
    get_use_mini_app, get_user_persona, get_user_lang
)
from payments import get_balance, get_package

from .config import send_log_http, build_start_log, MINIAPP_URL
from .menu import main_menu_for_user, tab_kb, stars_kb, mode_settings_kb, persona_settings_kb, lang_settings_kb
from .settings import handle_set_lang, handle_set_persona, handle_switch_mode
from .chat import inline_chat_start, handle_chat_message
from .image import inline_image_start, handle_image_generation

import re

# =========================
# УПРАВЛЕНИЕ МЕНЮ
# =========================
async def delete_prev_menu(bot, user_id: int):
    chat_id, msg_id = get_last_menu(user_id)
    if not chat_id or not msg_id:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        print(f"🗑️ Удалено старое меню для {user_id}")
    except Exception:
        pass
    clear_last_menu(user_id)


async def send_fresh_menu(bot, user_id: int, text: str = None):
    await delete_prev_menu(bot, user_id)
    
    if text is None:
        text = "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇"
    
    m = await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=main_menu_for_user(user_id),
    )
    set_last_menu(user_id, user_id, m.message_id)


async def update_user_menu(bot, user_id: int):
    await send_fresh_menu(bot, user_id)


async def send_block_notice(bot, user_id: int):
    await delete_prev_menu(bot, user_id)
    await bot.send_message(chat_id=user_id, text="⛔ Доступ заблокирован.")


async def edit_to_menu(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    try:
        await query.message.edit_text(
            "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
            reply_markup=main_menu_for_user(user_id)
        )
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)


async def edit_to_tab(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    from .menu import TAB_TEXT
    text = TAB_TEXT.get(tab_key, "Раздел в разработке.")
    
    if tab_key == "balance":
        balance = get_balance(user_id)
        text = f"⭐ Ваш баланс: {balance} звезд"
    
    if tab_key == "buy_stars":
        reply_markup = stars_kb(user_id)
    elif tab_key == "mode_settings":
        reply_markup = mode_settings_kb(user_id)
    elif tab_key == "persona_settings":
        reply_markup = persona_settings_kb(user_id)
    elif tab_key == "lang_settings":
        reply_markup = lang_settings_kb(user_id)
    else:
        reply_markup = tab_kb(user_id)
    
    try:
        await query.message.edit_text(text, reply_markup=reply_markup)
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)


# =========================
# ОСНОВНЫЕ ОБРАБОТЧИКИ
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    await send_fresh_menu(context.bot, uid)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = (query.data or "").strip()
    
    try:
        await query.answer()
    except Exception:
        pass
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    if data == "ignore":
        return
    
    if data == "back_to_menu":
        await edit_to_menu(context, query, uid)
        return
    
    if data.startswith("tab:"):
        key = data.split("tab:", 1)[1].strip()
        await edit_to_tab(context, query, uid, key)
        return
    
    if data.startswith("buy_stars:"):
        package_id = data.split("buy_stars:", 1)[1].strip()
        package = get_package(package_id)
        
        if package:
            stars = package["stars"]
            price = package["price_usd"]
            await query.message.edit_text(
                f"✅ Вы выбрали пакет {package['name']}\n"
                f"⭐ {stars} звезд за ${price}\n\n"
                f"Оплата через Telegram Stars будет доступна позже.",
                reply_markup=tab_kb(uid)
            )
        else:
            await query.message.edit_text("❌ Пакет не найден", reply_markup=tab_kb(uid))
        return
    
    if data.startswith("set_lang:"):
        lang = data.split("set_lang:", 1)[1].strip()
        await handle_set_lang(update, context, query, uid, lang)
        return
    
    if data.startswith("set_persona:"):
        persona = data.split("set_persona:", 1)[1].strip()
        await handle_set_persona(update, context, query, uid, persona)
        return
    
    if data == "switch_to_miniapp":
        await handle_switch_mode(update, context, query, uid, "miniapp")
        return
    
    if data == "switch_to_inline":
        await handle_switch_mode(update, context, query, uid, "inline")
        return
    
    if data == "inline_chat":
        await inline_chat_start(update, context)
        return
    
    if data == "inline_image":
        await inline_image_start(update, context)
        return
    
    await edit_to_menu(context, query, uid)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    uid = user.id
    
    if not context.user_data.get("in_chat_mode") and not context.user_data.get("in_image_mode"):
        return
    
    a = get_access(uid)
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        context.user_data.clear()
        return
    
    text = update.message.text
    
    if context.user_data.get("in_chat_mode"):
        await handle_chat_message(update, context, uid, text)
        context.user_data["in_chat_mode"] = False
        
    elif context.user_data.get("in_image_mode"):
        await handle_image_generation(update, context, uid, text)
        context.user_data["in_image_mode"] = False