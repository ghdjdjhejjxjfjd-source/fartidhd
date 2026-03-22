# bot/menu.py - ПОЛНАЯ ВЕРСИЯ С ЛОКАЛИЗАЦИЕЙ
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from api import get_use_mini_app, get_user_persona, get_user_lang, get_user_ai_lang, get_user_style, get_ai_mode, get_user_limits
from payments import get_balance
from .config import MINIAPP_URL, is_valid_https_url
from datetime import datetime
from .helpers import format_balance
from .locales import get_text  # ← импортируем функцию локализации
from bot.support import support_blocks


def tab_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")]])


def settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    limits = get_user_limits(user_id)
    
    keyboard = []
    
    if not use_mini_app:
        if ai_mode == "fast":
            keyboard.append([InlineKeyboardButton(get_text(user_id, "ai_lang_settings"), callback_data="tab:ai_lang_settings")])
        
        if ai_mode == "fast":
            used = limits.get("groq_persona", 0)
            max_limit = 5
            remaining = max_limit - used
            btn_text = f"🎭 {get_text(user_id, 'persona_settings')} ({remaining}/{max_limit})"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:persona_settings")])
        
        if ai_mode == "fast":
            used = limits.get("groq_style", 0)
            max_limit = 5
        else:
            used = limits.get("openai_style", 0)
            max_limit = 7
        remaining = max_limit - used
        btn_text = f"📝 {get_text(user_id, 'style_settings')} ({remaining}/{max_limit})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:style_settings")])
        
        used = limits.get("ai_mode_changes", 0)
        max_limit = 8
        remaining = max_limit - used
        btn_text = f"⚡ {get_text(user_id, 'ai_mode_settings')} ({remaining}/{max_limit})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:ai_mode_settings")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "mode_settings"), callback_data="tab:mode_settings")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "lang_settings"), callback_data="tab:lang_settings")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    
    return InlineKeyboardMarkup(keyboard)


def mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора режима работы"""
    use_mini_app = get_use_mini_app(user_id)
    
    keyboard = []
    if use_mini_app:
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'mode_miniapp')}", callback_data="ignore")])
        keyboard.append([InlineKeyboardButton(get_text(user_id, 'mode_inline'), callback_data="switch_to_inline")])
    else:
        keyboard.append([InlineKeyboardButton(get_text(user_id, 'mode_miniapp'), callback_data="switch_to_miniapp")])
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'mode_inline')}", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def ai_mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора режима ИИ"""
    current = get_ai_mode(user_id) or "fast"
    limits = get_user_limits(user_id)
    used = limits.get("ai_mode_changes", 0)
    
    keyboard = []
    
    if current == "fast":
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'ai_mode_fast')}", callback_data="ignore")])
        if used < 8:
            keyboard.append([InlineKeyboardButton(get_text(user_id, 'ai_mode_quality'), callback_data="confirm_ai_mode:quality")])
        else:
            keyboard.append([InlineKeyboardButton(f"{get_text(user_id, 'ai_mode_quality')} (лимит)", callback_data="limit_exceeded")])
    else:
        if used < 8:
            keyboard.append([InlineKeyboardButton(get_text(user_id, 'ai_mode_fast'), callback_data="confirm_ai_mode:fast")])
        else:
            keyboard.append([InlineKeyboardButton(f"{get_text(user_id, 'ai_mode_fast')} (лимит)", callback_data="limit_exceeded")])
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'ai_mode_quality')}", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def confirm_ai_mode_kb(user_id: int, new_mode: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения смены режима"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "confirm_yes"), callback_data=f"execute_ai_mode:{new_mode}")],
        [InlineKeyboardButton(get_text(user_id, "confirm_no"), callback_data="back_to_previous")]
    ]
    return InlineKeyboardMarkup(keyboard)


