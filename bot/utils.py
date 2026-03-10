# bot/utils.py
from api import get_last_menu, set_last_menu, clear_last_menu
from telegram.ext import ContextTypes


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
    from .menu import main_menu_for_user
    
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
    """Отправить уведомление о блокировке"""
    await delete_prev_menu(bot, user_id)
    await bot.send_message(chat_id=user_id, text="⛔ Доступ заблокирован.")


async def edit_to_menu(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Редактировать текущее сообщение в главное меню"""
    from .menu import main_menu_for_user
    
    try:
        await query.message.edit_text(
            "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
            reply_markup=main_menu_for_user(user_id)
        )
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
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
    
    try:
        await query.message.edit_text(text, reply_markup=reply_markup)
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)