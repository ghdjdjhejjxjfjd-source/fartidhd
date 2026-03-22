# bot/menu.py - РАБОЧАЯ ВЕРСИЯ С TAB_TEXT
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from api import get_use_mini_app, get_user_persona, get_user_lang, get_user_ai_lang, get_user_style, get_ai_mode, get_user_limits
from payments import get_balance
from .config import MINIAPP_URL, is_valid_https_url
from datetime import datetime
from .helpers import format_balance
from bot.support import support_blocks


# =========================
# ТЕКСТЫ МЕНЮ (РУССКИЙ)
# =========================
TAB_TEXT = {
    "blocked": "⛔ Доступ заблокирован.\n\nЕсли ты считаешь это ошибкой — напиши админу.",
    "need_pay": "💰 Чтобы открыть Mini App, нужно купить пакет.\n\nОплату подключим позже.",
    "need_stars": "⭐ Для доступа к Mini App нужна хотя бы 1 звезда.\n\nКупите пакет звезд ниже 👇",
    "need_stars_chat": "⭐ Недостаточно звезд для чата с ИИ.\n\nКупите звезды в меню ниже 👇",
    "need_stars_miniapp": "⭐ Недостаточно звезд для Mini App.\n\nКупите звезды в меню ниже 👇",
    "buy_pack": "💰 Купить пакет\n\nПакеты сообщений (пример):\n• 100 сообщений — 99₽\n• 500 сообщений — 399₽\n• 2000 сообщений — 999₽\n\nОплату подключим позже.",
    "settings": "⚙️ Настройки\n\nВыбери раздел:",
    "help": "❓ Помощь\n\nНажми «Открыть Mini App» или используй встроенный чат.",
    "profile": "        👤 ПРОФИЛЬ\n\nНик: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Сообщений: {messages}\n🎨 Картинок: {images}\n💸 Потрачено: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ ТЕКУЩЕЕ\n🌐 Язык: {lang}\n📱 Режим: {mode}\n🤖 ИИ: {ai_mode}",
    "status": "📌 Статус\n\nРаздел в разработке.",
    "ref": "🎁 Рефералы\n\nРаздел в разработке.",
    "support": "💬 Поддержка\n\nНапиши свой вопрос.",
    "support_blocked": "⛔ Поддержка заблокирована",
    "faq": "📚 FAQ\n\nРаздел в разработке.",
    "about": "ℹ️ О проекте\n\nРаздел в разработке.",
    "buy_stars": "⭐ Пакеты звезд\n\nВыберите пакет для пополнения:",
    "balance": "⭐ Ваш баланс звезд",
    "mode_settings": "🔄 Режим работы\n\nВыбери как пользоваться ботом:",
    "persona_settings": "🎭 Характер ИИ\n\nВыбери как ИИ будет отвечать:",
    "style_settings": "📝 Стиль ответа\n\nВыбери стиль ответов ИИ:",
    "lang_settings": "🌐 Язык интерфейса\n\nВыбери язык меню и кнопок:",
    "ai_lang_settings": "🌐 Язык ответов ИИ\n\nВыбери на каком языке будет отвечать ИИ:",
    "ai_mode_settings": "⚡ Режим ИИ\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 БЫСТРЫЙ (0.3 ⭐)\n• Быстрые ответы\n• Можно менять характер, стиль и язык ответов\n\n💎 КАЧЕСТВЕННЫЙ (1 ⭐)\n• Глубокие ответы\n• Можно менять только стиль\n• Язык определяется автоматически\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Сегодня осталось смен режима: {changes_left}/8\n⏰ Сброс в 00:00",
    "confirm_ai_mode_change": "⚠️ ПОДТВЕРЖДЕНИЕ\n\nВы выбрали режим: {new_mode}\n\nТекущий режим: {current_mode}\n\nПри смене режима:\n• История чата будет полностью очищена\n• Все предыдущие сообщения удалятся\n\nПродолжить?",
    "limit_exceeded": "⛔ Лимит исчерпан\n\nСегодня больше нельзя менять эту настройку.\nПопробуй завтра после 00:00.",
    "inline_chat_start_fast": "💬 Напиши сообщение.\n\nРежим: {mode}\nЯзык ответов: {lang}\nСтиль: {style}\nСтоимость: {cost}⭐",
    "inline_chat_start_quality": "💬 Напиши сообщение.\n\nРежим: {mode}\nСтиль: {style}\nСтоимость: {cost}⭐",
    "image_start": "🖼 Напиши описание картинки.\nСтоимость: 10⭐",
    "insufficient_stars": "❌ Недостаточно звезд (нужно {cost}⭐).\nКупи звезды в меню: ⭐ Купить звезды",
    "blocked_access": "⛔ Доступ заблокирован.",
    "generating": "🎨 Генерирую...",
    "error": "❌ Ошибка: {error}",
    "back_btn": "⬅️ Назад",
    "save_btn": "💾 Сохранить",
    "repeat_btn": "🔄 Повторить",
    "support_text": "💬 Поддержка\n\nОпиши свою проблему или вопрос в одном сообщении.\n\nАдмины ответят как можно скорее.\n\n⚠️ Принимаются только текстовые сообщения",
    "support_sent": "✅ Сообщение отправлено в поддержку.\nОжидайте ответа.",
    "support_blocked_msg": "⛔ Вы заблокированы в поддержке.\nОсталось: {hours}ч {minutes}мин",
    "support_only_text": "❌ В поддержку можно отправлять только текстовые сообщения.",
    "support_error": "❌ Ошибка при отправке. Попробуйте позже.",
    "setting_changed": "✅ Настройка изменена",
    "persona_changed": "✅ Характер изменен на: {persona}",
    "style_changed": "✅ Стиль изменен на: {style}",
    "lang_changed": "✅ Язык изменен",
    "ai_lang_changed": "✅ Язык ответов ИИ изменен на: {lang}",
    "mode_changed": "✅ Режим работы переключен на {mode}!",
    "ai_mode_changed": "✅ Режим изменен на {mode}\n\n🧹 История чата очищена.\n📊 Сегодня осталось смен режима: {left}/8",
    "stars_added": "✨ Вам начислено {amount} звезд!\n💰 Текущий баланс: {balance} ⭐",
    "stars_bought": "✅ Вы выбрали пакет {name}\n⭐ {stars} звезд за ${price}",
    "package_not_found": "❌ Пакет не найден",
    "mode_miniapp": "📱 Mini App",
    "mode_inline": "💬 Встроенный",
    "ai_mode_fast": "🚀 Быстрый",
    "ai_mode_quality": "💎 Качественный",
    "persona_friendly": "😊 Общительный",
    "persona_fun": "😂 Весёлый",
    "persona_smart": "🧐 Умный",
    "persona_strict": "😐 Строгий",
    "style_short": "📏 Коротко",
    "style_steps": "📋 По шагам",
    "style_detail": "📚 Подробно",
    "lang_ru": "🇷🇺 Русский",
    "lang_en": "🇬🇧 English",
    "lang_kk": "🇰🇿 Қазақша",
    "lang_tr": "🇹🇷 Türkçe",
    "lang_uk": "🇺🇦 Українська",
    "lang_fr": "🇫🇷 Français",
    "confirm_yes": "✅ Да, сменить",
    "confirm_no": "❌ Нет, отмена",
}