def persona_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора характера"""
    current = get_user_persona(user_id) or "friendly"
    limits = get_user_limits(user_id)
    used = limits.get("groq_persona", 0)
    
    personas = [
        ("friendly", get_text(user_id, "persona_friendly")),
        ("fun", get_text(user_id, "persona_fun")),
        ("smart", get_text(user_id, "persona_smart")),
        ("strict", get_text(user_id, "persona_strict"))
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
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def style_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора стиля ответа"""
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
        ("short", get_text(user_id, "style_short")),
        ("steps", get_text(user_id, "style_steps")),
        ("detail", get_text(user_id, "style_detail"))
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
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def ai_lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора языка ответов ИИ"""
    current = get_user_ai_lang(user_id) or "ru"
    
    languages = [
        ("ru", get_text(user_id, "lang_ru")),
        ("en", get_text(user_id, "lang_en")),
        ("kk", get_text(user_id, "lang_kk")),
        ("tr", get_text(user_id, "lang_tr")),
        ("uk", get_text(user_id, "lang_uk")),
        ("fr", get_text(user_id, "lang_fr"))
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
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора языка интерфейса"""
    current = get_user_lang(user_id) or "ru"
    
    languages = [
        ("ru", get_text(user_id, "lang_ru")),
        ("en", get_text(user_id, "lang_en")),
        ("kk", get_text(user_id, "lang_kk")),
        ("tr", get_text(user_id, "lang_tr")),
        ("uk", get_text(user_id, "lang_uk")),
        ("fr", get_text(user_id, "lang_fr"))
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
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
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
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def main_menu_for_user(user_id: int) -> InlineKeyboardMarkup:
    """Главное меню"""
    from api import get_access
    a = get_access(user_id) if user_id else {"is_free": False, "is_blocked": False}
    balance = get_balance(user_id)
    formatted_balance = format_balance(balance)
    use_mini_app = get_use_mini_app(user_id)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton(get_text(user_id, "blocked"), callback_data="tab:blocked")])
        return InlineKeyboardMarkup(keyboard)

    keyboard.append([InlineKeyboardButton(get_text(user_id, "balance_btn").format(balance=formatted_balance), callback_data="tab:balance")])

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
            keyboard.append([InlineKeyboardButton(get_text(user_id, "chat_btn"), callback_data="inline_chat")])
            keyboard.append([InlineKeyboardButton(get_text(user_id, "image_btn"), callback_data="inline_image")])
        else:
            keyboard.append([InlineKeyboardButton(get_text(user_id, "chat_btn"), callback_data="tab:need_stars_chat")])
            keyboard.append([InlineKeyboardButton(get_text(user_id, "image_btn"), callback_data="tab:need_stars_chat")])

    keyboard.append([InlineKeyboardButton(get_text(user_id, "buy_stars_btn"), callback_data="tab:buy_stars")])

    bottom_row1 = []
    bottom_row1.append(InlineKeyboardButton(get_text(user_id, "settings_btn"), callback_data="tab:settings"))
    bottom_row1.append(InlineKeyboardButton(get_text(user_id, "help_btn"), callback_data="tab:help"))
    keyboard.append(bottom_row1)
    
    bottom_row2 = []
    bottom_row2.append(InlineKeyboardButton(get_text(user_id, "profile_btn"), callback_data="tab:profile"))
    bottom_row2.append(InlineKeyboardButton(get_text(user_id, "status_btn"), callback_data="tab:status"))
    keyboard.append(bottom_row2)
    
    bottom_row3 = []
    bottom_row3.append(InlineKeyboardButton(get_text(user_id, "referral_btn"), callback_data="tab:ref"))
    
    is_support_blocked = False
    if user_id in support_blocks:
        if datetime.now() < support_blocks[user_id]:
            is_support_blocked = True
    
    if is_support_blocked:
        bottom_row3.append(InlineKeyboardButton(get_text(user_id, "support_blocked"), callback_data="tab:support_blocked"))
    else:
        bottom_row3.append(InlineKeyboardButton(get_text(user_id, "support_btn"), callback_data="tab:support"))
    
    keyboard.append(bottom_row3)

    return InlineKeyboardMarkup(keyboard)