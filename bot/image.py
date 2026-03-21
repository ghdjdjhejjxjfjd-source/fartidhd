from telegram import Update
from telegram.ext import ContextTypes
import base64

from api import get_access, increment_images, add_stars_spent
from payments import get_balance, spend_stars

# Импортируем OpenAI для генерации картинок
try:
    from openai_image import generate_image_dalle
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI image generation not available")

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
    """Обработка генерации картинки через OpenAI DALL-E 3"""
    a = get_access(uid)
    
    # Проверяем доступность OpenAI
    if not OPENAI_AVAILABLE:
        await update.message.reply_text("❌ Сервис генерации временно недоступен.")
        return
    
    await update.message.reply_text("🎨 Генерирую картинку через DALL-E 3... (до 30 секунд)")
    
    try:
        # Используем DALL-E 3 для генерации
        # Размер по умолчанию 1024x1024, качество standard
        image_base64 = generate_image_dalle(
            prompt=prompt,
            size="1024x1024",
            quality="standard"
        )
        
        # Извлекаем base64 данные из формата "data:image/png;base64,XXX"
        if image_base64.startswith("data:image/png;base64,"):
            image_data = base64.b64decode(image_base64.split(",")[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        await update.message.reply_photo(
            photo=image_data,
            caption=f"🖼 Промпт: {prompt}\n🎨 Сгенерировано через DALL-E 3"
        )
        
        # Обновляем статистику
        increment_images(uid)
        
        # Списываем звезды если не FREE (2 звезды)
        if not a.get("is_free"):
            spend_stars(uid, 2)
            add_stars_spent(uid, 2)
            
        # Логируем
        send_log_http(f"🖼 Генерация (DALL-E 3): {uid} -> {prompt[:50]}...")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка генерации: {error_msg}")
        
        if "insufficient_stars" in error_msg.lower():
            await update.message.reply_text(
                "❌ Недостаточно звезд (нужно 2).\n"
                "Купи звезды в меню: ⭐ Купить звезды"
            )
        elif "API key" in error_msg.lower() or "openai" in error_msg.lower():
            await update.message.reply_text(
                "❌ Ошибка API OpenAI. Попробуйте позже."
            )
        elif "timeout" in error_msg.lower():
            await update.message.reply_text(
                "❌ Превышено время ожидания. Попробуйте позже."
            )
        else:
            await update.message.reply_text(f"❌ Ошибка генерации: {error_msg[:100]}")