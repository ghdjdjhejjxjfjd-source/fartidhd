# bot/handlers/router.py - ПОЛНАЯ ВЕРСИЯ С ЛОКАЛИЗАЦИЕЙ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from api import get_ai_mode, get_ai_mode_changes, mem_clear, set_ai_mode, get_user_limits
from payments import get_balance
from bot.menu import (
    main_menu_for_user, tab_kb, stars_kb, mode_settings_kb,
    persona_settings_kb, lang_settings_kb, settings_kb, ai_lang_settings_kb,
    ai_mode_settings_kb, confirm_ai_mode_kb, style_settings_kb
)
from bot.locales import get_text
from bot.utils import edit_to_menu, send_fresh_menu, set_last_menu, update_user_menu, edit_to_tab
from bot.settings import handle_set_lang, handle_set_persona, handle_switch_mode
from bot.chat import inline_chat_start, exit_chat
from bot.image import inline_image_start
from bot.support import support_start, forward_to_support
from bot.helpers import format_balance
from .state import navigation_stack
from .navigation import back_to_previous, back_to_menu, ignore
from .tabs.profile import show_profile
from .tabs.help import show_help
from .tabs.status import show_status
from .tabs.ref import show_ref
from .tabs.support import show_support
from .tabs.buy_stars import show_buy_stars, buy_stars_package
from .tabs.style import show_style_settings, set_style
from .tabs.ai_lang import show_ai_lang_settings, set_ai_lang

BOT_USERNAME = "@NextAIO_Bot"


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
    
    # ===== КОПИРОВАНИЕ РЕФЕРАЛЬНОЙ ССЫЛКИ =====
    if data.startswith("copy_ref_"):
        user_id = int(data.split("_")[2])
        ref_link = context.user_data.get(f"ref_link_{user_id}")
        
        if ref_link:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📋 Твоя реферальная ссылка:\n`{ref_link}`",
                parse_mode="Markdown"
            )
            await query.answer("✅ Ссылка отправлена в чат")
        else:
            await query.answer("❌ Ошибка: ссылка не найдена")
        return
    
    # ===== ВЫХОД ИЗ ЧАТА =====
    if data == "exit_chat":
        await exit_chat(update, context, uid)
        return
    
    if data == "exit_chat_from_start":
        await exit_chat(update, context, uid)
        return
    
    # ===== ПОДДЕРЖКА =====
    if data == "support_start":
        await support_start(update, context)
        return
    
    # ===== ЛИМИТ ИСЧЕРПАН =====
    if data == "limit_exceeded":
        await query.message.edit_text(
            text=get_text(uid, "limit_exceeded"),
            reply_markup=tab_kb(uid)
        )
        return
    
    # ===== НАВИГАЦИЯ =====
    if data == "back_to_previous":
        if uid in navigation_stack:
            prev_tab = navigation_stack[uid]
            del navigation_stack[uid]
            await open_tab(context, query, uid, prev_tab)
        else:
            await edit_to_menu(context, query, uid)
        return
    
    if data == "back_to_menu":
        if uid in navigation_stack:
            del navigation_stack[uid]
        await edit_to_menu(context, query, uid)
        return
    
    if data == "ignore":
        return
    
    # ===== ВКЛАДКИ =====
    if data.startswith("tab:"):
        key = data.split("tab:", 1)[1].strip()
        
        current_tab = context.user_data.get('current_tab')
        parent_tabs = ['settings', 'profile', 'help', 'status', 'ref', 'support', 'buy_stars', 'balance']
        child_tabs = ['ai_mode_settings', 'mode_settings', 'persona_settings', 'lang_settings', 'style_settings', 'ai_lang_settings']
        
        if current_tab in parent_tabs and key in child_tabs:
            navigation_stack[uid] = current_tab
        
        context.user_data['current_tab'] = key
        
        if key == "support":
            await support_start(update, context)
        else:
            await open_tab(context, query, uid, key)
        return
    
    # ===== ПОКУПКА ЗВЕЗД =====
    if data.startswith("buy_stars:"):
        package_id = data.split("buy_stars:", 1)[1].strip()
        await buy_stars_package(update, context, query, uid, package_id)
        return
    
    # ===== НАСТРОЙКИ - ЯЗЫК ИНТЕРФЕЙСА =====
    if data.startswith("set_lang:"):
        lang = data.split("set_lang:", 1)[1].strip()
        await handle_set_lang(update, context, query, uid, lang)
        await open_tab(context, query, uid, "settings")
        return
    
    # ===== НАСТРОЙКИ - ЯЗЫК ОТВЕТОВ ИИ =====
    if data.startswith("set_ai_lang:"):
        lang = data.split("set_ai_lang:", 1)[1].strip()
        await set_ai_lang(update, context, query, uid, lang)
        await open_tab(context, query, uid, "settings")
        return
    
    # ===== НАСТРОЙКИ - ХАРАКТЕР =====
    if data.startswith("set_persona:"):
        persona = data.split("set_persona:", 1)[1].strip()
        
        limits = get_user_limits(uid)
        if limits.get("groq_persona", 0) >= 5:
            await query.message.edit_text(
                text=get_text(uid, "limit_exceeded"),
                reply_markup=tab_kb(uid)
            )
            return
        
        await handle_set_persona(update, context, query, uid, persona)
        await open_tab(context, query, uid, "settings")
        return
    
    # ===== НАСТРОЙКИ - СТИЛЬ =====
    if data.startswith("set_style:"):
        style = data.split("set_style:", 1)[1].strip()
        
        limits = get_user_limits(uid)
        ai_mode = get_ai_mode(uid)
        
        if ai_mode == "fast":
            if limits.get("groq_style", 0) >= 5:
                await query.message.edit_text(
                    text=get_text(uid, "limit_exceeded"),
                    reply_markup=tab_kb(uid)
                )
                return
        else:
            if limits.get("openai_style", 0) >= 7:
                await query.message.edit_text(
                    text=get_text(uid, "limit_exceeded"),
                    reply_markup=tab_kb(uid)
                )
                return
        
        await set_style(update, context, query, uid, style)
        await open_tab(context, query, uid, "settings")
        return
    
    # ===== РЕЖИМ ИИ - ПОДТВЕРЖДЕНИЕ =====
    if data.startswith("confirm_ai_mode:"):
        new_mode = data.split("confirm_ai_mode:", 1)[1].strip()
        current_mode = get_ai_mode(uid) or "fast"
        
        mode_names = {"fast": get_text(uid, "ai_mode_fast"), "quality": get_text(uid, "ai_mode_quality")}
        text = get_text(uid, "confirm_ai_mode_change").format(
            new_mode=mode_names.get(new_mode, new_mode),
            current_mode=mode_names.get(current_mode, current_mode)
        )
        
        try:
            await query.message.edit_text(text, reply_markup=confirm_ai_mode_kb(uid, new_mode))
            set_last_menu(uid, uid, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, uid)
        return
    
    # ===== РЕЖИМ ИИ - ВЫПОЛНЕНИЕ =====
    if data.startswith("execute_ai_mode:"):
        new_mode = data.split("execute_ai_mode:", 1)[1].strip()
        
        changes_left = await get_ai_mode_changes(uid)
        if changes_left <= 0:
            await query.message.edit_text(
                text=get_text(uid, "limit_exceeded"),
                reply_markup=tab_kb(uid)
            )
            return
        
        mem_clear(uid)
        print(f"🧹 Очищена память для пользователя {uid} при смене режима")
        
        set_ai_mode(uid, new_mode)
        
        mode_names = {"fast": get_text(uid, "ai_mode_fast"), "quality": get_text(uid, "ai_mode_quality")}
        await query.message.edit_text(
            get_text(uid, "ai_mode_changed").format(
                mode=mode_names.get(new_mode, new_mode),
                left=changes_left - 1
            ),
            reply_markup=tab_kb(uid)
        )
        return
    
    # ===== ПЕРЕКЛЮЧЕНИЕ РЕЖИМА РАБОТЫ =====
    if data == "switch_to_miniapp":
        await handle_switch_mode(update, context, query, uid, "miniapp")
        await open_tab(context, query, uid, "settings")
        return
    
    if data == "switch_to_inline":
        await handle_switch_mode(update, context, query, uid, "inline")
        await open_tab(context, query, uid, "settings")
        return
    
    # ===== ЧАТ И КАРТИНКИ =====
    if data == "inline_chat":
        await inline_chat_start(update, context)
        return
    
    if data == "inline_image":
        await inline_image_start(update, context)
        return
    
    await edit_to_menu(context, query, uid)


