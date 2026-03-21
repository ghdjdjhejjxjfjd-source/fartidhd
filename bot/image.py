# bot/image.py - КАК В ЧАТЕ
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

# Хранилище: user_id -> message_id последней картинки с кнопкой (как в чате)
last_image_message = {}


async def inline_image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало режима генерации картинок"""
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
    """Обработка запроса на генерацию картинки"""
    a = get_access(uid)
    
    if not OPENAI_AVAILABLE:
        await update.message.reply_text("❌ Сервис генерации недоступен.")
        context.user_data["in_image_mode"] = False
        return
    
    # Удаляем стартовое сообщение с кнопкой (если есть)
    if "image_start_message_id" in context.user_data:
        try:
            await context.bot.delete_message(uid, context.user_data["image_start_message_id"])
            del context.user_data["image_start_message_id"]
            print(f"✅ Стартовое сообщение удалено для {uid}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    status_msg = await update.message.reply_text("🎨 Генерирую...")
    
    try:
        # Генерация картинки
        image_base64 = generate_image_dalle(prompt, "1024x1024", "standard")
        
        if image_base64.startswith("data:image/png;base64,"):
            image_data = base64.b64decode(image_base64.split(",")[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        await status_msg.delete()
        
        # ===== КАК В ЧАТЕ: удаляем кнопку у ПРЕДЫДУЩЕЙ картинки =====
        if uid in last_image_message and last_image_message[uid]:
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=last_image_message[uid],
                    reply_markup=None
                )
                print(f"✅ Кнопка удалена у предыдущей картинки {last_image_message[uid]}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить кнопку: {e}")
        
        # Отправляем новую картинку с кнопкой
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="exit_image")]])
        sent_msg = await context.bot.send_photo(
            chat_id=uid,
            photo=image_data,
            caption=f"🖼 {prompt[:100]}...",
            reply_markup=keyboard
        )
        
        # Запоминаем ID этой картинки как последнюю с кнопкой (как в чате)
        last_image_message[uid] = sent_msg.message_id
        print(f"✅ Новая картинка отправлена для {uid}, ID: {sent_msg.message_id}")
        
        # Списание звезд
        increment_images(uid)
        if not a.get("is_free"):
            spend_stars(uid, 10)
            add_stars_spent(uid, 10)
        
        # Остаёмся в режиме (как в чате)
        context.user_data["in_image_mode"] = True
        
        send_log_http(f"🖼 Генерация картинки: {uid} -> {prompt[:50]}...")
        
    except Exception as e:
        await status_msg.delete()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")
        context.user_data["in_image_mode"] = False
        print(f"❌ Ошибка генерации для {uid}: {e}")


async def exit_image(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """
    Выход при нажатии кнопки "Назад" под картинкой.
    ТОЧНО КАК В ЧАТЕ: удаляем кнопку у последней картинки и показываем меню.
    """
    print(f"🚪 Выход из генерации для {uid} (нажата кнопка Назад)")
    
    # ===== КАК В ЧАТЕ: удаляем кнопку с последнего сообщения =====
    if uid in last_image_message and last_image_message[uid]:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=uid,
                message_id=last_image_message[uid],
                reply_markup=None
            )
            print(f"✅ Кнопка удалена с картинки {last_image_message[uid]}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку: {e}")
        
        # Удаляем запись о последней картинке (как в чате)
        del last_image_message[uid]
    
    # Очищаем стартовое сообщение из памяти если есть
    if "image_start_message_id" in context.user_data:
        del context.user_data["image_start_message_id"]
    
    # Выходим из режима генерации
    context.user_data["in_image_mode"] = False
    
    # Удаляем все старые меню
    await delete_all_menus(context.bot, uid)
    
    # Отправляем НОВОЕ сообщение с главным меню
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Новое меню отправлено для {uid}")


async def exit_image_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """
    Выход при нажатии кнопки "Назад" в стартовом экране (до первой генерации).
    """
    print(f"🚪 Выход из стартового экрана генерации для {uid}")
    
    query = update.callback_query
    
    # Удаляем стартовое сообщение
    if query and query.message:
        try:
            await query.message.delete()
            print(f"✅ Стартовое сообщение удалено")
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    # Очищаем данные
    context.user_data.pop("image_start_message_id", None)
    context.user_data["in_image_mode"] = False
    
    # Удаляем старые меню и показываем новое
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из стартового экрана завершен для {uid}")