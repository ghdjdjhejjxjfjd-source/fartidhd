# bot/ui/keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from api import get_use_mini_app, get_user_persona, get_user_lang, get_ai_mode
from payments import get_balance
from bot.config import MINIAPP_URL, is_valid_https_url

def main_menu(user_id: int) -> InlineKeyboardMarkup:
    """Главное меню"""
    from api import get_access
    a = get_access(user_id)
    balance = get_balance(user_id)
    use_mini_app = get_use_mini_app(user_id)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton("⛔ Доступ заблокирован", callback_data="tab:blocked")])
        return InlineKeyboardMarkup(keyboard)

    # Баланс
    keyboard.append([InlineKeyboardButton(f"⭐ Баланс: {balance} звезд", callback_data="tab:balance")])

    # Кнопки в зависимости от режима
    if use_mini_app:
        can_open = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        if can_open:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_stars")])
    else:
        # Встроенный режим - кнопки ведут в наши файлы
        keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="mode:chat")])
        keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="mode:image")])
        keyboard.append([InlineKeyboardButton("🔧 Инструменты", callback_data="mode:tools")])

    # Покупка звезд
    keyboard.append([InlineKeyboardButton("⭐ Купить звезды", callback_data="tab:buy_stars")])

    # Настройки и помощь
    keyboard.append([
        InlineKeyboardButton("⚙️ Настройки", callback_data="tab:settings"),
        InlineKeyboardButton("❓ Помощь", callback_data="tab:help"),
    ])

    return InlineKeyboardMarkup(keyboard)

def back_button() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]])

def settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    keyboard = [
        [InlineKeyboardButton("🎭 Характер ИИ", callback_data="tab:persona")],
        [InlineKeyboardButton("🔄 Режим работы", callback_data="tab:mode_settings")],
        [InlineKeyboardButton("🌐 Язык", callback_data="tab:lang")],
        [InlineKeyboardButton("⚡ Режим ИИ", callback_data="tab:ai_mode")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)