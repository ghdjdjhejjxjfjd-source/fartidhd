from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from api import get_use_mini_app, get_user_persona, get_user_lang, get_user_ai_lang, get_user_style, get_ai_mode
from payments import get_balance
from .config import MINIAPP_URL, is_valid_https_url

# =========================
# ТЕКСТЫ МЕНЮ
# =========================
MENU_TEXT = "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇"

TAB_TEXT = {
    "blocked": "⛔ Доступ заблокирован.\n\nЕсли ты считаешь это ошибкой — напиши админу.",
    "need_pay": "💰 Чтобы открыть Mini App, нужно купить пакет.\n\nОплату подключим позже.",
    "need_stars": "⭐ Для доступа к Mini App нужна хотя бы 1 звезда.\n\nКупите пакет звезд ниже 👇",
    "buy_pack": "💰 Купить пакет\n\nПакеты сообщений (пример):\n• 100 сообщений — 99₽\n• 500 сообщений — 399₽\n• 2000 сообщений — 999₽\n\nОплату подключим позже.",
    "settings": "⚙️ Настройки\n\nВыбери раздел:",
    "help": "❓ Помощь\n\nНажми «Открыть Mini App» или используй встроенный чат.",
    "profile": "👤 ПРОФИЛЬ\n\n"
               "🆔 ID: {user_id}\n"
               "📅 В боте с: {registered}\n\n"
               "📊 СТАТИСТИКА\n"
               "💬 Сообщений: {messages}\n"
               "🖼 Картинок: {images}\n"
               "⭐ Потрачено звезд: {spent}\n"
               "💎 Остаток: {balance}\n\n"
               "⚙️ ТЕКУЩЕЕ\n"
               "🎭 Характер: {persona}\n"
               "📝 Стиль: {style}\n"
               "🌐 Язык интерфейса: {lang}\n"
               "🌐 Язык ответов: {ai_lang}\n"
               "🔄 Режим работы: {mode}\n"
               "⚡ Режим ИИ: {ai_mode}\n"
               "💳 FREE: {free}\n"
               "⛔ Блок: {blocked}",
    "status": "📌 Статус\n\nРаздел в разработке.",
    "ref": "🎁 Рефералы\n\nРаздел в разработке.",
    "support": "💬 Поддержка\n\nРаздел в разработке.",
    "faq": "📚 FAQ\n\nРаздел в разработке.",
    "about": "ℹ️ О проекте\n\nРаздел в разработке.",
    "buy_stars": "⭐ Пакеты звезд\n\nВыберите пакет для пополнения:",
    "balance": "⭐ Ваш баланс звезд",
    "mode_settings": "🔄 Режим работы\n\nВыбери как пользоваться ботом:",
    "persona_settings": "🎭 Характер ИИ\n\nВыбери как ИИ будет отвечать:",
    "style_settings": "📝 Стиль ответа\n\nВыбери стиль ответов ИИ:",
    "lang_settings": "🌐 Язык интерфейса\n\nВыбери язык меню и кнопок:",
    "ai_lang_settings": "🌐 Язык ответов ИИ\n\nВыбери на каком языке будет отвечать ИИ:",
    "ai_mode_settings": "⚡ Режим ИИ\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
                        "🚀 БЫСТРЫЙ (0.3 ⭐)\n"
                        "• Groq AI\n"
                        "• Можно менять характер, стиль и язык ответов\n\n"
                        "💎 КАЧЕСТВЕННЫЙ (1 ⭐)\n"
                        "• OpenAI\n"
                        "• Можно менять только стиль\n"
                        "• Язык определяется автоматически\n"
                        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        "📊 Сегодня осталось смен режима: {changes_left}/8\n"
                        "⏰ Сброс в 00:00 (GMT+6)",
    "confirm_ai_mode_change": "⚠️ ПОДТВЕРЖДЕНИЕ\n\nВы выбрали режим: {new_mode}\n\nТекущий режим: {current_mode}\n\nПри смене режима:\n• История чата будет полностью очищена\n• Все предыдущие сообщения удалятся\n\nПродолжить?",
}


