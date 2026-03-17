# bot/support.py
from telegram import Update
from telegram.ext import ContextTypes
import os
import re
from datetime import datetime, timedelta

from .config import send_log_http

# ID группы поддержки (из .env)
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "0"))

# Хранилище для временных блокировок ТОЛЬКО ПОДДЕРЖКИ
support_blocks = {}

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало обращения в поддержку"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    # ==== ПРОВЕРКА БЛОКИРОВКИ ТОЛЬКО ДЛЯ ПОДДЕРЖКИ ====
    if uid in support_blocks:
        block_until = support_blocks[uid]
        if datetime.now() < block_until:
            remaining = block_until - datetime.now()
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            await query.message.edit_text(
                f"⛔ Доступ в поддержку заблокирован.\n"
                f"Осталось: {hours}ч {minutes}мин\n\n"
                f"Чат с ИИ и другие функции работают."
            )
            return
        else:
            del support_blocks[uid]
    
    # Текст с инструкцией
    text = (
        "💬 Поддержка\n\n"
        "Напиши сюда свой вопрос или проблему.\n"
        "Можешь отправить:\n"
        "• Текст\n"
        "• Фото\n"
        "• Видео\n"
        "• Файл\n"
        "• Голосовое\n\n"
        "Я передам твоё сообщение админам.\n"
        "Они ответят как можно скорее!"
    )
    
    await query.message.edit_text(text)
    
    # Запоминаем что пользователь в режиме поддержки
    context.user_data["in_support_mode"] = True
    print(f"✅ Режим поддержки включен для {uid}")

