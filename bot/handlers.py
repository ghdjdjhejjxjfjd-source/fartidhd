# bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes

from api import get_access, set_last_menu
from bot.config import send_log_http, build_start_log
from bot.ui.keyboards import main_menu, back_button, buy_menu_keyboard, help_keyboard, settings_keyboard, tools_keyboard
from bot.modes import chat_mode, image_mode, tools_mode

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка /start"""
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id
    
    await send_main_menu(update, context, uid)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Отправить главное меню"""
    text = "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=main_menu(uid))
        set_last_menu(uid, uid, update.callback_query.message.message_id)
    else:
        msg = await update.effective_message.reply_text(text, reply_markup=main_menu(uid))
        set_last_menu(uid, uid, msg.message_id)

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех callback кнопок"""
    query = update.callback_query
    data = query.data
    
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    # Проверка на блокировку
    a = get_access(uid)
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    # ===== НАВИГАЦИЯ =====
    if data == "back_to_menu":
        await send_main_menu(update, context, uid)
        return
    
    # ===== БАЛАНС =====
    if data == "balance":
        from payments import get_balance
        balance = get_balance(uid)
        await query.message.edit_text(
            f"💰 Твой баланс: {balance} ⭐\n\n"
            f"💬 Чат: 1 ⭐\n"
            f"🖼 Картинка: 2 ⭐\n"
            f"🔧 Инструменты: от 1 ⭐",
            reply_markup=back_button()
        )
        return
    
    # ===== РЕЖИМЫ =====
    if data == "mode:chat":
        await chat_mode.start(update, context)
        return
        
    if data == "mode:image":
        await image_mode.start(update, context)
        return
        
    if data == "mode:tools":
        await query.message.edit_text(
            "🔧 Выбери инструмент:",
            reply_markup=tools_keyboard(uid)
        )
        return
    
    # ===== ИНСТРУМЕНТЫ =====
    if data.startswith("tool:"):
        tool_id = data.split(":")[1]
        await tools_mode.handle_tool(update, context, tool_id)
        return
    
    # ===== ПОКУПКА ЗВЕЗД =====
    if data == "buy_menu":
        await query.message.edit_text(
            "⭐ Выбери пакет звезд:",
            reply_markup=buy_menu_keyboard()
        )
        return
    
    if data.startswith("buy:"):
        package_id = data.split(":")[1]
        from payments import get_package
        package = get_package(package_id)
        if package:
            await query.message.edit_text(
                f"✅ Пакет {package['name']}\n"
                f"⭐ {package['stars']} звезд\n"
                f"💰 ${package['price_usd']}\n\n"
                f"Оплата через Telegram Stars скоро будет доступна!",
                reply_markup=back_button()
            )
        else:
            await query.message.edit_text("❌ Пакет не найден", reply_markup=back_button())
        return
    
    # ===== ПОМОЩЬ =====
    if data == "help":
        await query.message.edit_text("❓ Помощь", reply_markup=help_keyboard())
        return
    
    if data.startswith("help:"):
        section = data.split(":")[1]
        texts = {
            "faq": "📚 **FAQ**\n\n1. Как начать?\n   Нажми /start\n\n2. Сколько стоит?\n   Чат: 1⭐\n   Картинка: 2⭐\n\n3. Как пополнить?\n   Нажми ⭐ Купить звезды",
            "support": "💬 **Поддержка**\n\nПо всем вопросам пиши:\n@instagroq_support",
            "about": "ℹ️ **О боте**\n\nInstaGroq AI v3.0\n\n• Быстрый ИИ (Groq)\n• Качественный ИИ (OpenAI)\n• Генерация картинок\n• 6 полезных инструментов"
        }
        await query.message.edit_text(
            texts.get(section, "Раздел в разработке"),
            reply_markup=back_button(),
            parse_mode="Markdown"
        )
        return
    
    # ===== НАСТРОЙКИ =====
    if data == "settings":
        await query.message.edit_text("⚙️ Настройки", reply_markup=settings_keyboard(uid))
        return
    
    if data.startswith("settings:"):
        section = data.split(":")[1]
        await query.message.edit_text(
            f"⚙️ Настройки {section}\n\nСкоро будет доступно!",
            reply_markup=back_button()
        )
        return
    
    if data == "need_stars":
        await query.message.edit_text(
            "❌ Недостаточно звезд!\n\nКупи звезды в меню: ⭐ Купить звезды",
            reply_markup=back_button()
        )
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    uid = user.id
    text = update.message.text
    
    # Проверка на блокировку
    a = get_access(uid)
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    mode = context.user_data.get("mode")
    
    if mode == "chat":
        await chat_mode.handle_message(update, context, text)
    elif mode == "image":
        await image_mode.handle_message(update, context, text)
    elif mode and mode.startswith("tool_"):
        await tools_mode.handle_text(update, context, text)
    else:
        await send_main_menu(update, context, uid)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото"""
    user = update.effective_user
    uid = user.id
    mode = context.user_data.get("mode")
    
    if mode and mode.startswith("tool_"):
        await tools_mode.handle_photo(update, context)
    else:
        await update.message.reply_text("Отправь текст или выбери режим в меню")