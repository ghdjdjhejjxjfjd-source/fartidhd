from telegram import Update
from telegram.ext import ContextTypes
from api import set_user_lang, set_user_persona
from bot.ui.keyboards import settings_keyboard, back_button

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    query = update.callback_query
    await query.message.edit_text("⚙️ **Настройки**\n\nВыбери что хочешь изменить:", 
                                  reply_markup=settings_keyboard(), 
                                  parse_mode="Markdown")

async def handle_lang(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    query = update.callback_query
    data = query.data
    
    if data == "lang_ru":
        set_user_lang(uid, "ru")
        await query.message.edit_text("✅ Язык изменен на 🇷🇺 Русский", reply_markup=back_button())
    elif data == "lang_en":
        set_user_lang(uid, "en")
        await query.message.edit_text("✅ Language changed to 🇬🇧 English", reply_markup=back_button())
    elif data == "lang_kk":
        set_user_lang(uid, "kk")
        await query.message.edit_text("✅ Тіл ауыстырылды 🇰🇿 Қазақша", reply_markup=back_button())

async def handle_persona(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    query = update.callback_query
    data = query.data
    
    personas = {
        "persona_friendly": ("friendly", "😊 Общительный"),
        "persona_fun": ("fun", "😂 Весёлый"),
        "persona_smart": ("smart", "🧐 Умный"),
        "persona_strict": ("strict", "😐 Строгий")
    }
    
    if data in personas:
        persona_id, persona_name = personas[data]
        set_user_persona(uid, persona_id)
        await query.message.edit_text(f"✅ Характер изменен на {persona_name}", reply_markup=back_button())