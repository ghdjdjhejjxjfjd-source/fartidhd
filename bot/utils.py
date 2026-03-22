# bot/utils.py - ПОЛНАЯ ВЕРСИЯ С handle_message
from api import get_last_menu, set_last_menu, clear_last_menu
from telegram.ext import ContextTypes
from telegram import Update
import time

# Глобальное хранилище для отслеживания последнего отправленного меню
_last_sent_menu = {}


async def delete_prev_menu(bot, user_id: int):
    """Удалить предыдущее меню пользователя"""
    chat_id, msg_id = get_last_menu(user_id)
    
    print(f"🔍 Пытаюсь удалить меню для {user_id}: chat_id={chat_id}, msg_id={msg_id}")
    
    if not chat_id or not msg_id:
        print(f"❌ Нет сохраненного меню для {user_id}")
        return False
    
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        print(f"✅ Удалено старое меню {msg_id} для {user_id}")
        clear_last_menu(user_id)
        return True
    except Exception as e:
        print(f"⚠️ Ошибка удаления меню {msg_id} для {user_id}: {e}")
        clear_last_menu(user_id)
        return False


async def delete_all_menus(bot, user_id: int):
    """Удалить ТОЛЬКО меню пользователя"""
    print(f"🧹 Удаляю меню для {user_id}")
    return await delete_prev_menu(bot, user_id)


async def send_fresh_menu(bot, user_id: int, text: str = None):
    """Отправить новое меню (отредактировав старое если есть) - ГАРАНТИРОВАННО ОДНО МЕНЮ"""
    from .menu import main_menu_for_user
    
    current_time = time.time()
    if user_id in _last_sent_menu:
        last_time = _last_sent_menu[user_id]
        if current_time - last_time < 1.0:
            print(f"⚠️ Пропущен дубль меню для {user_id} (менее 1 секунды)")
            return None
    
    if text is None:
        text = "💫 NextAI\n\nВыбирай действие кнопками ниже 👇"
    
    chat_id, msg_id = get_last_menu(user_id)
    
    if chat_id and msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                reply_markup=main_menu_for_user(user_id)
            )
            print(f"✅ Отредактировано меню для {user_id} (ID: {msg_id})")
            _last_sent_menu[user_id] = current_time
            return None
        except Exception as e:
            print(f"⚠️ Не удалось отредактировать меню {msg_id}: {e}")
            await delete_prev_menu(bot, user_id)
    
    await delete_prev_menu(bot, user_id)
    
    try:
        m = await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=main_menu_for_user(user_id),
        )
        set_last_menu(user_id, user_id, m.message_id)
        print(f"✅ Отправлено НОВОЕ меню для {user_id} (ID: {m.message_id})")
        _last_sent_menu[user_id] = current_time
        return m
    except Exception as e:
        print(f"❌ Ошибка отправки меню для {user_id}: {e}")
        return None


async def update_user_menu(bot, user_id: int):
    """Обновить меню пользователя"""
    await send_fresh_menu(bot, user_id)


async def send_block_notice(bot, user_id: int):
    """Отправить уведомление о блокировке"""
    await delete_prev_menu(bot, user_id)
    await bot.send_message(chat_id=user_id, text="⛔ Доступ заблокирован.")


async def edit_to_menu(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Редактировать текущее сообщение в главное меню"""
    from .menu import main_menu_for_user
    
    clear_last_menu(user_id)
    
    try:
        await query.message.edit_text(
            "💫 NextAI\n\nВыбирай действие кнопками ниже 👇",
            reply_markup=main_menu_for_user(user_id)
        )
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Отредактировано в меню для {user_id}")
    except Exception as e:
        print(f"⚠️ Не удалось отредактировать в меню: {e}")
        await send_fresh_menu(context.bot, user_id)


async def edit_to_tab(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    """Редактировать текущее сообщение в указанную вкладку"""
    from .menu import stars_kb, mode_settings_kb, persona_settings_kb, lang_settings_kb
    from .locales import get_text
    from payments import get_balance
    
    text = get_text(user_id, tab_key) if tab_key in ['blocked', 'need_stars_chat', 'need_stars_miniapp', 'buy_stars', 'settings', 'mode_settings', 'persona_settings', 'lang_settings'] else "Раздел в разработке."
    
    if tab_key == "balance":
        balance = get_balance(user_id)
        if balance == int(balance):
            formatted_balance = str(int(balance))
        else:
            formatted_balance = f"{balance:.1f}"
        text = f"⭐ Ваш баланс: {formatted_balance} звезд"
    
    if tab_key == "buy_stars":
        reply_markup = stars_kb(user_id)
    elif tab_key == "mode_settings":
        reply_markup = mode_settings_kb(user_id)
    elif tab_key == "persona_settings":
        reply_markup = persona_settings_kb(user_id)
    elif tab_key == "lang_settings":
        reply_markup = lang_settings_kb(user_id)
    else:
        from .menu import tab_kb
        reply_markup = tab_kb(user_id)
    
    clear_last_menu(user_id)
    
    try:
        await query.message.edit_text(text, reply_markup=reply_markup)
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Отредактировано во вкладку {tab_key} для {user_id}")
    except Exception as e:
        print(f"⚠️ Не удалось отредактировать во вкладку: {e}")
        await send_fresh_menu(context.bot, user_id)


# =========================
# ОБРАБОТЧИК СООБЩЕНИЙ
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений - перенаправляет в старый обработчик из old_handlers"""
    from bot.old_handlers import handle_message as old_handle_message
    await old_handle_message(update, context)