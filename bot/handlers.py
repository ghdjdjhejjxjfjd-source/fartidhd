# bot/handlers.py - НОВАЯ ВЕРСИЯ
from telegram import Update
from telegram.ext import ContextTypes

from api import get_access, set_last_menu
from bot.config import send_log_http, build_start_log
from bot.ui.keyboards import main_menu
from bot.ui.texts import get_text

# Импортируем наши режимы
from bot.modes import chat_mode, image_mode, tools_mode

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка /start"""
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id
    
    # Отправляем главное меню
    await send_menu(update, context, uid)

async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Отправить главное меню"""
    if update.callback_query:
        await update.callback_query.message.edit_text(
            "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
            reply_markup=main_menu(uid)
        )
        set_last_menu(uid, uid, update.callback_query.message.message_id)
    else:
        msg = await update.effective_message.reply_text(
            "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
            reply_markup=main_menu(uid)
        )
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
        await send_menu(update, context, uid)
        return
    
    # ===== РЕЖИМЫ =====
    if data == "mode:chat":
        await chat_mode.start(update, context)
        return
        
    if data == "mode:image":
        await image_mode.start(update, context)
        return
        
    if data == "mode:tools":
        await tools_mode.show_menu(update, context)
        return
    
    # ===== ИНСТРУМЕНТЫ =====
    if data.startswith("tool:"):
        tool_id = data.split(":")[1]
        await tools_mode.handle_tool(update, context, tool_id)
        return
    
    # ===== НАСТРОЙКИ =====
    if data == "tab:settings":
        # TODO: добавить настройки
        await query.message.edit_text(
            "⚙️ Настройки\n\nСкоро будет...",
            reply_markup=main_menu(uid)
        )
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    uid = user.id
    text = update.message.text
    
    # Проверяем в каком режиме пользователь
    mode = context.user_data.get("mode")
    
    if mode == "chat":
        await chat_mode.handle_message(update, context, text)
        
    elif mode == "image":
        await image_mode.handle_message(update, context, text)
        
    elif mode and mode.startswith("tool_"):
        await tools_mode.handle_text(update, context, text)
        
    else:
        # Если не в режиме - отправляем в меню
        await send_menu(update, context, uid)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото"""
    user = update.effective_user
    uid = user.id
    mode = context.user_data.get("mode")
    
    if mode and mode.startswith("tool_"):
        await tools_mode.handle_photo(update, context)
    else:
        await update.message.reply_text("Отправь текст или выбери режим в меню")