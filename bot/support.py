# bot/support.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os
import re

from .config import send_log_http

# ID группы поддержки (из .env)
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "0"))

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало обращения в поддержку"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    # Текст с инструкцией
    text = (
        "💬 **Поддержка**\n\n"
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
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Запоминаем что пользователь в режиме поддержки
    context.user_data["in_support_mode"] = True

async def forward_to_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переслать сообщение пользователя в группу поддержки"""
    if not SUPPORT_GROUP_ID:
        print("❌ SUPPORT_GROUP_ID не настроен")
        await update.message.reply_text("❌ Служба поддержки временно недоступна")
        return
    
    user = update.effective_user
    uid = user.id
    username = f"@{user.username}" if user.username else "—"
    first_name = user.first_name or "—"
    
    # Формируем информационный блок
    info_text = (
        f"🆔 **ID:** `{uid}`\n"
        f"👤 **Имя:** {first_name}\n"
        f"📱 **Юзернейм:** {username}\n"
        f"📅 **Дата:** {update.message.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"———————————————"
    )
    
    # Отправляем информацию в группу
    await context.bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=info_text,
        parse_mode="Markdown"
    )
    
    # Пересылаем само сообщение пользователя
    if update.message.text:
        await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=update.message.text
        )
    elif update.message.photo:
        photo = update.message.photo[-1]
        await context.bot.send_photo(
            chat_id=SUPPORT_GROUP_ID,
            photo=photo.file_id,
            caption=update.message.caption or ""
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=SUPPORT_GROUP_ID,
            document=update.message.document.file_id,
            caption=update.message.caption or ""
        )
    elif update.message.video:
        await context.bot.send_video(
            chat_id=SUPPORT_GROUP_ID,
            video=update.message.video.file_id,
            caption=update.message.caption or ""
        )
    elif update.message.voice:
        await context.bot.send_voice(
            chat_id=SUPPORT_GROUP_ID,
            voice=update.message.voice.file_id
        )
    elif update.message.audio:
        await context.bot.send_audio(
            chat_id=SUPPORT_GROUP_ID,
            audio=update.message.audio.file_id,
            caption=update.message.caption or ""
        )
    
    # Подтверждение пользователю
    await update.message.reply_text(
        "✅ Сообщение отправлено в поддержку.\n"
        "Ожидайте ответа."
    )
    
    # Выходим из режима поддержки после отправки
    context.user_data["in_support_mode"] = False
    
    # Логируем
    send_log_http(f"📨 Поддержка: {uid} -> {update.message.text[:50] if update.message.text else 'медиа'}")

async def handle_support_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа из группы поддержки"""
    
    # Проверяем что сообщение из группы поддержки
    if not SUPPORT_GROUP_ID or update.effective_chat.id != SUPPORT_GROUP_ID:
        return
    
    # Проверяем что это ответ на какое-то сообщение
    if not update.message.reply_to_message:
        return
    
    # Пробуем найти ID пользователя в сообщении на которое ответили
    replied_text = update.message.reply_to_message.text or ""
    replied_caption = update.message.reply_to_message.caption or ""
    
    # Ищем ID в тексте или подписи
    id_match = None
    if replied_text:
        id_match = re.search(r'ID:\s*`(\d+)`', replied_text)
    if not id_match and replied_caption:
        id_match = re.search(r'ID:\s*`(\d+)`', replied_caption)
    
    if not id_match:
        await update.message.reply_text("❌ Не удалось определить ID пользователя. Убедитесь, что вы отвечаете на сообщение с информацией о пользователе.")
        return
    
    user_id = int(id_match.group(1))
    admin = update.effective_user
    
    # Отправляем ответ пользователю
    try:
        if update.message.text and not update.message.text.startswith('/'):
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📨 **Ответ от поддержки:**\n\n{update.message.text}",
                parse_mode="Markdown"
            )
        elif update.message.photo:
            photo = update.message.photo[-1]
            caption = f"📨 **Ответ от поддержки**"
            if update.message.caption:
                caption += f"\n\n{update.message.caption}"
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo.file_id,
                caption=caption,
                parse_mode="Markdown"
            )
        elif update.message.document:
            caption = f"📨 **Ответ от поддержки**"
            if update.message.caption:
                caption += f"\n\n{update.message.caption}"
            await context.bot.send_document(
                chat_id=user_id,
                document=update.message.document.file_id,
                caption=caption,
                parse_mode="Markdown"
            )
        else:
            # Если это команда или другой тип - игнорируем
            return
        
        # Подтверждение админу
        await update.message.reply_text(f"✅ Ответ отправлен пользователю {user_id}")
        
        # Логируем
        send_log_http(f"📨 Ответ поддержки: {admin.id} -> {user_id}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")