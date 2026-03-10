from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from api import get_use_mini_app, get_access
from payments import get_balance
from bot.config import MINIAPP_URL, is_valid_https_url

def main_menu(user_id: int) -> InlineKeyboardMarkup:
    a = get_access(user_id)
    balance = get_balance(user_id)
    use_mini_app = get_use_mini_app(user_id)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton("⛔ Доступ заблокирован", callback_data="blocked")])
        return InlineKeyboardMarkup(keyboard)

    keyboard.append([InlineKeyboardButton(f"⭐ Баланс: {balance} звезд", callback_data="profile")])

    if use_mini_app:
        can_open = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        if can_open:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="need_stars")])
    else:
        keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="chat")])
        keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="image")])
        keyboard.append([InlineKeyboardButton("🔧 Инструменты", callback_data="tools")])

    keyboard.append([
        InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    ])

    return InlineKeyboardMarkup(keyboard)

def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]])

def settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🌐 Язык", callback_data="settings_lang")],
        [InlineKeyboardButton("🎭 Характер", callback_data="settings_persona")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def lang_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kk")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def persona_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("😊 Общительный", callback_data="persona_friendly")],
        [InlineKeyboardButton("😂 Весёлый", callback_data="persona_fun")],
        [InlineKeyboardButton("🧐 Умный", callback_data="persona_smart")],
        [InlineKeyboardButton("😐 Строгий", callback_data="persona_strict")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)