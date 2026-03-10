from telegram import Update
from telegram.ext import ContextTypes
from bot.ui.keyboards import back_button

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    query = update.callback_query
    await query.message.edit_text(
        "🔧 **Инструменты**\n\n"
        "Все инструменты доступны в Mini App:\n"
        "• 📸 Удаление фона\n"
        "• 📝 Текст с фото\n"
        "• 🎭 Создание мемов\n"
        "• 🎵 Music Lab\n"
        "• 📱 QR коды\n\n"
        "Нажми **🚀 Открыть Mini App** в главном меню",
        reply_markup=back_button(),
        parse_mode="Markdown"
    )