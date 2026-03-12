from telegram import Update
from telegram.ext import ContextTypes

from api import get_ai_mode, get_ai_mode_changes, mem_clear, set_ai_mode
from payments import get_balance
from bot.menu import (
    main_menu_for_user, tab_kb, stars_kb, mode_settings_kb,
    persona_settings_kb, lang_settings_kb, settings_kb,
    ai_mode_settings_kb, confirm_ai_mode_kb, TAB_TEXT
)
from bot.utils import edit_to_menu, send_fresh_menu, set_last_menu, update_user_menu
from bot.settings import handle_set_lang, handle_set_persona, handle_switch_mode
from bot.chat import inline_chat_start
from bot.image import inline_image_start
from .state import navigation_stack  # ← импорт из state.py
from .navigation import back_to_previous, back_to_menu, ignore
from .tabs.profile import show_profile
from .tabs.help import show_help
from .tabs.status import show_status
from .tabs.ref import show_ref
from .tabs.support import show_support
from .tabs.buy_stars import show_buy_stars, buy_stars_package

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
    
    # НАВИГАЦИЯ
    if data == "back_to_previous":
        await back_to_previous(update, context, query, uid)
        return
    
    if data == "back_to_menu":
        await back_to_menu(update, context, query, uid)
        return
    
    if data == "ignore":
        await ignore(update, context, query, uid)
        return
    
    # ВКЛАДКИ
    if data.startswith("tab:"):
        key = data.split("tab:", 1)[1].strip()
        
        current_tab = context.user_data.get('current_tab')
        parent_tabs = ['settings', 'profile', 'help', 'status', 'ref', 'support', 'buy_stars', 'balance']
        child_tabs = ['ai_mode_settings', 'mode_settings', 'persona_settings', 'lang_settings']
        
        if current_tab in parent_tabs and key in child_tabs:
            navigation_stack[uid] = current_tab
        
        context.user_data['current_tab'] = key
        await open_tab(context, query, uid, key)
        return
    
    # ПОКУПКА ЗВЕЗД
    if data.startswith("buy_stars:"):
        package_id = data.split("buy_stars:", 1)[1].strip()
        await buy_stars_package(update, context, query, uid, package_id)
        return
    
    # НАСТРОЙКИ
    if data.startswith("set_lang:"):
        lang = data.split("set_lang:", 1)[1].strip()
        await handle_set_lang(update, context, query, uid, lang)
        await open_tab(context, query, uid, "settings")
        return
    
    if data.startswith("set_persona:"):
        persona = data.split("set_persona:", 1)[1].strip()
        await handle_set_persona(update, context, query, uid, persona)
        await open_tab(context, query, uid, "settings")
        return
    
    # РЕЖИМ ИИ
    if data.startswith("confirm_ai_mode:"):
        new_mode = data.split("confirm_ai_mode:", 1)[1].strip()
        current_mode = get_ai_mode(uid) or "fast"
        
        mode_names = {"fast": "🚀 Быстрый", "quality": "💎 Качественный"}
        text = TAB_TEXT["confirm_ai_mode_change"].format(
            new_mode=mode_names.get(new_mode, new_mode),
            current_mode=mode_names.get(current_mode, current_mode)
        )
        
        try:
            await query.message.edit_text(text, reply_markup=confirm_ai_mode_kb(uid, new_mode))
            set_last_menu(uid, uid, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, uid)
        return
    
    if data.startswith("execute_ai_mode:"):
        new_mode = data.split("execute_ai_mode:", 1)[1].strip()
        
        changes_left = await get_ai_mode_changes(uid)
        if changes_left <= 0:
            await query.message.edit_text(
                "⛔ Лимит смены режима на сегодня исчерпан (8/8).\n"
                "Попробуйте завтра после 00:00.",
                reply_markup=tab_kb(uid)
            )
            return
        
        mem_clear(uid)
        print(f"🧹 Очищена память для пользователя {uid} при смене режима")
        
        set_ai_mode(uid, new_mode)
        
        mode_names = {"fast": "🚀 Быстрый", "quality": "💎 Качественный"}
        await query.message.edit_text(
            f"✅ Режим изменен на {mode_names.get(new_mode, new_mode)}\n\n"
            f"🧹 История чата очищена.\n"
            f"📊 Сегодня осталось смен режима: {changes_left - 1}/8\n\n"
            f"При следующем открытии Mini App начнёте с чистого листа.",
            reply_markup=tab_kb(uid)
        )
        
        await update_user_menu(context.bot, uid)
        return
    
    # ПЕРЕКЛЮЧЕНИЕ РЕЖИМА РАБОТЫ
    if data == "switch_to_miniapp":
        await handle_switch_mode(update, context, query, uid, "miniapp")
        await open_tab(context, query, uid, "settings")
        return
    
    if data == "switch_to_inline":
        await handle_switch_mode(update, context, query, uid, "inline")
        await open_tab(context, query, uid, "settings")
        return
    
    # ЧАТ И КАРТИНКИ
    if data == "inline_chat":
        await inline_chat_start(update, context)
        return
    
    if data == "inline_image":
        await inline_image_start(update, context)
        return
    
    await edit_to_menu(context, query, uid)


async def open_tab(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    """Открыть вкладку"""
    
    if tab_key == "profile":
        await show_profile(context, query, user_id)
    
    elif tab_key == "help":
        await show_help(context, query, user_id)
    
    elif tab_key == "status":
        await show_status(context, query, user_id)
    
    elif tab_key == "ref":
        await show_ref(context, query, user_id)
    
    elif tab_key == "support":
        await show_support(context, query, user_id)
    
    elif tab_key == "buy_stars":
        await show_buy_stars(context, query, user_id)
    
    elif tab_key == "settings":
        text = "⚙️ Настройки\n\nВыбери раздел:"
        try:
            await query.message.edit_text(text, reply_markup=settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "ai_mode_settings":
        changes_left = await get_ai_mode_changes(user_id)
        text = TAB_TEXT["ai_mode_settings"].format(changes_left=changes_left)
        try:
            await query.message.edit_text(text, reply_markup=ai_mode_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "mode_settings":
        text = TAB_TEXT.get(tab_key, "🔄 Режим работы\n\nВыбери как пользоваться ботом:")
        try:
            await query.message.edit_text(text, reply_markup=mode_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "persona_settings":
        text = TAB_TEXT.get(tab_key, "🎭 Характер ИИ\n\nВыбери как ИИ будет отвечать:")
        try:
            await query.message.edit_text(text, reply_markup=persona_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "lang_settings":
        text = TAB_TEXT.get(tab_key, "🌐 Язык\n\nВыбери язык интерфейса:")
        try:
            await query.message.edit_text(text, reply_markup=lang_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "balance":
        balance = get_balance(user_id)
        text = f"⭐ Ваш баланс: {balance} звезд"
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    else:
        text = TAB_TEXT.get(tab_key, "Раздел в разработке.")
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)