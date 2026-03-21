# bot/image.py - ИСПРАВЛЕННАЯ ВЕРСИЯ (кнопка удаляется как в чате)
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

# Хранилище: user_id -> message_id последней картинки с кнопкой
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
    
    if uid not in last_image_message:
        last_image_message[uid] = None
    
    print(f"✅ Режим генерации включен для {uid}")


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, prompt: str):
    """Обработка запроса на генерацию картинки"""
    a = get_access(uid)
    
    if not OPENAI_AVAILABLE:
        await update.message.reply_text("❌ Сервис генерации недоступен.")
        context.user_data["in_image_mode"] = False
        return
    
    # Удаляем стартовое сообщение
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
        
        # Удаляем кнопку у ПРЕДЫДУЩЕЙ картинки
        if uid in last_image_message and last_image_message[uid]:
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=last_image_message[uid],
                    reply_markup=None
                )
                print(f"✅ Кнопка удалена у предыдущей картинки {last_image_message[uid]}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить кнопку у предыдущей: {e}")
        
        # Отправляем новую картинку с кнопкой
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="exit_image")]])
        sent_msg = await context.bot.send_photo(
            chat_id=uid,
            photo=image_data,
            caption=f"🖼 {prompt[:100]}...",
            reply_markup=keyboard
        )
        
        last_image_message[uid] = sent_msg.message_id
        print(f"✅ Новая картинка отправлена для {uid}, ID: {sent_msg.message_id}")
        
        increment_images(uid)
        if not a.get("is_free"):
            spend_stars(uid, 10)
            add_stars_spent(uid, 10)
        
        # Остаёмся в режиме
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
    Удаляем ТОЛЬКО КНОПКУ, картинка остаётся (как в чате с ИИ).
    """
    print(f"🚪 Выход из генерации для {uid} (нажата кнопка Назад)")
    
    query = update.callback_query
    current_message_id = query.message.message_id if query.message else None
    
    # 1. Удаляем ТОЛЬКО КНОПКУ у текущей картинки (как в чате)
    if current_message_id:
        try:
            # Пробуем удалить кнопку через edit_reply_markup
            await query.message.edit_reply_markup(reply_markup=None)
            print(f"✅ Кнопка удалена у картинки {current_message_id}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку через edit_reply_markup: {e}")
            # Альтернативный способ: через bot.edit_message_reply_markup
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=current_message_id,
                    reply_markup=None
                )
                print(f"✅ Кнопка удалена (альтернативный способ) у картинки {current_message_id}")
            except Exception as e2:
                print(f"⚠️ Не удалось удалить кнопку альтернативным способом: {e2}")
    
    # 2. Очищаем запись о последней картинке
    if uid in last_image_message and last_image_message[uid] == current_message_id:
        last_image_message[uid] = None
    
    # 3. Очищаем данные режима
    context.user_data.pop("image_start_message_id", None)
    context.user_data["in_image_mode"] = False
    
    # 4. Удаляем старые меню и показываем новое
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из режима картинок завершен для {uid}")


async def exit_image_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """
    Выход при нажатии кнопки "Назад" в стартовом экране.
    """
    print(f"🚪 Выход из стартового экрана генерации для {uid}")
    
    query = update.callback_query
    
    if query and query.message:
        try:
            await query.message.delete()
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    context.user_data.pop("image_start_message_id", None)
    context.user_data["in_image_mode"] = False
    
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из стартового экрана завершен для {uid}")


async def cleanup_image_state(uid: int, bot):
    """Очистить состояние (опционально)"""
    if uid in last_image_message:
        del last_image_message[uid]