async def open_tab(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    if tab_key == "profile":
        await show_profile(context, query, user_id)
        return
    elif tab_key == "help":
        await show_help(context, query, user_id)
        return
    elif tab_key == "status":
        await show_status(context, query, user_id)
        return
    elif tab_key == "ref":
        await show_ref(context, query, user_id)
        return
    elif tab_key == "support":
        await show_support(context, query, user_id)
        return
    elif tab_key == "buy_stars":
        await show_buy_stars(context, query, user_id)
        return
    elif tab_key == "style_settings":
        await show_style_settings(context, query, user_id)
        return
    elif tab_key == "ai_lang_settings":
        await show_ai_lang_settings(context, query, user_id)
        return
    elif tab_key == "settings":
        text = get_text(user_id, "settings")
        try:
            await query.message.edit_text(text, reply_markup=settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    elif tab_key == "ai_mode_settings":
        changes_left = await get_ai_mode_changes(user_id)
        text = get_text(user_id, "ai_mode_settings").format(changes_left=changes_left)
        try:
            await query.message.edit_text(text, reply_markup=ai_mode_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    elif tab_key == "mode_settings":
        text = get_text(user_id, "mode_settings")
        try:
            await query.message.edit_text(text, reply_markup=mode_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    elif tab_key == "persona_settings":
        text = get_text(user_id, "persona_settings")
        try:
            await query.message.edit_text(text, reply_markup=persona_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    elif tab_key == "lang_settings":
        text = get_text(user_id, "lang_settings")
        try:
            await query.message.edit_text(text, reply_markup=lang_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    elif tab_key == "balance":
        balance = get_balance(user_id)
        formatted_balance = format_balance(balance)
        text = f"⭐ Ваш баланс: {formatted_balance} звезд"
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    else:
        text = get_text(user_id, tab_key) if tab_key in ['blocked', 'need_stars_chat', 'need_stars_miniapp', 'buy_stars'] else "Раздел в разработке."
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return