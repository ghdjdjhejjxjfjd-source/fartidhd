# bot/image.py - ИСПРАВЛЕННАЯ ВЕРСИЯ (кнопка только под последней картинкой)
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

# Хранилище: user_id -> список всех message_id картинок (чтобы удалять кнопки у предыдущих)
all_image_messages = {}


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
    
    sent_msg = await query.message.edit_text(text, reply_markup=keyboard)
    context.user_data["image_start_message_id"] = sent_msg.message_id
    context.user_data["in_image_mode"] = True
    
    # Инициализируем списки для этого пользователя
    if uid not in all_image_messages:
        all_image_messages[uid] = []
    if uid not in last_image_message:
        last_image_message[uid] = None


async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, prompt: str):
    """Обработка запроса на генерацию картинки"""
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
        
        # ===== КЛЮЧЕВАЯ ЛОГИКА: удаляем кнопку у ПРЕДЫДУЩЕЙ картинки =====
        # (НО НЕ УДАЛЯЕМ САМУ КАРТИНКУ)
        if uid in last_image_message and last_image_message[uid]:
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=last_image_message[uid],
                    reply_markup=None
                )
                print(f"✅ Кнопка удалена у предыдущей картинки {last_image_message[uid]}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить кнопку у предыдущей картинки: {e}")
        
        # Отправляем НОВУЮ картинку С КНОПКОЙ
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="exit_image")]])
        sent_msg = await context.bot.send_photo(
            uid, 
            image_data, 
            caption=f"🖼 {prompt}", 
            reply_markup=keyboard
        )
        
        # Запоминаем ID новой картинки как последнюю с кнопкой
        last_image_message[uid] = sent_msg.message_id
        
        # Сохраняем в список всех картинок (для возможной очистки)
        if uid not in all_image_messages:
            all_image_messages[uid] = []
        all_image_messages[uid].append(sent_msg.message_id)
        
        # Ограничиваем список до 50 сообщений
        if len(all_image_messages[uid]) > 50:
            all_image_messages[uid] = all_image_messages[uid][-50:]
        
        # Списание звезд
        increment_images(uid)
        if not a.get("is_free"):
            spend_stars(uid, 10)
            add_stars_spent(uid, 10)
        
        # Остаёмся в режиме — можно отправлять следующие запросы
        context.user_data["in_image_mode"] = True
        
        # Лог
        send_log_http(f"🖼 Генерация картинки: {uid} -> {prompt[:50]}...")
        
    except Exception as e:
        await status_msg.delete()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")
        context.user_data["in_image_mode"] = False


async def exit_image(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """
    Выход при нажатии кнопки "Назад" под последней картинкой.
    Удаляем кнопку у последней картинки и возвращаемся в меню.
    """
    print(f"🚪 Выход из генерации картинок для {uid} (нажата кнопка Назад)")
    
    # 1. Удаляем кнопку у последней картинки
    if uid in last_image_message and last_image_message[uid]:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=uid,
                message_id=last_image_message[uid],
                reply_markup=None
            )
            print(f"✅ Кнопка удалена у последней картинки {last_image_message[uid]}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить кнопку: {e}")
        
        # Очищаем запись о последней картинке
        last_image_message[uid] = None
    
    # 2. Очищаем данные режима
    context.user_data.pop("image_start_message_id", None)
    context.user_data["in_image_mode"] = False
    
    # 3. Удаляем старые меню и показываем новое
    await delete_all_menus(context.bot, uid)
    await send_fresh_menu(context.bot, uid)
    
    print(f"✅ Выход из режима картинок завершен для {uid}")


async def exit_image_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int):
    """
    Выход при нажатии кнопки "Назад" в стартовом экране (до первой генерации).
    """
    print(f"🚪 Выход из стартового экрана генерации для {uid}")
    
    # Удаляем стартовое сообщение
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
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


# ===== ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОЧИСТКИ ПРИ ВЫХОДЕ ИЗ БОТА =====
async def cleanup_image_state(uid: int, bot):
    """Очистить состояние пользователя при выходе"""
    if uid in last_image_message:
        # Пытаемся удалить кнопку у последней картинки
        if last_image_message[uid]:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=uid,
                    message_id=last_image_message[uid],
                    reply_markup=None
                )
            except:
                pass
        del last_image_message[uid]
    
    if uid in all_image_messages:
        del all_image_messages[uid]