# =========================
# ВСПОМОГАТЕЛЬНЫЕ КЛАВИАТУРЫ
# =========================
def tab_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")]])


def settings_kb(user_id: int) -> InlineKeyboardMarkup:
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    limits = get_user_limits(user_id)
    
    keyboard = []
    
    if not use_mini_app:
        if ai_mode == "fast":
            keyboard.append([InlineKeyboardButton("🌐 Язык ответов ИИ", callback_data="tab:ai_lang_settings")])
        
        if ai_mode == "fast":
            used = limits.get("groq_persona", 0)
            max_limit = 5
            remaining = max_limit - used
            btn_text = f"🎭 Характер ({remaining}/{max_limit})"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:persona_settings")])
        
        if ai_mode == "fast":
            used = limits.get("groq_style", 0)
            max_limit = 5
        else:
            used = limits.get("openai_style", 0)
            max_limit = 7
        remaining = max_limit - used
        btn_text = f"📝 Стиль ответа ({remaining}/{max_limit})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:style_settings")])
        
        used = limits.get("ai_mode_changes", 0)
        max_limit = 8
        remaining = max_limit - used
        btn_text = f"⚡ Режим ИИ ({remaining}/{max_limit})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:ai_mode_settings")])
    
    keyboard.append([InlineKeyboardButton("🔄 Режим работы", callback_data="tab:mode_settings")])
    keyboard.append([InlineKeyboardButton("🌐 Язык интерфейса", callback_data="tab:lang_settings")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    
    return InlineKeyboardMarkup(keyboard)


def mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
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
    current = get_ai_mode(user_id) or "fast"
    limits = get_user_limits(user_id)
    used = limits.get("ai_mode_changes", 0)
    
    keyboard = []
    
    if current == "fast":
        keyboard.append([InlineKeyboardButton("✅ 🚀 Быстрый", callback_data="ignore")])
        if used < 8:
            keyboard.append([InlineKeyboardButton("💎 Качественный", callback_data="confirm_ai_mode:quality")])
        else:
            keyboard.append([InlineKeyboardButton("💎 Качественный (лимит)", callback_data="limit_exceeded")])
    else:
        if used < 8:
            keyboard.append([InlineKeyboardButton("🚀 Быстрый", callback_data="confirm_ai_mode:fast")])
        else:
            keyboard.append([InlineKeyboardButton("🚀 Быстрый (лимит)", callback_data="limit_exceeded")])
        keyboard.append([InlineKeyboardButton("✅ 💎 Качественный", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def confirm_ai_mode_kb(user_id: int, new_mode: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("✅ Да, сменить", callback_data=f"execute_ai_mode:{new_mode}")],
        [InlineKeyboardButton("❌ Нет, отмена", callback_data="back_to_previous")]
    ]
    return InlineKeyboardMarkup(keyboard)


def persona_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    current = get_user_persona(user_id) or "friendly"
    limits = get_user_limits(user_id)
    used = limits.get("groq_persona", 0)
    
    personas = [
        ("friendly", "😊 Общительный"),
        ("fun", "😂 Весёлый"),
        ("smart", "🧐 Умный"),
        ("strict", "😐 Строгий")
    ]
    
    keyboard = []
    for p_id, p_name in personas:
        if p_id == current:
            keyboard.append([InlineKeyboardButton(f"✅ {p_name}", callback_data="ignore")])
        else:
            if used < 5:
                keyboard.append([InlineKeyboardButton(p_name, callback_data=f"set_persona:{p_id}")])
            else:
                keyboard.append([InlineKeyboardButton(f"{p_name} (лимит)", callback_data="limit_exceeded")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def style_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    current = get_user_style(user_id) or "steps"
    ai_mode = get_ai_mode(user_id)
    limits = get_user_limits(user_id)
    
    if ai_mode == "fast":
        used = limits.get("groq_style", 0)
        max_limit = 5
    else:
        used = limits.get("openai_style", 0)
        max_limit = 7
    
    styles = [
        ("short", "📏 Коротко"),
        ("steps", "📋 По шагам"),
        ("detail", "📚 Подробно")
    ]
    
    keyboard = []
    for s_id, s_name in styles:
        if s_id == current:
            keyboard.append([InlineKeyboardButton(f"✅ {s_name}", callback_data="ignore")])
        else:
            if used < max_limit:
                keyboard.append([InlineKeyboardButton(s_name, callback_data=f"set_style:{s_id}")])
            else:
                keyboard.append([InlineKeyboardButton(f"{s_name} (лимит)", callback_data="limit_exceeded")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def ai_lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
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
        if lang_id == current:
            row.append(InlineKeyboardButton(f"✅ {lang_name}", callback_data="ignore"))
        else:
            row.append(InlineKeyboardButton(lang_name, callback_data=f"set_ai_lang:{lang_id}"))
        if len(row) == 2 or i == len(languages) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
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
        if lang_id == current:
            row.append(InlineKeyboardButton(f"✅ {lang_name}", callback_data="ignore"))
        else:
            row.append(InlineKeyboardButton(lang_name, callback_data=f"set_lang:{lang_id}"))
        if len(row) == 2 or i == len(languages) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def stars_kb(user_id: int) -> InlineKeyboardMarkup:
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
    formatted_balance = format_balance(balance)
    use_mini_app = get_use_mini_app(user_id)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton("⛔ Доступ заблокирован", callback_data="tab:blocked")])
        return InlineKeyboardMarkup(keyboard)

    keyboard.append([InlineKeyboardButton(f"⭐ Баланс: {formatted_balance} звезд", callback_data="tab:balance")])

    if use_mini_app:
        can_open_miniapp = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        
        if can_open_miniapp:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            if balance < 1:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_stars_miniapp")])
            else:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_pay")])
    else:
        can_use_chat = (balance >= 1 or a.get("is_free"))
        
        if can_use_chat:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="inline_chat")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="inline_image")])
        else:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="tab:need_stars_chat")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="tab:need_stars_chat")])

    keyboard.append([InlineKeyboardButton("⭐ Купить звезды", callback_data="tab:buy_stars")])

    bottom_row1 = []
    bottom_row1.append(InlineKeyboardButton("⚙️ Настройки", callback_data="tab:settings"))
    bottom_row1.append(InlineKeyboardButton("❓ Помощь", callback_data="tab:help"))
    keyboard.append(bottom_row1)
    
    bottom_row2 = []
    bottom_row2.append(InlineKeyboardButton("👤 Профиль", callback_data="tab:profile"))
    bottom_row2.append(InlineKeyboardButton("📌 Статус", callback_data="tab:status"))
    keyboard.append(bottom_row2)
    
    bottom_row3 = []
    bottom_row3.append(InlineKeyboardButton("🎁 Рефералы", callback_data="tab:ref"))
    
    is_support_blocked = False
    if user_id in support_blocks:
        if datetime.now() < support_blocks[user_id]:
            is_support_blocked = True
    
    if is_support_blocked:
        bottom_row3.append(InlineKeyboardButton("⛔ Поддержка", callback_data="tab:support_blocked"))
    else:
        bottom_row3.append(InlineKeyboardButton("💬 Поддержка", callback_data="tab:support"))
    
    keyboard.append(bottom_row3)

    return InlineKeyboardMarkup(keyboard)