from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import base64

from api import get_access, increment_images, add_stars_spent
from payments import get_balance, spend_stars
from .utils import delete_all_menus, send_fresh_menu

# Импортируем OpenAI для генерации картинок
try:
    from openai_image import generate_image_dalle
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI image generation not available")

from .config import send_log_http

# Глобальное хранилище ID последнего сообщения с кнопкой
last_bot_message_with_button = {}


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
    
    if not a.get("is_free") and balance < 10:
        await query.message.reply_text(
            "❌ Недостаточно звезд (нужно 10).\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    context.user_data["invite_message_id"] = query.message.message_id
    
    text = (
        "🖼 **Генерация картинки**\n\n"
        "Напиши описание того, что хочешь увидеть.\n"
        "Например: *красивый закат в горах*\n\n"
        "Стоимость: 10⭐"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="exit_image_from_start")]
    ])
    
    sent_msg = await query.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    context.user_data["image_start_message_id"] = sent_msg.message_id
    context.user_data["in_image_mode"] = True
    print(f"✅ Режим генерации включен для {uid}")


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, prompt: str):
    """Обработка генерации картинки"""
    a = get_access(uid)
    
    if not OPENAI_AVAILABLE:
        await update.message.reply_text("❌ Сервис генерации временно недоступен.")
        return
    
    # Удаляем стартовое сообщение
    if "image_start_message_id" in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=uid,
                message_id=context.user_data["image_start_message_id"]
            )
            del context.user_data["image_start_message_id"]
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    status_msg = await update.message.reply_text("🎨 Генерирую картинку...")
    
    try:
        image_base64 = generate_image_dalle(
            prompt=prompt,
            size="1024x1024",
            quality="standard"
        )
        
        if image_base64.startswith("data:image/png;base64,"):
            image_data = base64.b64decode(image_base64.split(",")[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        await status_msg.delete()
        
        # Удаляем кнопку с предыдущей картинки
        if uid in last_bot_message_with_button:
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=last_bot_message_with_button[uid],
                    reply_markup=None
                )
            except Exception as e:
                print(f"⚠️ Не удалось убрать кнопку: {e}")
        
        # Отправляем новую картинку с кнопкой
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад", callback_data="exit_image")]
        ])
        
        sent_msg = await context.bot.send_photo(
            chat_id=uid,
            photo=image_data,
            caption=f"🖼 {prompt}",
            reply_markup=keyboard
        )
        
        last_bot_message_with_button[uid] = sent_msg.message_id
        
        increment_images(uid)
        
        if not a.get("is_free"):
            spend_stars(uid, 10)
            add_stars_spent(uid, 10)
            
        send_log_http(f"🖼 Генерация: {uid} -> {prompt[:50]}...")
        
        # Режим остаётся активным для следующих запросов
        
    except Exception as e:
        await status_msg.delete()
        error_msg = str(e)
        print(f"❌ Ошибка генерации: {error_msg}")
        
        if "insufficient_stars" in error_msg.lower():
            await update.message.reply_text(
                "❌ Недостаточно звезд (нужно 10).\n"
                "Купи звезды в меню: ⭐ Купить звезды"
            )
            context.user_data["in_image_mode"] = False
        elif "API key" in error_msg.lower():
            await update.message.reply_text("❌ Ошибка API. Попробуйте позже.")
        elif "timeout" in error_msg.lower():
            await update.message.reply_text("❌ Превышено время ожидания. Попробуйте позже.")
        else:
            await update.message.reply_text(f"❌ Ошибка: {error_msg[:100]}")


async def exit_image(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Выход из режима генерации (нажата кнопка Назад под картинкой)"""
    print(f"🚪 Выход из режима генерации для {uid}")
    
    # Удаляем кнопку с последней картинки
    if uid in last_bot_message_with_button:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=uid,
                message_id=last_bot_message_with_button[uid],
                reply_markup=None
            )
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку: {e}")
        del last_bot_message_with_button[uid]
    
    if "image_start_message_id" in context.user_data:
        del context.user_data["image_start_message_id"]
    
    context.user_data["in_image_mode"] = False
    
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Новое меню отправлено для {uid}")


async def exit_image_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Выход из режима генерации со стартового экрана"""
    print(f"🚪 Выход со стартового экрана генерации для {uid}")
    
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    if "image_start_message_id" in context.user_data:
        del context.user_data["image_start_message_id"]
    
    context.user_data["in_image_mode"] = False
    
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Новое меню отправлено для {uid}")