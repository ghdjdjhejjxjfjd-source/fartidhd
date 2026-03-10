from telegram import Update
from telegram.ext import ContextTypes
from api import get_access, set_last_menu
from bot.config import send_log_http, build_start_log
from bot.ui.keyboards import main_menu, back_button
from bot.modes import chat, image, profile, settings, tools

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))
    user = update.effective_user
    await send_main_menu(update, context, user.id)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    text = "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇"
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
    
    if data == "back_to_menu":
        await send_main_menu(update, context, uid)
    
    elif data == "profile":
        await profile.show(update, context, uid)
    
    elif data == "chat":
        await chat.start(update, context)
    
    elif data == "image":
        await image.start(update, context)
    
    elif data == "tools":
        await tools.show_menu(update, context, uid)
    
    elif data == "settings":
        await settings.show_menu(update, context, uid)
    
    elif data == "help":
        text = "❓ Помощь\n\nЧат с ИИ: 1⭐\nГенерация картинок: 2⭐\nИнструменты: от 1⭐\n\nПо вопросам: @instagroq_support"
        await query.message.edit_text(text, reply_markup=back_button())
    
    elif data == "need_stars":
        await query.message.edit_text("❌ Недостаточно звезд! Купи в меню.", reply_markup=back_button())
    
    elif data.startswith("lang_"):
        await settings.handle_lang(update, context, uid)
    
    elif data.startswith("persona_"):
        await settings.handle_persona(update, context, uid)
    
    elif data == "settings_lang":
        from bot.ui.keyboards import lang_keyboard
        await query.message.edit_text("🌐 Выбери язык:", reply_markup=lang_keyboard())
    
    elif data == "settings_persona":
        from bot.ui.keyboards import persona_keyboard
        await query.message.edit_text("🎭 Выбери характер:", reply_markup=persona_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    text = update.message.text
    mode = context.user_data.get("mode")
    
    if mode == "chat":
        await chat.handle_message(update, context, text)
    elif mode == "image":
        await image.handle_message(update, context, text)
    else:
        await send_main_menu(update, context, user.id)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode == "image":
        await image.handle_photo(update, context)
    else:
        await update.message.reply_text("Выбери режим генерации картинки в меню")