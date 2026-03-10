# bot/ui/keyboards.py
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

    keyboard.append([InlineKeyboardButton(f"💰 Баланс: {balance} ⭐", callback_data="balance")])

    if use_mini_app:
        if (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL):
            keyboard.append([InlineKeyboardButton("🚀 Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            keyboard.append([InlineKeyboardButton("🚀 Mini App", callback_data="need_stars")])
    else:
        keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="mode_chat")])
        keyboard.append([InlineKeyboardButton("🖼 Картинка", callback_data="mode_image")])
        keyboard.append([InlineKeyboardButton("🔧 Инструменты", callback_data="mode_tools")])

    keyboard.append([InlineKeyboardButton("⭐ Купить звезды", callback_data="buy_menu")])
    keyboard.append([
        InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    ])

    return InlineKeyboardMarkup(keyboard)

def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]])

def tools_keyboard(user_id: int) -> InlineKeyboardMarkup:
    a = get_access(user_id)
    balance = get_balance(user_id)
    
    tools = [
        ("remove_bg", "📸 Удаление фона", 2),
        ("ocr", "📝 Текст с фото", 1),
        ("meme", "🎭 Создание мемов", 1),
        ("qr", "📱 QR код", 1),
    ]
    
    keyboard = []
    for tool_id, name, cost in tools:
        if a.get("is_free") or balance >= cost:
            keyboard.append([InlineKeyboardButton(f"{name} ({cost}⭐)", callback_data=f"tool_{tool_id}")])
        else:
            keyboard.append([InlineKeyboardButton(f"{name} ❌", callback_data="need_stars")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)