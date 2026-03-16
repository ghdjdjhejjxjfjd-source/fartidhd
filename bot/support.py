# bot/support.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os
import re

from .config import send_log_http

# ID группы поддержки (из .env)
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "0"))

# Хранилище для связи message_id -> user_id
support_messages = {}

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало обращения в поддержку"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    # Текст с инструкцией
    text = (
        "💬 Поддержка\n\n"
        "Напиши сюда свой вопрос или проблему.\n"
        "Можешь отправить:\n"
        "• Текст\n"
        "• Фото\n"
        "• Файл\n\n"
        "Я передам твоё сообщение админам.\n"
        "Они ответят как можно скорее!"
    )
    
    # Клавиатура с кнопкой назад
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_previous")]
    ])
    
    await query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )
    
    # Запоминаем что пользователь в режиме поддержки
    context.user_data["in_support_mode"] = True
    print(f"✅ Режим поддержки включен для {uid}")

async def forward_to_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переслать сообщение пользователя в группу поддержки (ОДНИМ СООБЩЕНИЕМ)"""
    if not SUPPORT_GROUP_ID:
        print("❌ SUPPORT_GROUP_ID не настроен")
        await update.message.reply_text("❌ Служба поддержки временно недоступна")
        return
    
    user = update.effective_user
    uid = user.id
    username = f"@{user.username}" if user.username else "—"
    first_name = user.first_name or "—"
    
    # Формируем шапку с информацией о пользователе
    header = (
        f"🆔 ID: {uid}\n"
        f"👤 Имя: {first_name}\n"
        f"📱 Юзернейм: {username}\n"
        f"📅 {update.message.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"———————————————\n\n"
    )
    
    # Кнопки для админа
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ответить", callback_data=f"support_reply_{uid}"),
            InlineKeyboardButton("⛔ Заблокировать", callback_data=f"support_block_{uid}")
        ],
        [
            InlineKeyboardButton("⭐ Добавить звёзд", callback_data=f"support_addstars_{uid}")
        ]
    ])
    
    # Отправляем ВСЁ одним сообщением
    if update.message.text:
        full_text = header + update.message.text
        sent_msg = await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=full_text,
            reply_markup=keyboard
        )
        support_messages[sent_msg.message_id] = uid
        
    elif update.message.photo:
        photo = update.message.photo[-1]
        caption = header + (update.message.caption or "")
        sent_msg = await context.bot.send_photo(
            chat_id=SUPPORT_GROUP_ID,
            photo=photo.file_id,
            caption=caption,
            reply_markup=keyboard
        )
        support_messages[sent_msg.message_id] = uid
        
    elif update.message.document:
        caption = header + (update.message.caption or "")
        sent_msg = await context.bot.send_document(
            chat_id=SUPPORT_GROUP_ID,
            document=update.message.document.file_id,
            caption=caption,
            reply_markup=keyboard
        )
        support_messages[sent_msg.message_id] = uid
        
    elif update.message.video:
        caption = header + (update.message.caption or "")
        sent_msg = await context.bot.send_video(
            chat_id=SUPPORT_GROUP_ID,
            video=update.message.video.file_id,
            caption=caption,
            reply_markup=keyboard
        )
        support_messages[sent_msg.message_id] = uid
        
    elif update.message.voice:
        sent_msg = await context.bot.send_voice(
            chat_id=SUPPORT_GROUP_ID,
            voice=update.message.voice.file_id,
            caption=header,
            reply_markup=keyboard
        )
        support_messages[sent_msg.message_id] = uid
        
    elif update.message.audio:
        caption = header + (update.message.caption or "")
        sent_msg = await context.bot.send_audio(
            chat_id=SUPPORT_GROUP_ID,
            audio=update.message.audio.file_id,
            caption=caption,
            reply_markup=keyboard
        )
        support_messages[sent_msg.message_id] = uid
    
    # Подтверждение пользователю
    await update.message.reply_text(
        "✅ Сообщение отправлено в поддержку.\n"
        "Ожидайте ответа."
    )
    
    # Выходим из режима поддержки после отправки
    context.user_data["in_support_mode"] = False
    
    # Логируем
    send_log_http(f"📨 Поддержка: {uid} -> {update.message.text[:50] if update.message.text else 'медиа'}")

async def handle_support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок в группе поддержки"""
    query = update.callback_query
    data = query.data
    
    await query.answer()
    
    if data.startswith("support_reply_"):
        user_id = int(data.split("_")[2])
        context.user_data["replying_to"] = user_id
        await query.message.reply_text(
            f"✏️ Режим ответа для пользователя {user_id}\n"
            f"Просто напиши сообщение — оно уйдёт ему."
        )
    
    elif data.startswith("support_block_"):
        user_id = int(data.split("_")[2])
        from api import set_blocked
        set_blocked(user_id, True)
        await query.message.reply_text(f"✅ Пользователь {user_id} заблокирован")
    
    elif data.startswith("support_addstars_"):
        user_id = int(data.split("_")[2])
        from payments import add_stars
        add_stars(user_id, 100, "support")
        await query.message.reply_text(f"✅ Пользователю {user_id} добавлено 100 ⭐")

async def handle_support_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа админа пользователю"""
    
    # Проверяем что сообщение из группы поддержки
    if not SUPPORT_GROUP_ID or update.effective_chat.id != SUPPORT_GROUP_ID:
        return
    
    # Если админ в режиме ответа
    if "replying_to" in context.user_data:
        user_id = context.user_data["replying_to"]
        admin = update.effective_user
        
        try:
            if update.message.text:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📨 Ответ от поддержки:\n\n{update.message.text}"
                )
            elif update.message.photo:
                photo = update.message.photo[-1]
                caption = f"📨 Ответ от поддержки"
                if update.message.caption:
                    caption += f"\n\n{update.message.caption}"
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo.file_id,
                    caption=caption
                )
            
            await update.message.reply_text(f"✅ Ответ отправлен пользователю {user_id}")
            del context.user_data["replying_to"]
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
        
        return
    
    # Если не в режиме ответа - пробуем найти по reply
    if update.message.reply_to_message:
        replied_msg_id = update.message.reply_to_message.message_id
        
        if replied_msg_id in support_messages:
            user_id = support_messages[replied_msg_id]
            
            try:
                if update.message.text:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"📨 Ответ от поддержки:\n\n{update.message.text}"
                    )
                elif update.message.photo:
                    photo = update.message.photo[-1]
                    caption = f"📨 Ответ от поддержки"
                    if update.message.caption:
                        caption += f"\n\n{update.message.caption}"
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo.file_id,
                        caption=caption
                    )
                
                await update.message.reply_text(f"✅ Ответ отправлен пользователю {user_id}")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")