async def forward_to_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переслать сообщение пользователя в группу поддержки"""
    if not SUPPORT_GROUP_ID:
        print("❌ SUPPORT_GROUP_ID не настроен")
        await update.message.reply_text("❌ Служба поддержки временно недоступна")
        return
    
    user = update.effective_user
    uid = user.id
    
    # ==== ПРОВЕРКА БЛОКИРОВКИ ТОЛЬКО ДЛЯ ПОДДЕРЖКИ ====
    if uid in support_blocks:
        block_until = support_blocks[uid]
        if datetime.now() < block_until:
            remaining = block_until - datetime.now()
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            await update.message.reply_text(
                f"⛔ Вы заблокированы в поддержке.\n"
                f"Осталось: {hours}ч {minutes}мин"
            )
            return
        else:
            del support_blocks[uid]
    
    username = f"@{user.username}" if user.username else "—"
    first_name = user.first_name or "—"
    
    # Получаем текст сообщения или подпись
    message_text = ""
    if update.message.text:
        message_text = update.message.text
    elif update.message.caption:
        message_text = update.message.caption
    
    # Формируем шапку с информацией о пользователе
    header = (
        f"🆔 ID: {uid}\n"
        f"👤 Имя: {first_name}\n"
        f"📱 Юзернейм: {username}\n"
        f"📅 {update.message.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"———————————————\n\n"
    )
    
    # Формируем команды внизу (Telegram сделает их синими автоматически)
    commands = (
        f"\n\n———————————————\n"
        f"/reply {uid}\n"
        f"/block {uid}"
    )
    
    # ==== ОБРАБОТКА РАЗНЫХ ТИПОВ СООБЩЕНИЙ ====
    try:
        if update.message.text:
            full_text = header + update.message.text + commands
            await context.bot.send_message(
                chat_id=SUPPORT_GROUP_ID,
                text=full_text
            )
            
        elif update.message.photo:
            photo = update.message.photo[-1]
            caption = header + (update.message.caption or "") + commands
            await context.bot.send_photo(
                chat_id=SUPPORT_GROUP_ID,
                photo=photo.file_id,
                caption=caption
            )
            
        elif update.message.video:
            caption = header + (update.message.caption or "") + commands
            await context.bot.send_video(
                chat_id=SUPPORT_GROUP_ID,
                video=update.message.video.file_id,
                caption=caption
            )
            
        elif update.message.document:
            caption = header + (update.message.caption or "") + commands
            await context.bot.send_document(
                chat_id=SUPPORT_GROUP_ID,
                document=update.message.document.file_id,
                caption=caption
            )
            
        elif update.message.voice:
            # Для голосовых caption идет отдельно
            await context.bot.send_voice(
                chat_id=SUPPORT_GROUP_ID,
                voice=update.message.voice.file_id,
                caption=header + commands
            )
            
        elif update.message.audio:
            caption = header + (update.message.caption or "") + commands
            await context.bot.send_audio(
                chat_id=SUPPORT_GROUP_ID,
                audio=update.message.audio.file_id,
                caption=caption
            )
            
        elif update.message.sticker:
            # Для стикеров отправляем как есть + информация отдельно
            await context.bot.send_message(
                chat_id=SUPPORT_GROUP_ID,
                text=header + "📦 Стикер" + commands
            )
            await context.bot.send_sticker(
                chat_id=SUPPORT_GROUP_ID,
                sticker=update.message.sticker.file_id
            )
            
        elif update.message.animation:
            caption = header + (update.message.caption or "") + commands
            await context.bot.send_animation(
                chat_id=SUPPORT_GROUP_ID,
                animation=update.message.animation.file_id,
                caption=caption
            )
            
        elif update.message.video_note:
            # Видеосообщения (кружки)
            await context.bot.send_message(
                chat_id=SUPPORT_GROUP_ID,
                text=header + "📹 Видеосообщение" + commands
            )
            await context.bot.send_video_note(
                chat_id=SUPPORT_GROUP_ID,
                video_note=update.message.video_note.file_id
            )
        
        else:
            # Неподдерживаемый тип
            await context.bot.send_message(
                chat_id=SUPPORT_GROUP_ID,
                text=header + "⚠️ Неподдерживаемый тип сообщения" + commands
            )
        
        # Подтверждение пользователю
        await update.message.reply_text(
            "✅ Сообщение отправлено в поддержку.\n"
            "Ожидайте ответа."
        )
        
    except Exception as e:
        print(f"❌ Ошибка при отправке в поддержку: {e}")
        await update.message.reply_text(
            "❌ Ошибка при отправке. Попробуйте позже."
        )
        return
    
    # Выходим из режима поддержки после отправки
    context.user_data["in_support_mode"] = False
    
    # Логируем
    send_log_http(f"📨 Поддержка: {uid} -> {message_text[:50] if message_text else 'медиа'}")

async def handle_support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команд в группе поддержки"""
    
    # Проверяем что сообщение из группы поддержки
    if not SUPPORT_GROUP_ID or update.effective_chat.id != SUPPORT_GROUP_ID:
        return
    
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    admin = update.effective_user
    
    # ===== КОМАНДА /reply =====
    if text.startswith('/reply'):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            await update.message.reply_text("❌ Использование: /reply <id> <текст>")
            return
        
        try:
            user_id = int(parts[1])
            reply_text = parts[2]
            
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📨 Ответ от поддержки:\n\n{reply_text}"
            )
            
            await update.message.reply_text(f"✅ Ответ отправлен пользователю {user_id}")
            send_log_http(f"📨 Ответ поддержки: {admin.id} -> {user_id}")
            
        except ValueError:
            await update.message.reply_text("❌ Неверный ID")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    # ===== КОМАНДА /block (ТОЛЬКО ДЛЯ ПОДДЕРЖКИ) =====
    elif text.startswith('/block'):
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text("❌ Использование: /block <id> <часы>")
            return
        
        try:
            user_id = int(parts[1])
            hours = int(parts[2])
            
            if hours <= 0:
                await update.message.reply_text("❌ Часы должны быть больше 0")
                return
            
            # Устанавливаем временную блокировку ТОЛЬКО для поддержки
            block_until = datetime.now() + timedelta(hours=hours)
            support_blocks[user_id] = block_until
            
            await update.message.reply_text(
                f"✅ Пользователь {user_id} заблокирован в ПОДДЕРЖКЕ на {hours} часов\n"
                f"До: {block_until.strftime('%d.%m.%Y %H:%M')}\n"
                f"Остальные функции бота работают."
            )
            
            # Уведомляем пользователя
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⛔ Доступ в поддержку заблокирован на {hours} часов.\n"
                         f"Чат с ИИ и другие функции работают."
                )
            except:
                pass
            
            send_log_http(f"⛔ Блокировка поддержки: {admin.id} -> {user_id} на {hours}ч")
            
        except ValueError:
            await update.message.reply_text("❌ Неверный ID или часы")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    # ===== КОМАНДА /unblock (ТОЛЬКО ДЛЯ ПОДДЕРЖКИ) =====
    elif text.startswith('/unblock'):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("❌ Использование: /unblock <id>")
            return
        
        try:
            user_id = int(parts[1])
            
            # Убираем временную блокировку поддержки
            if user_id in support_blocks:
                del support_blocks[user_id]
                await update.message.reply_text(f"✅ Пользователь {user_id} разблокирован в поддержке")
                
                # Уведомляем пользователя
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="✅ Доступ в поддержку восстановлен."
                    )
                except:
                    pass
            else:
                await update.message.reply_text(f"❌ Пользователь {user_id} не заблокирован в поддержке")
            
            send_log_http(f"✅ Разблокировка поддержки: {admin.id} -> {user_id}")
            
        except ValueError:
            await update.message.reply_text("❌ Неверный ID")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")