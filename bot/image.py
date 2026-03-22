# bot/image.py - КНОПКА ОТДЕЛЬНО БЕЗ ТЕКСТА
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import base64

from api import get_access, increment_images, add_stars_spent
from payments import get_balance, spend_stars
from .utils import send_fresh_menu

try:
    from openai_image import generate_image_dalle
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .config import send_log_http

# Хранилище: user_id -> message_id последней КНОПКИ
last_button_message = {}


async def inline_image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    uid = update.effective_user.id
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < 10:
        await query.message.reply_text("❌ Недостаточно звезд (нужно 10).")
        return
    
    text = "🖼 Напиши описание картинки.\nСтоимость: 10⭐"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="exit_image_from_start")]])
    
    try:
        sent_msg = await query.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        sent_msg = await query.message.reply_text(text, reply_markup=keyboard)
    
    context.user_data["image_start_message_id"] = sent_msg.message_id
    context.user_data["in_image_mode"] = True
    
    print(f"✅ Режим генерации включен для {uid}")


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, prompt: str):
    a = get_access(uid)
    
    if not OPENAI_AVAILABLE:
        await update.message.reply_text("❌ Сервис генерации недоступен.")
        context.user_data["in_image_mode"] = False
        return
    
    if "image_start_message_id" in context.user_data:
        try:
            await context.bot.delete_message(uid, context.user_data["image_start_message_id"])
            del context.user_data["image_start_message_id"]
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    status_msg = await update.message.reply_text("🎨 Генерирую...")
    
    try:
        image_base64 = generate_image_dalle(prompt, "1024x1024", "standard")
        
        if image_base64.startswith("data:image/png;base64,"):
            image_data = base64.b64decode(image_base64.split(",")[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        await status_msg.delete()
        
        # Удаляем ПРЕДЫДУЩУЮ кнопку
        if uid in last_button_message and last_button_message[uid]:
            try:
                await context.bot.delete_message(uid, last_button_message[uid])
                print(f"✅ Предыдущая кнопка удалена {last_button_message[uid]}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить предыдущую кнопку: {e}")
        
        # Отправляем картинку без кнопки
        await context.bot.send_photo(
            chat_id=uid,
            photo=image_data,
            caption=f"🖼 {prompt[:100]}..."
        )
        
        # Отправляем отдельное сообщение ТОЛЬКО С КНОПКОЙ (без текста)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️", callback_data="exit_image")]])
        sent_button = await context.bot.send_message(
            chat_id=uid,
            text="",
            reply_markup=keyboard
        )
        
        last_button_message[uid] = sent_button.message_id
        
        increment_images(uid)
        if not a.get("is_free"):
            spend_stars(uid, 10)
            add_stars_spent(uid, 10)
        
        context.user_data["in_image_mode"] = True
        
        send_log_http(f"🖼 Генерация картинки: {uid} -> {prompt[:50]}...")
        
    except Exception as e:
        await status_msg.delete()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")
        context.user_data["in_image_mode"] = False
        print(f"❌ Ошибка генерации для {uid}: {e}")


async def exit_image(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    print(f"🚪 Выход из генерации для {uid}")
    
    # Удаляем сообщение с кнопкой
    if uid in last_button_message and last_button_message[uid]:
        try:
            await context.bot.delete_message(uid, last_button_message[uid])
            print(f"✅ Сообщение с кнопкой удалено {last_button_message[uid]}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить сообщение с кнопкой: {e}")
        
        del last_button_message[uid]
    
    if "image_start_message_id" in context.user_data:
        del context.user_data["image_start_message_id"]
    
    context.user_data["in_image_mode"] = False
    
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из режима картинок завершен для {uid}")


async def exit_image_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    print(f"🚪 Выход из стартового экрана для {uid}")
    
    query = update.callback_query
    
    if query and query.message:
        try:
            await query.message.delete()
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    context.user_data.pop("image_start_message_id", None)
    context.user_data["in_image_mode"] = False
    
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из стартового экрана завершен для {uid}")