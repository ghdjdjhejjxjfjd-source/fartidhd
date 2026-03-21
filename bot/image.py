from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import base64

from api import get_access, increment_images, add_stars_spent
from payments import get_balance, spend_stars
from .utils import delete_all_menus, send_fresh_menu

try:
    from openai_image import generate_image_dalle
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .config import send_log_http

last_bot_message_with_button = {}


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
    
    sent_msg = await query.message.edit_text(text, reply_markup=keyboard)
    context.user_data["image_start_message_id"] = sent_msg.message_id
    context.user_data["in_image_mode"] = True


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, prompt: str):
    a = get_access(uid)
    
    if not OPENAI_AVAILABLE:
        await update.message.reply_text("❌ Сервис генерации недоступен.")
        return
    
    # Удаляем стартовое сообщение с кнопкой
    if "image_start_message_id" in context.user_data:
        try:
            await context.bot.delete_message(uid, context.user_data["image_start_message_id"])
            del context.user_data["image_start_message_id"]
        except:
            pass
    
    status_msg = await update.message.reply_text("🎨 Генерирую...")
    
    try:
        image_base64 = generate_image_dalle(prompt, "1024x1024", "standard")
        
        if image_base64.startswith("data:image/png;base64,"):
            image_data = base64.b64decode(image_base64.split(",")[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        await status_msg.delete()
        
        # Удаляем кнопку с предыдущей картинки
        if uid in last_bot_message_with_button:
            try:
                await context.bot.edit_message_reply_markup(uid, last_bot_message_with_button[uid], reply_markup=None)
            except:
                pass
        
        # Отправляем картинку с кнопкой
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="exit_image")]])
        sent_msg = await context.bot.send_photo(uid, image_data, caption=f"🖼 {prompt}", reply_markup=keyboard)
        
        # Запоминаем ID последней картинки с кнопкой
        last_bot_message_with_button[uid] = sent_msg.message_id
        
        increment_images(uid)
        if not a.get("is_free"):
            spend_stars(uid, 10)
            add_stars_spent(uid, 10)
        
        # ✅ ОСТАЁМСЯ В РЕЖИМЕ — можно отправлять следующие запросы
        context.user_data["in_image_mode"] = True
        
    except Exception as e:
        await status_msg.delete()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")
        context.user_data["in_image_mode"] = False


async def exit_image(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Выход при нажатии кнопки Назад под картинкой"""
    # ✅ Удаляем кнопку с последней картинки
    if uid in last_bot_message_with_button:
        try:
            await context.bot.edit_message_reply_markup(uid, last_bot_message_with_button[uid], reply_markup=None)
            del last_bot_message_with_button[uid]
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку: {e}")
    
    # Очищаем данные
    context.user_data.pop("image_start_message_id", None)
    context.user_data["in_image_mode"] = False
    
    # ✅ Удаляем старые меню и показываем новое
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)


async def exit_image_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Выход при нажатии кнопки Назад в стартовом экране"""
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
        except:
            pass
    
    context.user_data.pop("image_start_message_id", None)
    context.user_data["in_image_mode"] = False
    
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)