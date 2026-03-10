# bot/modes/tools_mode.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from api import get_access
from payments import get_balance
from bot.config import send_log_http

# Список всех инструментов
TOOLS = [
    {"id": "remove_bg", "name": "📸 Удаление фона", "desc": "Удали фон с фото", "cost": 2},
    {"id": "ocr", "name": "📝 Текст с фото", "desc": "Распознай текст с картинки", "cost": 1},
    {"id": "meme", "name": "🎭 Создание мемов", "desc": "Сделай мем из фото", "cost": 1},
    {"id": "music", "name": "🎵 Music Lab", "desc": "Создай музыку", "cost": 2},
    {"id": "qr", "name": "📱 QR коды", "desc": "Создай QR код", "cost": 1},
]

def get_tools_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с инструментами"""
    a = get_access(user_id)
    balance = get_balance(user_id)
    
    keyboard = []
    
    for tool in TOOLS:
        # Проверяем можно ли использовать
        can_use = a.get("is_free") or balance >= tool["cost"]
        
        if can_use:
            btn_text = f"{tool['name']} ({tool['cost']}⭐)"
        else:
            btn_text = f"{tool['name']} ❌"
        
        keyboard.append([InlineKeyboardButton(
            btn_text,
            callback_data=f"tool:{tool['id']}" if can_use else "need_stars"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(keyboard)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню инструментов"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    text = "🔧 **Инструменты**\n\nВыбери что хочешь сделать:"
    
    await query.message.edit_text(
        text,
        reply_markup=get_tools_keyboard(uid),
        parse_mode="Markdown"
    )
    
    context.user_data["mode"] = "tools_menu"

async def handle_tool(update: Update, context: ContextTypes.DEFAULT_TYPE, tool_id: str):
    """Обработка выбранного инструмента"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    # Находим инструмент
    tool = next((t for t in TOOLS if t["id"] == tool_id), None)
    if not tool:
        await query.message.reply_text("❌ Инструмент не найден")
        return
    
    # Проверяем баланс
    a = get_access(uid)
    balance = get_balance(uid)
    
    if not a.get("is_free") and balance < tool["cost"]:
        await query.message.reply_text(
            f"❌ Недостаточно звезд (нужно {tool['cost']})\n"
            f"💰 Твой баланс: {balance}⭐\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    # Сохраняем контекст
    context.user_data["mode"] = f"tool_{tool_id}"
    context.user_data["tool"] = tool
    context.user_data["tool_cost"] = tool["cost"]
    
    # Отправляем инструкцию в зависимости от инструмента
    if tool_id == "remove_bg":
        await query.message.reply_text(
            "📸 **Удаление фона**\n\n"
            "Отправь мне фото, а я удалю фон.\n\n"
            f"💰 Стоимость: {tool['cost']}⭐\n"
            "Для отмены напиши /cancel"
        )
        
    elif tool_id == "ocr":
        await query.message.reply_text(
            "📝 **Текст с фото**\n\n"
            "Отправь фото с текстом, а я его распознаю.\n\n"
            f"💰 Стоимость: {tool['cost']}⭐\n"
            "Для отмены напиши /cancel"
        )
        
    elif tool_id == "meme":
        await query.message.reply_text(
            "🎭 **Создание мемов**\n\n"
            "Отправь фото для мема и напиши текст.\n\n"
            f"💰 Стоимость: {tool['cost']}⭐\n"
            "Для отмены напиши /cancel"
        )
        
    elif tool_id == "music":
        await query.message.reply_text(
            "🎵 **Music Lab**\n\n"
            "Скоро будет доступно!\n"
            "Пока можно попробовать в Mini App."
        )
        
    elif tool_id == "qr":
        await query.message.reply_text(
            "📱 **QR коды**\n\n"
            "Напиши текст или ссылку, я создам QR код.\n\n"
            f"💰 Стоимость: {tool['cost']}⭐\n"
            "Для отмены напиши /cancel"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото для инструментов"""
    # TODO: реализовать обработку фото
    await update.message.reply_text("⏳ В разработке...")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обработка текста для инструментов"""
    mode = context.user_data.get("mode", "")
    
    if mode == "tool_qr":
        # Создаем QR код
        await update.message.reply_text("⏳ Генерация QR кода...")
        # TODO: интеграция с qr.html через API
    else:
        await update.message.reply_text("⏳ В разработке...")