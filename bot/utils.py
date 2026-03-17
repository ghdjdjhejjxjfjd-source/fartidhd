# bot/utils.py
from api import get_last_menu, set_last_menu, clear_last_menu
from telegram.ext import ContextTypes

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
        # Даже если ошибка - очищаем запись, чтобы не пытаться снова
        clear_last_menu(user_id)
        return False

async def delete_all_menus(bot, user_id: int):
    """Удалить ВСЕ возможные меню пользователя"""
    print(f"🧹 Удаляю все меню для {user_id}")
    
    deleted_count = 0
    
    # 1. Пробуем удалить сохраненное меню
    await delete_prev_menu(bot, user_id)
    
    # 2. Пробуем найти и удалить последние 10 сообщений бота
    try:
        updates = await bot.get_updates()
        for update in updates:
            if update.message and update.message.chat.id == user_id:
                try:
                    await bot.delete_message(
                        chat_id=user_id, 
                        message_id=update.message.message_id
                    )
                    deleted_count += 1
                    print(f"✅ Удалено сообщение {update.message.message_id}")
                except:
                    pass
    except Exception as e:
        print(f"⚠️ Ошибка при массовом удалении: {e}")
    
    print(f"✅ Всего удалено сообщений: {deleted_count}")
    return deleted_count

async def send_fresh_menu(bot, user_id: int, text: str = None):
    """Отправить новое меню (отредактировав старое если есть)"""
    from .menu import main_menu_for_user
    
    chat_id, msg_id = get_last_menu(user_id)
    
    if text is None:
        text = "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇"
    
    # Если есть сохраненное меню - пробуем отредактировать
    if chat_id and msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                reply_markup=main_menu_for_user(user_id)
            )
            print(f"✅ Отредактировано меню для {user_id} (ID: {msg_id})")
            # ID не меняется, поэтому не обновляем в БД
            return
        except Exception as e:
            print(f"⚠️ Не удалось отредактировать меню {msg_id}: {e}")
            # Если не получилось - удаляем старое и создаем новое
            await delete_prev_menu(bot, user_id)
    
    # Создаем новое меню
    m = await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=main_menu_for_user(user_id),
    )
    set_last_menu(user_id, user_id, m.message_id)
    print(f"✅ Отправлено НОВОЕ меню для {user_id} (ID: {m.message_id})")
    return m

async def update_user_menu(bot, user_id: int):
    """Обновить меню пользователя"""
    await send_fresh_menu(bot, user_id)

async def send_block_notice(bot, user_id: int):
    """Отправить уведомление о блокировке"""
    await delete_all_menus(bot, user_id)
    await bot.send_message(chat_id=user_id, text="⛔ Доступ заблокирован.")

async def edit_to_menu(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Редактировать текущее сообщение в главное меню"""
    from .menu import main_menu_for_user
    
    clear_last_menu(user_id)
    
    try:
        await query.message.edit_text(
            "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
            reply_markup=main_menu_for_user(user_id)
        )
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Отредактировано в меню для {user_id}")
    except Exception as e:
        print(f"⚠️ Не удалось отредактировать в меню: {e}")
        await send_fresh_menu(context.bot, user_id)

async def edit_to_tab(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    """Редактировать текущее сообщение в указанную вкладку"""
    from .menu import TAB_TEXT, tab_kb, stars_kb, mode_settings_kb, persona_settings_kb, lang_settings_kb
    from payments import get_balance
    
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
    
    clear_last_menu(user_id)
    
    try:
        await query.message.edit_text(text, reply_markup=reply_markup)
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Отредактировано во вкладку {tab_key} для {user_id}")
    except Exception as e:
        print(f"⚠️ Не удалось отредактировать во вкладку: {e}")
        await send_fresh_menu(context.bot, user_id)