# bot/modes/tools_mode.py
from telegram import Update
from telegram.ext import ContextTypes

from api import get_access
from payments import get_balance, spend_stars
from bot.config import send_log_http

TOOLS = {
    "remove_bg": {"name": "Удаление фона", "cost": 2, "desc": "Отправь фото, удалю фон"},
    "ocr": {"name": "Текст с фото", "cost": 1, "desc": "Отправь фото с текстом"},
    "meme": {"name": "Создание мемов", "cost": 1, "desc": "Отправь фото для мема"},
    "music": {"name": "Music Lab", "cost": 2, "desc": "Создай музыку (скоро)"},
    "qr": {"name": "QR коды", "cost": 1, "desc": "Напиши текст для QR"},
}

async def handle_tool(update: Update, context: ContextTypes.DEFAULT_TYPE, tool_id: str):
    """Обработка выбора инструмента"""
    query = update.callback_query
    
    user = update.effective_user
    uid = user.id
    
    tool = TOOLS.get(tool_id)
    if not tool:
        await query.message.reply_text("❌ Инструмент не найден")
        return
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if not a.get("is_free") and balance < tool["cost"]:
        await query.message.reply_text(
            f"❌ Недостаточно звезд (нужно {tool['cost']})\n"
            f"💰 Твой баланс: {balance}⭐"
        )
        return
    
    context.user_data["mode"] = f"tool_{tool_id}"
    context.user_data["tool"] = tool
    context.user_data["tool_cost"] = tool["cost"]
    
    await query.message.reply_text(
        f"🔧 **{tool['name']}**\n\n{tool['desc']}\n\n"
        f"💰 Стоимость: {tool['cost']}⭐\n"
        f"Для отмены напиши /cancel",
        parse_mode="Markdown"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото для инструментов"""
    user = update.effective_user
    uid = user.id
    mode = context.user_data.get("mode")
    tool = context.user_data.get("tool")
    
    if not tool:
        return
    
    await update.message.reply_text(f"⏳ Обрабатываю {tool['name']}...")
    
    # TODO: Здесь будет логика каждого инструмента
    await update.message.reply_text("✅ Готово! (в разработке)")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обработка текста для инструментов"""
    user = update.effective_user
    uid = user.id
    mode = context.user_data.get("mode")
    tool = context.user_data.get("tool")
    
    if not tool:
        return
    
    if mode == "tool_qr":
        await update.message.reply_text(f"⏳ Создаю QR код...")
        # TODO: генерация QR
        await update.message.reply_text(f"✅ QR код для: {text}\n(в разработке)")
    else:
        await update.message.reply_text("ℹ️ Отправь фото, а не текст")