# bot/modes/image_mode.py
from telegram import Update
from telegram.ext import ContextTypes
import base64
from api import get_access, increment_images, add_stars_spent
from payments import get_balance, spend_stars
from stability_client import generate_image

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await query.message.reply_text("❌ Недостаточно звезд (нужно 2).")
        return
    
    await query.message.reply_text("🖼 Опиши картинку. /cancel для отмены")
    context.user_data["mode"] = "image"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    user = update.effective_user
    uid = user.id
    a = get_access(uid)
    
    await update.message.reply_text("🎨 Генерирую...")
    
    try:
        image_base64 = generate_image(prompt)
        image_data = base64.b64decode(image_base64.split(",")[1])
        await update.message.reply_photo(photo=image_data, caption=f"🖼 {prompt[:50]}")
        increment_images(uid)
        if not a.get("is_free"):
            spend_stars(uid, 2)
            add_stars_spent(uid, 2)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")