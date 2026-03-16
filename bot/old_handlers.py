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
from .utils import delete_prev_menu, send_fresh_menu, update_user_menu, edit_to_menu, send_block_notice

navigation_stack = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    if uid in navigation_stack:
        del navigation_stack[uid]
    
    print(f"🚀 /start от пользователя {uid}")
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
    
    print(f"🖱️ Нажата кнопка: {data} от {uid}")
    
    # ===== ВЫХОД ИЗ ЧАТА (НОВАЯ КНОПКА) =====
    if data == "exit_chat":
        print(f"🚪 Выход из чата через кнопку для {uid}")
        context.user_data["in_chat_mode"] = False
        
        # Удаляем сообщение с кнопкой
        try:
            await query.message.delete()
            print(f"🗑️ Удалено сообщение с кнопкой для {uid}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить сообщение: {e}")
        
        # Отправляем новое меню
        await send_fresh_menu(context.bot, uid)
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
            try:
                await query.message.edit_text(
                    "⛔ Лимит смены режима на сегодня исчерпан",
                    reply_markup=tab_kb(uid)
                )
                set_last_menu(uid, uid, query.message.message_id)
            except Exception:
                await send_fresh_menu(context.bot, uid)
            return
        
        mem_clear(uid)
        from api import set_ai_mode
        set_ai_mode(uid, new_mode)
        
        mode_names = {"fast": "🚀 Быстрый", "quality": "💎 Качественный"}
        try:
            await query.message.edit_text(
                f"✅ Режим изменен на {mode_names.get(new_mode, new_mode)}",
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
        text = TAB_TEXT.get("need_stars_chat", "⭐ Недостаточно звезд для чата")
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
    elif tab_key == "need_stars_miniapp":
        text = TAB_TEXT.get("need_stars_miniapp", "⭐ Недостаточно звезд для Mini App")
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
            set_last_menu(user_id, user_id, query.message.message_id)
        except Exception:
            await send_fresh_menu(context.bot, user_id)
    
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
    
    elif tab_key == "balance":
        balance = get_balance(user_id)
        text = f"⭐ Ваш баланс: {balance} звезд"
        try:
            await query.message.edit_text(text, reply_markup=tab_kb(user_id))
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
        text = TAB_TEXT.get(tab_key, "🌐 Язык интерфейса\n\nВыбери язык меню и кнопок:")
        try:
            await query.message.edit_text(text, reply_markup=lang_settings_kb(user_id))
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

async def show_profile(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
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
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    uid = user.id
    text = update.message.text
    
    print(f"📨 handle_message: uid={uid}, text='{text}'")
    
    # Проверяем режим чата
    in_chat_mode = context.user_data.get("in_chat_mode", False)
    
    if not in_chat_mode:
        return
    
    a = get_access(uid)
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        context.user_data.clear()
        return
    
    from .chat import handle_chat_message
    await handle_chat_message(update, context, uid, text)

__all__ = [
    'start',
    'on_button',
    'handle_message',
    'send_block_notice'
]