# =========================
# ВСПОМОГАТЕЛЬНЫЕ КЛАВИАТУРЫ
# =========================
def tab_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад (возврат в предыдущую вкладку)"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")]])


def settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    
    keyboard = []
    
    # Кнопки ТОЛЬКО для встроенного режима
    if not use_mini_app:
        # Язык ответов ИИ - только для быстрого режима (Groq)
        if ai_mode == "fast":
            keyboard.append([InlineKeyboardButton("🌐 Язык ответов ИИ", callback_data="tab:ai_lang_settings")])
        
        # Характер - только для быстрого режима (Groq)
        if ai_mode == "fast":
            keyboard.append([InlineKeyboardButton("🎭 Характер ИИ", callback_data="tab:persona_settings")])
        
        # Стиль - доступен всегда
        keyboard.append([InlineKeyboardButton("📝 Стиль ответа", callback_data="tab:style_settings")])
        
        # Режим ИИ - только для встроенного режима!
        keyboard.append([InlineKeyboardButton("⚡ Режим ИИ", callback_data="tab:ai_mode_settings")])
    
    # Остальные кнопки всегда
    keyboard.append([InlineKeyboardButton("🔄 Режим работы", callback_data="tab:mode_settings")])
    keyboard.append([InlineKeyboardButton("🌐 Язык интерфейса", callback_data="tab:lang_settings")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    
    return InlineKeyboardMarkup(keyboard)


def mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора режима работы (Mini App / Встроенный)"""
    use_mini_app = get_use_mini_app(user_id)
    
    keyboard = []
    if use_mini_app:
        keyboard.append([InlineKeyboardButton("✅ Mini App", callback_data="ignore")])
        keyboard.append([InlineKeyboardButton("💬 Встроенный", callback_data="switch_to_inline")])
    else:
        keyboard.append([InlineKeyboardButton("📱 Mini App", callback_data="switch_to_miniapp")])
        keyboard.append([InlineKeyboardButton("✅ Встроенный", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def ai_mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора режима ИИ (Быстрый / Качественный)"""
    current = get_ai_mode(user_id) or "fast"
    
    keyboard = []
    
    if current == "fast":
        keyboard.append([InlineKeyboardButton("✅ 🚀 Быстрый", callback_data="ignore")])
        keyboard.append([InlineKeyboardButton("💎 Качественный", callback_data="confirm_ai_mode:quality")])
    else:
        keyboard.append([InlineKeyboardButton("🚀 Быстрый", callback_data="confirm_ai_mode:fast")])
        keyboard.append([InlineKeyboardButton("✅ 💎 Качественный", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    
    return InlineKeyboardMarkup(keyboard)


def confirm_ai_mode_kb(user_id: int, new_mode: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения смены режима"""
    keyboard = [
        [InlineKeyboardButton("✅ Да, сменить", callback_data=f"execute_ai_mode:{new_mode}")],
        [InlineKeyboardButton("❌ Нет, отмена", callback_data="back_to_previous")]
    ]
    return InlineKeyboardMarkup(keyboard)


def persona_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора характера"""
    current = get_user_persona(user_id) or "friendly"
    
    personas = [
        ("friendly", "😊 Общительный"),
        ("fun", "😂 Весёлый"),
        ("smart", "🧐 Умный"),
        ("strict", "😐 Строгий")
    ]
    
    keyboard = []
    for p_id, p_name in personas:
        mark = " ✅" if p_id == current else ""
        keyboard.append([InlineKeyboardButton(f"{p_name}{mark}", callback_data=f"set_persona:{p_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def style_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора стиля ответа"""
    current = get_user_style(user_id) or "steps"
    
    styles = [
        ("short", "📏 Коротко"),
        ("steps", "📋 По шагам"),
        ("detail", "📚 Подробно")
    ]
    
    keyboard = []
    for s_id, s_name in styles:
        mark = " ✅" if s_id == current else ""
        keyboard.append([InlineKeyboardButton(f"{s_name}{mark}", callback_data=f"set_style:{s_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def ai_lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора языка ответов ИИ"""
    current = get_user_ai_lang(user_id) or "ru"
    
    languages = [
        ("ru", "🇷🇺 Русский"),
        ("en", "🇬🇧 English"),
        ("kk", "🇰🇿 Қазақша"),
        ("tr", "🇹🇷 Türkçe"),
        ("uk", "🇺🇦 Українська"),
        ("fr", "🇫🇷 Français")
    ]
    
    keyboard = []
    row = []
    for i, (lang_id, lang_name) in enumerate(languages):
        mark = " ✅" if lang_id == current else ""
        row.append(InlineKeyboardButton(f"{lang_name}{mark}", callback_data=f"set_ai_lang:{lang_id}"))
        if len(row) == 2 or i == len(languages) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора языка интерфейса"""
    current = get_user_lang(user_id) or "ru"
    
    languages = [
        ("ru", "🇷🇺 Русский"),
        ("en", "🇬🇧 English"),
        ("kk", "🇰🇿 Қазақша"),
        ("tr", "🇹🇷 Türkçe"),
        ("uk", "🇺🇦 Українська"),
        ("fr", "🇫🇷 Français")
    ]
    
    keyboard = []
    row = []
    for i, (lang_id, lang_name) in enumerate(languages):
        mark = " ✅" if lang_id == current else ""
        row.append(InlineKeyboardButton(f"{lang_name}{mark}", callback_data=f"set_lang:{lang_id}"))
        if len(row) == 2 or i == len(languages) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def stars_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с пакетами звезд"""
    from payments import get_packages
    keyboard = []
    packages = get_packages()
    
    for p in packages:
        stars = p["stars"]
        price = f"${p['price_usd']:.2f}"
        discount = f" 🔥 -{p['discount']}%" if p['discount'] > 0 else ""
        popular = " ⭐" if p.get('popular', False) else ""
        
        btn_text = f"{stars} ⭐ – {price}{discount}{popular}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_stars:{p['id']}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================
def main_menu_for_user(user_id: int) -> InlineKeyboardMarkup:
    from api import get_access
    a = get_access(user_id) if user_id else {"is_free": False, "is_blocked": False}
    balance = get_balance(user_id)
    use_mini_app = get_use_mini_app(user_id)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton("⛔ Доступ заблокирован", callback_data="tab:blocked")])
        return InlineKeyboardMarkup(keyboard)

    # Баланс звезд
    keyboard.append([InlineKeyboardButton(f"⭐ Баланс: {balance} звезд", callback_data="tab:balance")])

    # Кнопки в зависимости от режима
    if use_mini_app:
        can_open_miniapp = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        
        if can_open_miniapp:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            if balance < 1:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_stars")])
            else:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_pay")])
    else:
        can_use_chat = (balance >= 1 or a.get("is_free"))
        
        if can_use_chat:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="inline_chat")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="inline_image")])
        else:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="tab:need_stars")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="tab:need_stars")])

    # Кнопка покупки звезд
    keyboard.append([InlineKeyboardButton("⭐ Купить звезды", callback_data="tab:buy_stars")])

    # Нижние кнопки
    keyboard.append([
        InlineKeyboardButton("⚙️ Настройки", callback_data="tab:settings"),
        InlineKeyboardButton("❓ Помощь", callback_data="tab:help"),
    ])
    keyboard.append([
        InlineKeyboardButton("👤 Профиль", callback_data="tab:profile"),
        InlineKeyboardButton("📌 Статус", callback_data="tab:status"),
    ])
    keyboard.append([
        InlineKeyboardButton("🎁 Рефералы", callback_data="tab:ref"),
        InlineKeyboardButton("💬 Поддержка", callback_data="tab:support"),
    ])

    return InlineKeyboardMarkup(keyboard)