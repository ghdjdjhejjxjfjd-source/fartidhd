# bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from api import get_access, set_last_menu
from bot.config import send_log_http, build_start_log
from bot.ui.keyboards import main_menu, back_button, tools_keyboard
from bot.modes import chat_mode, image_mode, tools_mode

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))
    user = update.effective_user
    await send_main_menu(update, context, user.id)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    text = "🤖 InstaGroq AI\n\nВыбирай:"
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=main_menu(uid))
        set_last_menu(uid, uid, update.callback_query.message.message_id)
    else:
        msg = await update.effective_message.reply_text(text, reply_markup=main_menu(uid))
        set_last_menu(uid, uid, msg.message_id)

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    if get_access(uid).get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if data == "back":
        await send_main_menu(update, context, uid)
    elif data == "balance":
        from payments import get_balance
        bal = get_balance(uid)
        await query.message.edit_text(f"💰 Баланс: {bal} ⭐", reply_markup=back_button())
    elif data == "mode_chat":
        await chat_mode.start(update, context)
    elif data == "mode_image":
        await image_mode.start(update, context)
    elif data == "mode_tools":
        await query.message.edit_text("🔧 Инструменты:", reply_markup=tools_keyboard(uid))
    elif data.startswith("tool_"):
        await tools_mode.handle_tool(update, context, data.replace("tool_", ""))
    elif data == "need_stars":
        await query.message.edit_text("❌ Недостаточно звезд", reply_markup=back_button())
    elif data == "help":
        await query.message.edit_text("❓ Помощь\n\nЧат: 1⭐\nКартинка: 2⭐\nИнструменты: от 1⭐", reply_markup=back_button())
    elif data == "settings":
        await query.message.edit_text("⚙️ Настройки скоро", reply_markup=back_button())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user = update.effective_user
    text = update.message.text
    mode = context.user_data.get("mode")
    
    if mode == "chat":
        await chat_mode.handle_message(update, context, text)
    elif mode == "image":
        await image_mode.handle_message(update, context, text)
    elif mode and mode.startswith("tool_"):
        await tools_mode.handle_text(update, context, text)
    else:
        await send_main_menu(update, context, user.id)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode and mode.startswith("tool_"):
        await tools_mode.handle_photo(update, context)
    else:
        await update.message.reply_text("Выбери инструмент сначала")