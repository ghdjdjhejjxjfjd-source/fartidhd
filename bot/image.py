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

# Глобальное хранилище ID последнего сообщения с кнопкой
last_bot_message_with_button = {}


async def inline_image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало генерации картинки в Telegram (как в чате)"""
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
    
    # Сохраняем ID сообщения, на котором была нажата кнопка
    context.user_data["invite_message_id"] = query.message.message_id
    
    # Текст с инструкцией
    text = (
        "🖼 **Генерация картинки**\n\n"
        "Напиши описание того, что хочешь увидеть.\n"
        "Например: *красивый закат в горах*\n\n"
        "Стоимость: 10⭐"
    )
    
    # Кнопка "Назад" (как в чате)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="exit_image_from_start")]
    ])
    
    sent_msg = await query.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Запоминаем ID стартового сообщения
    context.user_data["image_start_message_id"] = sent_msg.message_id
    context.user_data["in_image_mode"] = True
    print(f"✅ Режим генерации включен для {uid}")


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, prompt: str):
    """Обработка генерации картинки (как в чате)"""
    a = get_access(uid)
    
    if not OPENAI_AVAILABLE:
        await update.message.reply_text("❌ Сервис генерации временно недоступен.")
        return
    
    # Удаляем кнопку со стартового экрана (как в чате)
    if "image_start_message_id" in context.user_data:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=uid,
                message_id=context.user_data["image_start_message_id"],
                reply_markup=None
            )
            print(f"✅ Кнопка удалена со стартового экрана")
            del context.user_data["image_start_message_id"]
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку со старта: {e}")
    
    # Сообщение о начале генерации
    status_msg = await update.message.reply_text("🎨 Генерирую картинку...")
    
    try:
        # Генерация через DALL-E
        image_base64 = generate_image_dalle(
            prompt=prompt,
            size="1024x1024",
            quality="standard"
        )
        
        # Извлекаем base64
        if image_base64.startswith("data:image/png;base64,"):
            image_data = base64.b64decode(image_base64.split(",")[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        # Удаляем сообщение о статусе
        await status_msg.delete()
        
        # Удаляем кнопку с предыдущего ответа (как в чате)
        if uid in last_bot_message_with_button:
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=last_bot_message_with_button[uid],
                    reply_markup=None
                )
                print(f"✅ Кнопка удалена с предыдущего сообщения")
            except Exception as e:
                print(f"⚠️ Не удалось убрать кнопку: {e}")
        
        # Отправляем картинку с кнопкой "Назад" (как в чате)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад", callback_data="exit_image")]
        ])
        
        sent_msg = await context.bot.send_photo(
            chat_id=uid,
            photo=image_data,
            caption=f"🖼 {prompt}",
            reply_markup=keyboard
        )
        
        # Запоминаем это сообщение как последнее с кнопкой
        last_bot_message_with_button[uid] = sent_msg.message_id
        
        # Обновляем статистику
        increment_images(uid)
        
        # Списываем звезды (10 звезд)
        if not a.get("is_free"):
            spend_stars(uid, 10)
            add_stars_spent(uid, 10)
            
        # Логируем
        send_log_http(f"🖼 Генерация: {uid} -> {prompt[:50]}...")
        
        # Режим остаётся активным для следующих запросов (как в чате)
        
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
    """Выход из режима генерации (с последней картинки) — как в чате"""
    print(f"🚪 Выход из режима генерации для {uid}")
    
    # Удаляем кнопку с последнего сообщения с картинкой
    if uid in last_bot_message_with_button:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=uid,
                message_id=last_bot_message_with_button[uid],
                reply_markup=None
            )
            print(f"✅ Кнопка удалена с сообщения")
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку: {e}")
        del last_bot_message_with_button[uid]
    
    # Очищаем данные
    if "image_start_message_id" in context.user_data:
        del context.user_data["image_start_message_id"]
    
    # Выходим из режима
    context.user_data["in_image_mode"] = False
    
    # Удаляем все старые меню
    await delete_all_menus(context.bot, uid)
    
    # Отправляем новое меню
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Новое меню отправлено для {uid}")


async def exit_image_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Выход из режима генерации со стартового экрана — как в чате"""
    print(f"🚪 Выход со стартового экрана генерации для {uid}")
    
    # Удаляем стартовое сообщение
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
            print(f"✅ Стартовое сообщение удалено")
        except Exception as e:
            print(f"⚠️ Не удалось удалить стартовое сообщение: {e}")
    
    # Очищаем данные
    if "image_start_message_id" in context.user_data:
        del context.user_data["image_start_message_id"]
    
    # Выходим из режима
    context.user_data["in_image_mode"] = False
    
    # Удаляем все старые меню
    await delete_all_menus(context.bot, uid)
    
    # Отправляем новое меню
    await send_fresh_menu(context.bot, uid)
    print(f"✅ Новое меню отправлено для {uid}")