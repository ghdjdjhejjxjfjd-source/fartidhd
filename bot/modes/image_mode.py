# bot/modes/image_mode.py
from telegram import Update
from telegram.ext import ContextTypes
import base64

from api import get_access, increment_images, add_stars_spent
from payments import get_balance, spend_stars
from stability_client import generate_image
from bot.config import send_log_http

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск режима генерации картинок"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < 2:
        await query.message.reply_text(
            "❌ Недостаточно звезд (нужно 2).\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await query.message.reply_text(
        "🖼 Отправь описание картинки.\n"
        "Например: 'красивый закат в горах'\n\n"
        "Для отмены напиши /cancel"
    )
    
    context.user_data["mode"] = "image"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """Обработка генерации картинки"""
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    
    await update.message.reply_text("🎨 Генерирую картинку... (до 30 секунд)")
    
    try:
        image_base64 = generate_image(prompt)
        image_data = base64.b64decode(image_base64.split(",")[1])
        
        await update.message.reply_photo(
            photo=image_data,
            caption=f"🖼 Промпт: {prompt}"
        )
        
        # Обновляем статистику
        increment_images(uid)
        
        # Списываем звезды
        if not a.get("is_free"):
            spend_stars(uid, 2)
            add_stars_spent(uid, 2)
        
        send_log_http(f"🖼 Генерация: {uid} -> {prompt[:50]}...")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка генерации: {e}")