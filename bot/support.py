# bot/support.py - ПОЛНАЯ ВЕРСИЯ С ЛОКАЛИЗАЦИЕЙ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os
import re
import json
from datetime import datetime, timedelta

from .config import send_log_http
from .locales import get_text
from .utils import send_fresh_menu

# ID группы поддержки (из .env)
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "0"))

# Хранилище для временных блокировок ТОЛЬКО ПОДДЕРЖКИ
support_blocks = {}

# Файл для сохранения блокировок
BLOCKS_FILE = "support_blocks.json"


def load_blocks():
    """Загрузить блокировки из файла"""
    global support_blocks
    try:
        if os.path.exists(BLOCKS_FILE):
            with open(BLOCKS_FILE, 'r') as f:
                data = json.load(f)
                for uid, until_str in data.items():
                    support_blocks[int(uid)] = datetime.fromisoformat(until_str)
            print(f"✅ Загружено {len(support_blocks)} блокировок поддержки")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки блокировок: {e}")


def save_blocks():
    """Сохранить блокировки в файл"""
    try:
        data = {}
        for uid, until in support_blocks.items():
            if datetime.now() < until:
                data[str(uid)] = until.isoformat()
        
        with open(BLOCKS_FILE, 'w') as f:
            json.dump(data, f)
        print(f"✅ Сохранено {len(data)} блокировок поддержки")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения блокировок: {e}")


def cleanup_blocks():
    """Очистить истекшие блокировки"""
    global support_blocks
    now = datetime.now()
    expired = [uid for uid, until in support_blocks.items() if now >= until]
    for uid in expired:
        del support_blocks[uid]
    if expired:
        print(f"🧹 Очищено {len(expired)} истекших блокировок")
        save_blocks()


# Загружаем блокировки при старте
load_blocks()
cleanup_blocks()


async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало обращения в поддержку"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    cleanup_blocks()
    
    # Проверка блокировки
    if uid in support_blocks:
        block_until = support_blocks[uid]
        if datetime.now() < block_until:
            remaining = block_until - datetime.now()
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            text = get_text(uid, "support_blocked_msg").format(hours=hours, minutes=minutes)
            await query.message.edit_text(text)
            return
        else:
            del support_blocks[uid]
            save_blocks()
    
    text = get_text(uid, "support_text")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(uid, "back_btn"), callback_data="exit_support")]
    ])
    
    sent_msg = await query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )
    
    context.user_data["support_message_id"] = sent_msg.message_id
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
    
    cleanup_blocks()
    
    # Проверка блокировки
    if uid in support_blocks:
        block_until = support_blocks[uid]
        if datetime.now() < block_until:
            remaining = block_until - datetime.now()
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            text = get_text(uid, "support_blocked_msg").format(hours=hours, minutes=minutes)
            await update.message.reply_text(text)
            return
        else:
            del support_blocks[uid]
            save_blocks()
    
    if not update.message.text:
        await update.message.reply_text(get_text(uid, "support_only_text"))
        return
    
    username = f"@{user.username}" if user.username else "—"
    first_name = user.first_name or "—"
    
    header = (
        f"🆔 ID: {uid}\n"
        f"👤 Имя: {first_name}\n"
        f"📱 Юзернейм: {username}\n"
        f"📅 {update.message.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"———————————————\n\n"
    )
    
    commands = f"\n\n———————————————\n/reply {uid}"
    
    try:
        full_text = header + update.message.text + commands
        await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=full_text
        )
        
        # Удаляем сообщение-инструкцию
        if "support_message_id" in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=uid,
                    message_id=context.user_data["support_message_id"]
                )
                print(f"✅ Инструкция удалена для {uid}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить инструкцию: {e}")
            finally:
                del context.user_data["support_message_id"]
        
        # Отправляем подтверждение
        await context.bot.send_message(
            chat_id=uid,
            text=get_text(uid, "support_sent")
        )
        
        # Отправляем/обновляем меню
        await send_fresh_menu(context.bot, uid)
        
    except Exception as e:
        print(f"❌ Ошибка при отправке в поддержку: {e}")
        await update.message.reply_text(get_text(uid, "support_error"))
        return
    
    context.user_data["in_support_mode"] = False
    send_log_http(f"📨 Поддержка: {uid} -> {update.message.text[:50]}")


async def handle_support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команд в группе поддержки"""
    
    if not SUPPORT_GROUP_ID or update.effective_chat.id != SUPPORT_GROUP_ID:
        return
    
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    admin = update.effective_user
    
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
            
            block_until = datetime.now() + timedelta(hours=hours)
            support_blocks[user_id] = block_until
            save_blocks()
            
            await update.message.reply_text(
                f"✅ Пользователь {user_id} заблокирован в ПОДДЕРЖКЕ на {hours} часов\n"
                f"До: {block_until.strftime('%d.%m.%Y %H:%M')}\n"
                f"Остальные функции бота работают."
            )
            
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
    
    elif text.startswith('/unblock'):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("❌ Использование: /unblock <id>")
            return
        
        try:
            user_id = int(parts[1])
            
            if user_id in support_blocks:
                del support_blocks[user_id]
                save_blocks()
                await update.message.reply_text(f"✅ Пользователь {user_id} разблокирован в поддержке")
                
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