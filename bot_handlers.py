# bot_handlers.py
import os
from datetime import datetime

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

from api import get_access, get_last_menu, set_last_menu, clear_last_menu, set_use_mini_app, get_use_mini_app, set_user_persona, get_user_persona
from payments import get_balance

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
MINIAPP_URL = (os.getenv("MINIAPP_URL") or "").strip()

# лог-группа: TARGET_GROUP_ID приоритет
GROUP_ID_RAW = (os.getenv("TARGET_GROUP_ID") or os.getenv("LOG_GROUP_ID") or "0").strip()
try:
    GROUP_ID = int(GROUP_ID_RAW)
except Exception:
    GROUP_ID = 0


def is_valid_https_url(url: str) -> bool:
    return url.startswith("https://") and len(url) > len("https://")


def send_log_http(text: str):
    if not BOT_TOKEN or not GROUP_ID:
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": GROUP_ID, "text": text},
            timeout=12,
        )
        if not r.ok:
            print("LOG ERROR:", r.status_code, r.text)
    except Exception as e:
        print("LOG ERROR:", e)


def build_start_log(update: Update) -> str:
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = (user.username or "—") if user else "—"
    full_name = f"{(user.first_name or '') if user else ''} {(user.last_name or '') if user else ''}".strip() or "—"

    chat_type = chat.type if chat else "—"
    chat_id = chat.id if chat else "—"
    text = (msg.text or "").strip() if msg else ""

    return (
        "🚀 /start\n"
        f"🕒 {time_str}\n"
        f"👤 {full_name} (@{username})\n"
        f"🆔 user_id: {user.id if user else '—'}\n"
        f"💬 chat_type: {chat_type}\n"
        f"🏷 chat_id: {chat_id}\n"
        f"✉️ text: {text}"
    )


# =========================
#   UI: MENU + TABS
# =========================
MENU_TEXT = "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇"

TAB_TEXT = {
    "blocked": "⛔ Доступ заблокирован.\n\nЕсли ты считаешь это ошибкой — напиши админу.",
    "need_pay": "💰 Чтобы открыть Mini App, нужно купить пакет.\n\nОплату подключим позже.",
    "need_stars": "⭐ Для доступа к Mini App нужна хотя бы 1 звезда.\n\nКупите пакет звезд ниже 👇",
    "buy_pack": "💰 Купить пакет\n\nПакеты сообщений (пример):\n• 100 сообщений — 99₽\n• 500 сообщений — 399₽\n• 2000 сообщений — 999₽\n\nОплату подключим позже.",
    "settings": "⚙️ Настройки\n\n• 🎭 Характер ИИ\n• 🔄 Режим работы",
    "help": "❓ Помощь\n\nНажми «Открыть Mini App» или используй встроенный чат.",
    "profile": "👤 Профиль\n\nРаздел в разработке.",
    "status": "📌 Статус\n\nРаздел в разработке.",
    "ref": "🎁 Рефералы\n\nРаздел в разработке.",
    "support": "💬 Поддержка\n\nРаздел в разработке.",
    "faq": "📚 FAQ\n\nРаздел в разработке.",
    "about": "ℹ️ О проекте\n\nРаздел в разработке.",
    "buy_stars": "⭐ Пакеты звезд\n\nВыберите пакет для пополнения:",
    "balance": "⭐ Ваш баланс звезд",
    "mode_settings": "🔄 Режим работы\n\nВыбери как пользоваться ботом:\n\n📱 Mini App — открывается веб-приложение\n💬 Встроенный — чат прямо в Telegram",
    "persona_settings": "🎭 Характер ИИ\n\nВыбери как ИИ будет отвечать:\n\n😊 Общительный — тёплый, со смайликами\n😂 Весёлый — шутливый, энергичный\n🧐 Умный — вдумчивый, с объяснениями\n😐 Строгий — коротко и по делу"
}


def tab_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]])


