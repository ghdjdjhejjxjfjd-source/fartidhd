# bot/image.py - ИСПРАВЛЕННАЯ ВЕРСИЯ (только одно меню)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import base64

from api import get_access, increment_images, add_stars_spent
from payments import get_balance, spend_stars
from .utils import send_fresh_menu  # ← только send_fresh_menu, без delete_all_menus

try:
    from openai_image import generate_image_dalle
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .config import send_log_http

# Хранилище: user_id -> message_id последней КНОПКИ (отдельное сообщение)
last_button_message = {}


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
        
        # ===== УДАЛЯЕМ ПРЕДЫДУЩУЮ КНОПКУ (НО НЕ КАРТИНКУ) =====
        if uid in last_button_message and last_button_message[uid]:
            try:
                await context.bot.delete_message(uid, last_button_message[uid])
                print(f"✅ Предыдущая кнопка удалена {last_button_message[uid]}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить предыдущую кнопку: {e}")
        
        # 1. Отправляем КАРТИНКУ без кнопки (остаётся навсегда)
        sent_photo = await context.bot.send_photo(
            chat_id=uid,
            photo=image_data,
            caption=f"🖼 {prompt[:100]}..."
        )
        print(f"✅ Картинка отправлена для {uid}, ID: {sent_photo.message_id}")
        
        # 2. Отправляем ОТДЕЛЬНОЕ сообщение с кнопкой "Назад"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="exit_image")]])
        sent_button = await context.bot.send_message(
            chat_id=uid,
            text="⬅️ Нажмите для выхода",
            reply_markup=keyboard
        )
        
        # Запоминаем ID сообщения с кнопкой
        last_button_message[uid] = sent_button.message_id
        print(f"✅ Кнопка отправлена для {uid}, ID: {sent_button.message_id}")
        
        # Списание звезд
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
    Выход при нажатии кнопки "Назад".
    Удаляем ТОЛЬКО сообщение с кнопкой, все картинки остаются.
    """
    print(f"🚪 Выход из генерации для {uid} (нажата кнопка Назад)")
    
    # ===== УДАЛЯЕМ СООБЩЕНИЕ С КНОПКОЙ =====
    if uid in last_button_message and last_button_message[uid]:
        try:
            await context.bot.delete_message(uid, last_button_message[uid])
            print(f"✅ Сообщение с кнопкой удалено {last_button_message[uid]}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить сообщение с кнопкой: {e}")
            # Альтернативный способ: убрать кнопку
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=last_button_message[uid],
                    reply_markup=None
                )
                print(f"✅ Кнопка удалена (альтернативно) у {last_button_message[uid]}")
            except Exception as e2:
                print(f"⚠️ Не удалось удалить кнопку альтернативно: {e2}")
        
        # Удаляем запись о кнопке
        del last_button_message[uid]
    
    # Очищаем стартовое сообщение из памяти если есть
    if "image_start_message_id" in context.user_data:
        del context.user_data["image_start_message_id"]
    
    # Выходим из режима генерации
    context.user_data["in_image_mode"] = False
    
    # ===== ВАЖНО: НЕ УДАЛЯЕМ МЕНЮ ВРУЧНУЮ! =====
    # send_fresh_menu сам удалит/отредактирует старое меню
    # await delete_all_menus(context.bot, uid)  # ← УБРАНО!
    
    # Отправляем/обновляем меню (только одно!)
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из режима картинок завершен для {uid}")


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
    
    # ===== ВАЖНО: НЕ УДАЛЯЕМ МЕНЮ ВРУЧНУЮ! =====
    # await delete_all_menus(context.bot, uid)  # ← УБРАНО!
    
    # Отправляем/обновляем меню (только одно!)
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из стартового экрана завершен для {uid}")


async def cleanup_image_state(uid: int, bot):
    """Очистить состояние (опционально)"""
    if uid in last_button_message:
        del last_button_message[uid]