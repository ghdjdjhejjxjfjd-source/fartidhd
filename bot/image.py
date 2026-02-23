from telegram import Update
from telegram.ext import ContextTypes
import base64

from api import get_access
from payments import get_balance, spend_stars
from stability_client import generate_image
from .config import send_log_http


async def inline_image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало генерации картинки в Telegram"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < 2:  # Картинка стоит 2 звезды
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
    
    # Запоминаем что пользователь в режиме генерации
    context.user_data["in_image_mode"] = True


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, prompt: str):
    """Обработка генерации картинки"""
    a = get_access(uid)
    
    await update.message.reply_text("🎨 Генерирую картинку... (до 30 секунд)")
    
    try:
        image_base64 = generate_image(prompt)
        image_data = base64.b64decode(image_base64.split(",")[1])
        
        await update.message.reply_photo(
            photo=image_data,
            caption=f"🖼 Промпт: {prompt}"
        )
        
        # Списываем звезды если не FREE (2 звезды)
        if not a.get("is_free"):
            spend_stars(uid, 2)
            
        # Логируем
        send_log_http(f"🖼 Генерация: {uid} -> {prompt[:50]}...")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка генерации: {e}")