def mode_settings_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📱 Mini App", callback_data="switch_to_miniapp")],
        [InlineKeyboardButton("💬 Встроенный", callback_data="switch_to_inline")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def persona_settings_kb(current_persona: str = "friendly") -> InlineKeyboardMarkup:
    keyboard = []
    
    personas = [
        ("friendly", "😊 Общительный"),
        ("fun", "😂 Весёлый"),
        ("smart", "🧐 Умный"),
        ("strict", "😐 Строгий")
    ]
    
    for p_id, p_name in personas:
        mark = " ✅" if p_id == current_persona else ""
        keyboard.append([InlineKeyboardButton(f"{p_name}{mark}", callback_data=f"set_persona:{p_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)


def stars_kb() -> InlineKeyboardMarkup:
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
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)


def main_menu_for_user(user_id: int) -> InlineKeyboardMarkup:
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
        # Режим Mini App
        can_open_miniapp = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        
        if can_open_miniapp:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            if balance < 1:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_stars")])
            else:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_pay")])
    else:
        # Встроенный режим (чат в Telegram)
        can_use_chat = (balance >= 1 or a.get("is_free"))
        
        if can_use_chat:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="inline_chat")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="inline_image")])
        else:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="tab:need_stars")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="tab:need_stars")])

    # Кнопка покупки звезд
    keyboard.append([InlineKeyboardButton("⭐ Купить звезды", callback_data="tab:buy_stars")])

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


# =========================
#   MENU MESSAGE MANAGEMENT
# =========================
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


async def send_fresh_menu(bot, user_id: int, text: str):
    # удаляем предыдущее меню
    await delete_prev_menu(bot, user_id)

    # отправляем новое
    m = await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=main_menu_for_user(user_id),
    )
    set_last_menu(user_id, user_id, m.message_id)


async def update_user_menu(bot, user_id: int):
    """Принудительно обновить меню пользователя"""
    await send_fresh_menu(bot, user_id, MENU_TEXT)


async def send_block_notice(bot, user_id: int):
    # удаляем меню
    await delete_prev_menu(bot, user_id)

    # просто текст (без меню)
    await bot.send_message(chat_id=user_id, text="⛔ Доступ заблокирован.")


