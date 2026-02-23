# bot/utils.py
from api import get_last_menu, set_last_menu, clear_last_menu


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