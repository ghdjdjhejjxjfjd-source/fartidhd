# bot/old_handlers.py - ИСПРАВЛЕННАЯ ВЕРСИЯ (без TAB_TEXT)
from telegram import Update
from telegram.ext import ContextTypes
import os

from api import (
    get_access, get_last_menu, set_last_menu, clear_last_menu,
    get_use_mini_app, get_user_persona, get_user_lang, get_ai_mode,
    get_ai_mode_changes, mem_clear
)
from payments import get_balance, get_package

from .config import send_log_http, build_start_log
from .menu import (
    main_menu_for_user, tab_kb, stars_kb, mode_settings_kb, 
    persona_settings_kb, lang_settings_kb, settings_kb, 
    ai_mode_settings_kb, confirm_ai_mode_kb
)
from .locales import get_text  # ← добавляем импорт
from .settings import handle_set_lang, handle_set_persona, handle_switch_mode
from .chat import inline_chat_start, exit_chat
from .image import inline_image_start, exit_image, exit_image_from_start
from .utils import delete_prev_menu, send_fresh_menu, update_user_menu, edit_to_menu, send_block_notice
from .support import support_start, forward_to_support

SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "0"))
navigation_stack = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    uid = user.id if user else 0
    
    # Если это группа поддержки - игнорируем
    if update.effective_chat and update.effective_chat.id == SUPPORT_GROUP_ID:
        print(f"🚫 /start в группе поддержки проигнорирован")
        return
    
    send_log_http(build_start_log(update))
    
    if not uid:
        return
    
    if uid in navigation_stack:
        del navigation_stack[uid]
    
    print(f"🚀 /start от пользователя {uid}")
    await send_fresh_menu(context.bot, uid)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = (query.data or "").strip()
    
    # Если это группа поддержки - игнорируем все кнопки
    if update.effective_chat and update.effective_chat.id == SUPPORT_GROUP_ID:
        print(f"🚫 Кнопка {data} в группе поддержки проигнорирована")
        await query.answer("❌ Кнопки не работают в группе поддержки")
        return
    
    try:
        await query.answer()
    except Exception:
        pass
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    print(f"🖱️ Нажата кнопка: {data} от {uid}")
    
    # ===== ВЫХОД ИЗ ГЕНЕРАЦИИ КАРТИНКИ =====
    if data == "exit_image":
        await exit_image(update, context, uid)
        return
    
    if data == "exit_image_from_start":
        await exit_image_from_start(update, context, uid)
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
    
    # ===== КНОПКА НАЗАД =====
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
        child_tabs = ['ai_mode_settings', 'mode_settings', 'persona_settings', 'lang_settings']
        
        if current_tab in parent_tabs and key in child_tabs:
            navigation_stack[uid] = current_tab
        
        context.user_data['current_tab'] = key
        
        # Специальная обработка для поддержки
        if key == "support":
            await support_start(update, context)
        else:
            await open_tab(context, query, uid, key)
        return
    
    # ===== ПОКУПКА ЗВЕЗД =====
    if data.startswith("buy_stars:"):
        package_id = data.split("buy_stars:", 1)[1].strip()
        package = get_package(package_id)
        
        if package:
            stars = package["stars"]
            price = package["price_usd"]
            try:
                await query.message.edit_text(
                    f"✅ Вы выбрали пакет {package['name']}\n"
                    f"⭐ {stars} звезд за ${price}",
                    reply_markup=tab_kb(uid)
                )
                set_last_menu(uid, uid, query.message.message_id)
            except Exception:
                await send_fresh_menu(context.bot, uid)
        else:
            try:
                await query.message.edit_text("❌ Пакет не найден", reply_markup=tab_kb(uid))
                set_last_menu(uid, uid, query.message.message_id)
            except Exception:
                await send_fresh_menu(context.bot, uid)
        return
    
    # ===== НАСТРОЙКИ =====
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
    
    # ===== РЕЖИМ ИИ =====
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
    
    if data.startswith("execute_ai_mode:"):
        new_mode = data.split("execute_ai_mode:", 1)[1].strip()
        
        changes_left = await get_ai_mode_changes(uid)
        if changes_left <= 0:
            try:
                await query.message.edit_text(
                    get_text(uid, "limit_exceeded"),
                    reply_markup=tab_kb(uid)
                )
                set_last_menu(uid, uid, query.message.message_id)
            except Exception:
                await send_fresh_menu(context.bot, uid)
            return
        
        mem_clear(uid)
        from api import set_ai_mode
        set_ai_mode(uid, new_mode)
        
        mode_names = {"fast": get_text(uid, "ai_mode_fast"), "quality": get_text(uid, "ai_mode_quality")}
        try:
            await query.message.edit_text(
                get_text(uid, "ai_mode_changed").format(
                    mode=mode_names.get(new_mode, new_mode),
                    left=changes_left - 1
                ),
                reply_markup=tab_kb(uid)
            )
            set_last_menu(uid, uid, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, uid)
        
        await update_user_menu(context.bot, uid)
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
    print(f"📂 Открываем вкладку: {tab_key} для {user_id}")
    
    if tab_key == "profile":
        await show_profile(context, query, user_id)
    
    elif tab_key == "need_stars_chat":
        text = get_text(user_id, "need_stars_chat")
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "need_stars_miniapp":
        text = get_text(user_id, "need_stars_miniapp")
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "settings":
        text = get_text(user_id, "settings")
        try:
            await query.message.edit_text(text, reply_markup=settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "ai_mode_settings":
        changes_left = await get_ai_mode_changes(user_id)
        text = get_text(user_id, "ai_mode_settings").format(changes_left=changes_left)
        try:
            await query.message.edit_text(text, reply_markup=ai_mode_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "balance":
        balance = get_balance(user_id)
        # Форматируем баланс
        if balance == int(balance):
            formatted_balance = str(int(balance))
        else:
            formatted_balance = f"{balance:.1f}"
        text = f"⭐ Ваш баланс: {formatted_balance} звезд"
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "mode_settings":
        text = get_text(user_id, "mode_settings")
        try:
            await query.message.edit_text(text, reply_markup=mode_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "persona_settings":
        text = get_text(user_id, "persona_settings")
        try:
            await query.message.edit_text(text, reply_markup=persona_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "lang_settings":
        text = get_text(user_id, "lang_settings")
        try:
            await query.message.edit_text(text, reply_markup=lang_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    else:
        text = get_text(user_id, tab_key) if tab_key in ['blocked', 'help', 'status', 'ref', 'support', 'buy_stars'] else "Раздел в разработке."
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)


async def show_profile(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    from datetime import datetime
    from bot.helpers import format_balance
    
    a = get_access(user_id)
    balance = get_balance(user_id)
    formatted_balance = format_balance(balance)
    persona = get_user_persona(user_id)
    lang = get_user_lang(user_id)
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    changes_left = await get_ai_mode_changes(user_id)
    
    persona_names = {
        "friendly": get_text(user_id, "persona_friendly"),
        "fun": get_text(user_id, "persona_fun"),
        "smart": get_text(user_id, "persona_smart"),
        "strict": get_text(user_id, "persona_strict")
    }
    
    lang_names = {
        "ru": get_text(user_id, "lang_ru"),
        "en": get_text(user_id, "lang_en"),
        "kk": get_text(user_id, "lang_kk"),
        "tr": get_text(user_id, "lang_tr"),
        "uk": get_text(user_id, "lang_uk"),
        "fr": get_text(user_id, "lang_fr")
    }
    
    ai_mode_names = {
        "fast": get_text(user_id, "ai_mode_fast"),
        "quality": get_text(user_id, "ai_mode_quality")
    }
    
    registered = "неизвестно"
    if a.get("registered_at"):
        try:
            reg_date = datetime.strptime(a["registered_at"], "%Y-%m-%d %H:%M:%S")
            registered = reg_date.strftime("%d.%m.%Y")
        except:
            registered = a["registered_at"][:10]
    
    # Получаем username
    username = "—"
    if query.from_user and query.from_user.username:
        username = f"@{query.from_user.username}"
    
    text = get_text(user_id, "profile").format(
        username=username,
        registered=registered,
        messages=a.get("total_messages", 0),
        images=a.get("total_images", 0),
        spent=a.get("total_stars_spent", 0),
        balance=formatted_balance,
        persona=persona_names.get(persona, persona),
        lang=lang_names.get(lang, lang),
        mode=get_text(user_id, "mode_miniapp") if use_mini_app else get_text(user_id, "mode_inline"),
        ai_mode=f"{ai_mode_names.get(ai_mode, ai_mode)} (осталось смен: {changes_left}/8)"
    )
    
    try:
        await query.message.edit_text(text, reply_markup=tab_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если это группа поддержки - не обрабатываем как обычные сообщения
    if update.effective_chat and update.effective_chat.id == SUPPORT_GROUP_ID:
        return
    
    # Проверяем наличие сообщения
    if not update.message:
        return
    
    user = update.effective_user
    uid = user.id
    
    # ===== ПРОВЕРКА НА РЕЖИМ ГЕНЕРАЦИИ КАРТИНКИ =====
    if context.user_data.get("in_image_mode", False):
        if not update.message.text:
            await update.message.reply_text("❌ Отправьте текстовое описание картинки")
            return
        
        from .image import handle_image_generation
        await handle_image_generation(update, context, uid, update.message.text)
        return
    
    # ===== ПРОВЕРКА НА РЕЖИМ ПОДДЕРЖКИ =====
    if context.user_data.get("in_support_mode", False):
        await forward_to_support(update, context)
        return
    
    in_chat_mode = context.user_data.get("in_chat_mode", False)
    
    if not in_chat_mode:
        return
    
    a = get_access(uid)
    if a.get("is_blocked"):
        await update.message.reply_text(get_text(uid, "blocked_access"))
        context.user_data.clear()
        return
    
    # Для чата с ИИ нужен текст
    if not update.message.text:
        await update.message.reply_text("❌ В чате можно отправлять только текст")
        return
    
    from .chat import handle_chat_message
    await handle_chat_message(update, context, uid, update.message.text)


__all__ = [
    'start',
    'on_button',
    'handle_message',
    'send_block_notice'
]