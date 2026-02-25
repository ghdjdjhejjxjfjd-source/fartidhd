from telegram import Update
from telegram.ext import ContextTypes

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
    ai_mode_settings_kb, confirm_ai_mode_kb, TAB_TEXT
)
from .settings import handle_set_lang, handle_set_persona, handle_switch_mode
from .chat import inline_chat_start
from .image import inline_image_start
from .utils import delete_prev_menu, send_fresh_menu, update_user_menu, edit_to_menu, edit_to_tab, send_block_notice

import requests

# =========================
# НАВИГАЦИЯ - ИСПРАВЛЕНО
# =========================
# Теперь храним ТОЛЬКО предыдущую вкладку для кнопки "Назад"
# Формат: {user_id: предыдущая_вкладка}
navigation_prev = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    # Очищаем навигацию при старте
    if uid in navigation_prev:
        del navigation_prev[uid]
    
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
    
    # ===== ОБРАБОТКА КНОПКИ НАЗАД =====
    if data == "back_to_previous":
        # Если есть предыдущая вкладка - идём туда
        if uid in navigation_prev:
            prev_tab = navigation_prev[uid]
            # Очищаем предыдущую вкладку (чтобы при следующем нажатии шло в главное меню)
            del navigation_prev[uid]
            await edit_to_tab_handler(context, query, uid, prev_tab)
        else:
            # Если нет предыдущей вкладки - идём в главное меню
            await edit_to_menu(context, query, uid)
        return
    
    if data == "back_to_menu":
        # Очищаем навигацию при возврате в главное меню
        if uid in navigation_prev:
            del navigation_prev[uid]
        await edit_to_menu(context, query, uid)
        return
    
    if data == "ignore":
        return
    
    # ===== ОБРАБОТКА ОТКРЫТИЯ ВКЛАДОК =====
    if data.startswith("tab:"):
        key = data.split("tab:", 1)[1].strip()
        
        # Сохраняем ТЕКУЩУЮ вкладку как предыдущую ТОЛЬКО если:
        # 1. Мы не в главном меню сейчас
        # 2. Это не первое открытие вкладки
        current_tab = context.user_data.get('current_tab')
        
        if current_tab and current_tab != key:
            # Если мы уже в какой-то вкладке и открываем новую
            navigation_prev[uid] = current_tab
        elif not current_tab:
            # Если мы в главном меню и открываем вкладку - НЕ сохраняем главное меню в стек
            pass
        
        context.user_data['current_tab'] = key
        await edit_to_tab_handler(context, query, uid, key)
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
            # Сохраняем предыдущую вкладку
            navigation_prev[uid] = context.user_data.get('current_tab', 'settings')
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
    
    # ОБРАБОТКА ПОДТВЕРЖДЕНИЯ СМЕНЫ РЕЖИМА
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
            # Сохраняем предыдущую вкладку
            navigation_prev[uid] = context.user_data.get('current_tab', 'ai_mode_settings')
        except Exception:
            await send_fresh_menu(context.bot, uid)
        return
    
    # ВЫПОЛНЕНИЕ СМЕНЫ РЕЖИМА ПОСЛЕ ПОДТВЕРЖДЕНИЯ
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
        
        from api import set_ai_mode
        set_ai_mode(uid, new_mode)
        
        mode_names = {"fast": "🚀 Быстрый", "quality": "💎 Качественный"}
        await query.message.edit_text(
            f"✅ Режим изменен на {mode_names.get(new_mode, new_mode)}\n\n"
            f"🧹 История чата очищена.\n"
            f"📊 Сегодня осталось смен режима: {changes_left - 1}/8\n\n"
            f"При следующем открытии Mini App начнёте с чистого листа.",
            reply_markup=tab_kb(uid)
        )
        
        # Сохраняем предыдущую вкладку
        navigation_prev[uid] = context.user_data.get('current_tab', 'ai_mode_settings')
        
        await update_user_menu(context.bot, uid)
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


async def edit_to_tab_handler(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    """Обработчик открытия вкладок"""
    
    if tab_key == "profile":
        await show_profile(context, query, user_id)
        return
    
    if tab_key == "settings":
        text = "⚙️ Настройки\n\nВыбери раздел:"
        try:
            await query.message.edit_text(text, reply_markup=settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    
    if tab_key == "ai_mode_settings":
        changes_left = await get_ai_mode_changes(user_id)
        text = TAB_TEXT["ai_mode_settings"].format(changes_left=changes_left)
        try:
            await query.message.edit_text(text, reply_markup=ai_mode_settings_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
        return
    
    await edit_to_tab(context, query, user_id, tab_key)


async def show_profile(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Показать профиль пользователя"""
    from datetime import datetime
    
    a = get_access(user_id)
    balance = get_balance(user_id)
    persona = get_user_persona(user_id)
    lang = get_user_lang(user_id)
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    changes_left = await get_ai_mode_changes(user_id)
    
    persona_names = {
        "friendly": "😊 Общительный",
        "fun": "😂 Весёлый",
        "smart": "🧐 Умный",
        "strict": "😐 Строгий"
    }
    
    lang_names = {
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
        "kk": "🇰🇿 Қазақша",
        "tr": "🇹🇷 Türkçe",
        "uk": "🇺🇦 Українська",
        "fr": "🇫🇷 Français"
    }
    
    ai_mode_names = {
        "fast": "🚀 Быстрый (0.3 ⭐)",
        "quality": "💎 Качественный (1 ⭐)"
    }
    
    registered = "неизвестно"
    if a.get("registered_at"):
        try:
            reg_date = datetime.strptime(a["registered_at"], "%Y-%m-%d %H:%M:%S")
            registered = reg_date.strftime("%d.%m.%Y")
        except:
            registered = a["registered_at"][:10]
    
    text = TAB_TEXT["profile"].format(
        user_id=user_id,
        registered=registered,
        messages=a.get("total_messages", 0),
        images=a.get("total_images", 0),
        spent=a.get("total_stars_spent", 0),
        balance=balance,
        persona=persona_names.get(persona, persona),
        lang=lang_names.get(lang, lang),
        mode="📱 Mini App" if use_mini_app else "💬 Встроенный",
        ai_mode=f"{ai_mode_names.get(ai_mode, ai_mode)} (осталось смен: {changes_left}/8)",
        free="✅ Да" if a.get("is_free") else "❌ Нет",
        blocked="✅ Нет" if not a.get("is_blocked") else "❌ Да"
    )
    
    try:
        await query.message.edit_text(text, reply_markup=tab_kb(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)


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
        from .chat import handle_chat_message
        await handle_chat_message(update, context, uid, text)
        context.user_data["in_chat_mode"] = False
        
    elif context.user_data.get("in_image_mode"):
        from .image import handle_image_generation
        await handle_image_generation(update, context, uid, text)
        context.user_data["in_image_mode"] = False


# Экспортируем все нужные функции
__all__ = [
    'start',
    'on_button',
    'handle_message',
    'send_block_notice'
]