async def edit_to_menu(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    try:
        await query.message.edit_text(MENU_TEXT, reply_markup=main_menu_for_user(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id, MENU_TEXT)


async def edit_to_tab(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    text = TAB_TEXT.get(tab_key, "Раздел в разработке.")
    
    # Для баланса показываем актуальное значение
    if tab_key == "balance":
        balance = get_balance(user_id)
        text = f"⭐ Ваш баланс: {balance} звезд"
    
    # Для покупки звезд показываем специальную клавиатуру
    if tab_key == "buy_stars":
        reply_markup = stars_kb()
    elif tab_key == "mode_settings":
        reply_markup = mode_settings_kb()
    elif tab_key == "persona_settings":
        current = get_user_persona(user_id) or "friendly"
        reply_markup = persona_settings_kb(current)
    else:
        reply_markup = tab_kb()
    
    try:
        await query.message.edit_text(text, reply_markup=reply_markup)
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id, MENU_TEXT)


# =========================
#   INLINE CHAT HANDLERS
# =========================
async def inline_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало чата в Telegram"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < 1:
        await query.message.reply_text(
            "❌ Недостаточно звезд.\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await query.message.reply_text(
        "💬 Напиши сообщение для ИИ.\n"
        "Отправь текст, и я отвечу.\n\n"
        "Для отмены напиши /cancel"
    )
    
    # Запоминаем что пользователь в режиме чата
    context.user_data["in_chat_mode"] = True


async def inline_image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало генерации картинки в Telegram"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < 1:
        await query.message.reply_text(
            "❌ Недостаточно звезд.\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await query.message.reply_text(
        "🖼 Отправь описание картинки.\n"
        "Например: 'красивый закат в горах'\n\n"
        "Для отмены напиши /cancel"
    )
    
    # Запоминаем что пользователь в режиме генерации
    context.user_data["in_image_mode"] = True


# =========================
#   HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))

    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return

    await send_fresh_menu(context.bot, uid, MENU_TEXT)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = (query.data or "").strip()

    try:
        await query.answer()
    except Exception:
        pass

    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return

    # назад в меню
    if data == "back_to_menu":
        await edit_to_menu(context, query, uid)
        return

    # вкладки: tab:<key>
    if data.startswith("tab:"):
        key = data.split("tab:", 1)[1].strip()
        await edit_to_tab(context, query, uid, key)
        return

    # покупка звезд
    if data.startswith("buy_stars:"):
        package_id = data.split("buy_stars:", 1)[1].strip()
        from payments import get_package
        package = get_package(package_id)
        
        if package:
            stars = package["stars"]
            price = package["price_usd"]
            
            await query.message.edit_text(
                f"✅ Вы выбрали пакет {package['name']}\n"
                f"⭐ {stars} звезд за ${price}\n\n"
                f"Оплата через Telegram Stars будет доступна позже.\n"
                f"Сейчас это тестовый режим.",
                reply_markup=tab_kb()
            )
        else:
            await query.message.edit_text(
                "❌ Пакет не найден",
                reply_markup=tab_kb()
            )
        return

    # переключение режима
    if data == "switch_to_miniapp":
        confirm_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Да, переключить", callback_data="confirm_switch_to_miniapp")],
            [InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu")]
        ])
        await query.message.edit_text(
            "🔄 Переключиться на Mini App режим?\n\n"
            "В главном меню появится кнопка 'Открыть Mini App'.",
            reply_markup=confirm_kb
        )
        return

    if data == "switch_to_inline":
        confirm_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Да, переключить", callback_data="confirm_switch_to_inline")],
            [InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu")]
        ])
        await query.message.edit_text(
            "🔄 Переключиться на встроенный режим?\n\n"
            "Кнопки 'Открыть Mini App' заменятся на 'Чат с ИИ' и 'Генерация картинки'.\n"
            "Сможешь общаться прямо в Telegram.",
            reply_markup=confirm_kb
        )
        return

    # подтверждение переключения
    if data == "confirm_switch_to_miniapp":
        set_use_mini_app(uid, True)
        await query.message.edit_text(
            "✅ Режим переключен на Mini App!\n\n"
            "Теперь в главном меню будет кнопка 'Открыть Mini App'.",
            reply_markup=tab_kb()
        )
        # обновляем меню
        await update_user_menu(context.bot, uid)
        return

    if data == "confirm_switch_to_inline":
        set_use_mini_app(uid, False)
        await query.message.edit_text(
            "✅ Режим переключен на встроенный!\n\n"
            "Теперь в главном меню будут кнопки:\n"
            "💬 Чат с ИИ\n"
            "🖼 Генерация картинки",
            reply_markup=tab_kb()
        )
        # обновляем меню
        await update_user_menu(context.bot, uid)
        return

    # выбор характера
    if data.startswith("set_persona:"):
        persona = data.split("set_persona:", 1)[1].strip()
        set_user_persona(uid, persona)
        
        persona_names = {
            "friendly": "😊 Общительный",
            "fun": "😂 Весёлый",
            "smart": "🧐 Умный",
            "strict": "😐 Строгий"
        }
        
        await query.message.edit_text(
            f"✅ Характер изменен на: {persona_names.get(persona, persona)}",
            reply_markup=tab_kb()
        )
        return

    # inline чат
    if data == "inline_chat":
        await inline_chat_start(update, context)
        return

    # inline генерация
    if data == "inline_image":
        await inline_image_start(update, context)
        return

    await edit_to_menu(context, query, uid)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (для inline режима)"""
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    uid = user.id
    
    # Проверяем режим
    if not context.user_data.get("in_chat_mode") and not context.user_data.get("in_image_mode"):
        return
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        context.user_data.clear()
        return
    
    if not a.get("is_free") and balance < 1:
        await update.message.reply_text(
            "❌ Недостаточно звезд.\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        context.user_data.clear()
        return
    
    text = update.message.text
    
    if context.user_data.get("in_chat_mode"):
        # Отправляем в Groq
        await update.message.reply_text("🤔 Думаю...")
        
        try:
            from groq_client import ask_groq
            persona = get_user_persona(uid) or "friendly"
            reply = ask_groq(text, persona=persona)
            
            await update.message.reply_text(reply)
            
            # Списываем звезду если не FREE
            if not a.get("is_free"):
                from payments import spend_stars
                spend_stars(uid, 1)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
        
        # Выходим из режима
        context.user_data["in_chat_mode"] = False
        
    elif context.user_data.get("in_image_mode"):
        # Генерируем картинку
        await update.message.reply_text("🎨 Генерирую картинку...")
        
        try:
            from stability_client import generate_image
            image_base64 = generate_image(text)
            
            # Отправляем фото
            import base64
            image_data = base64.b64decode(image_base64.split(",")[1])
            
            await update.message.reply_photo(
                photo=image_data,
                caption=f"🖼 Промпт: {text}"
            )
            
            # Списываем звезду если не FREE
            if not a.get("is_free"):
                from payments import spend_stars
                spend_stars(uid, 1)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
        
        # Выходим из режима
        context.user_data["in_image_mode"] = False