# bot/modes/tools_mode.py
from telegram import Update
from telegram.ext import ContextTypes
from api import get_access
from payments import get_balance, spend_stars

async def handle_tool(update: Update, context: ContextTypes.DEFAULT_TYPE, tool_id: str):
    query = update.callback_query
    user = update.effective_user
    uid = user.id
    
    costs = {"remove_bg": 2, "ocr": 1, "meme": 1, "qr": 1}
    names = {"remove_bg": "Удаление фона", "ocr": "Текст с фото", "meme": "Создание мемов", "qr": "QR код"}
    
    cost = costs.get(tool_id, 1)
    a = get_access(uid)
    balance = get_balance(uid)
    
    if not a.get("is_free") and balance < cost:
        await query.message.reply_text(f"❌ Нужно {cost}⭐. У тебя {balance}⭐")
        return
    
    context.user_data["mode"] = f"tool_{tool_id}"
    context.user_data["tool_cost"] = cost
    
    instructions = {
        "remove_bg": "📸 Отправь фото, удалю фон",
        "ocr": "📝 Отправь фото с текстом",
        "meme": "🎭 Отправь фото для мема и напиши текст",
        "qr": "📱 Напиши текст или ссылку"
    }
    
    await query.message.reply_text(f"{instructions.get(tool_id)} (💰 {cost}⭐)")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Фото получено. Обрабатываю...")
    # TODO: добавить логику

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    mode = context.user_data.get("mode")
    if mode == "tool_qr":
        await update.message.reply_text(f"✅ QR код для: {text}\n(скоро)")
    else:
        await update.message.reply_text("ℹ️ Отправь фото")