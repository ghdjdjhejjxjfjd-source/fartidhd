# bot/ui/keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from api import get_use_mini_app, get_access
from payments import get_balance
from bot.config import MINIAPP_URL, is_valid_https_url

def main_menu(user_id: int) -> InlineKeyboardMarkup:
    """Главное меню"""
    a = get_access(user_id)
    balance = get_balance(user_id)
    use_mini_app = get_use_mini_app(user_id)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton("⛔ Доступ заблокирован", callback_data="blocked")])
        return InlineKeyboardMarkup(keyboard)

    # Баланс
    keyboard.append([InlineKeyboardButton(f"⭐ Баланс: {balance} звезд", callback_data="balance")])

    # Кнопки в зависимости от режима
    if use_mini_app:
        can_open = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        if can_open:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="need_stars")])
    else:
        # Встроенный режим
        keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="mode:chat")])
        keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="mode:image")])
        keyboard.append([InlineKeyboardButton("🔧 Инструменты", callback_data="mode:tools")])

    # Покупка звезд
    keyboard.append([InlineKeyboardButton("⭐ Купить звезды", callback_data="buy_menu")])

    # Настройки и помощь
    keyboard.append([
        InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    ])

    return InlineKeyboardMarkup(keyboard)

def back_button() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]])

def buy_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню покупки звезд"""
    from payments import get_packages
    keyboard = []
    packages = get_packages()
    
    for p in packages:
        stars = p["stars"]
        price = f"${p['price_usd']:.2f}"
        discount = f" 🔥 -{p['discount']}%" if p['discount'] > 0 else ""
        popular = " ⭐" if p.get('popular', False) else ""
        
        btn_text = f"{stars} ⭐ – {price}{discount}{popular}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy:{p['id']}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)

def help_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура помощи"""
    keyboard = [
        [InlineKeyboardButton("📚 FAQ", callback_data="help:faq")],
        [InlineKeyboardButton("💬 Поддержка", callback_data="help:support")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="help:about")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    keyboard = [
        [InlineKeyboardButton("🎭 Характер ИИ", callback_data="settings:persona")],
        [InlineKeyboardButton("🔄 Режим работы", callback_data="settings:mode")],
        [InlineKeyboardButton("🌐 Язык", callback_data="settings:lang")],
        [InlineKeyboardButton("⚡ Режим ИИ", callback_data="settings:ai_mode")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def tools_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура инструментов"""
    a = get_access(user_id)
    balance = get_balance(user_id)
    
    tools = [
        {"id": "remove_bg", "name": "📸 Удаление фона", "cost": 2},
        {"id": "ocr", "name": "📝 Текст с фото", "cost": 1},
        {"id": "meme", "name": "🎭 Создание мемов", "cost": 1},
        {"id": "music", "name": "🎵 Music Lab", "cost": 2},
        {"id": "qr", "name": "📱 QR коды", "cost": 1},
    ]
    
    keyboard = []
    for tool in tools:
        can_use = a.get("is_free") or balance >= tool["cost"]
        if can_use:
            btn_text = f"{tool['name']} ({tool['cost']}⭐)"
        else:
            btn_text = f"{tool['name']} ❌"
        
        keyboard.append([InlineKeyboardButton(
            btn_text,
            callback_data=f"tool:{tool['id']}" if can_use else "need_stars"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)