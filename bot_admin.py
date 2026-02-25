# bot_admin.py (добавить в начало и исправить функции)

import os
import re
import time
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps

from api import set_free, set_blocked, get_access
from bot.handlers import send_fresh_menu, send_block_notice, update_user_menu
from payments import add_stars, get_balance, reset_balance

ADMIN_USER_ID_RAW = (os.getenv("ADMIN_USER_ID") or "0").strip()
try:
    ADMIN_USER_ID = int(ADMIN_USER_ID_RAW)
except Exception:
    ADMIN_USER_ID = 0

GROUP_ID_RAW = (os.getenv("TARGET_GROUP_ID") or os.getenv("LOG_GROUP_ID") or "0").strip()
try:
    ADMIN_GROUP_ID = int(GROUP_ID_RAW)
except Exception:
    ADMIN_GROUP_ID = 0

# Простая защита от брутфорса
admin_command_usage = {}
COMMAND_LIMIT = 10  # максимум команд в минуту
COMMAND_WINDOW = 60  # 60 секунд

def admin_only(func):
    """Декоратор для проверки прав админа и rate limiting"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        
        if not user or not chat:
            return
        
        # Проверка прав
        if ADMIN_USER_ID and user.id != ADMIN_USER_ID:
            await update.effective_message.reply_text("⛔ У вас нет прав администратора.")
            return
        
        if ADMIN_GROUP_ID and chat.id != ADMIN_GROUP_ID:
            await update.effective_message.reply_text("⛔ Эта команда работает только в админ-группе.")
            return
        
        # Rate limiting для команд
        now = time.time()
        key = f"{user.id}:{func.__name__}"
        
        if key in admin_command_usage:
            count, first = admin_command_usage[key]
            if now - first < COMMAND_WINDOW:
                if count >= COMMAND_LIMIT:
                    await update.effective_message.reply_text("⛔ Слишком много команд. Подождите минуту.")
                    return
                admin_command_usage[key] = (count + 1, first)
            else:
                admin_command_usage[key] = (1, now)
        else:
            admin_command_usage[key] = (1, now)
        
        # Логируем админ-команды
        command = update.message.text if update.message else "callback"
        print(f"👑 Админ {user.id} выполнил: {command}")
        
        return await func(update, context)
    return wrapper

def parse_user_id(arg: str) -> int:
    """Безопасный парсинг user_id"""
    if not arg:
        return 0
    
    # Удаляем все кроме цифр и минуса
    s = re.sub(r"[^\d\-]", "", arg.strip())
    
    try:
        user_id = int(s)
        # Проверка что это реальный Telegram ID
        if 1 <= user_id <= 9007199254740991:
            return user_id
        return 0
    except:
        return 0

def log_admin_action(action: str, admin_id: int, target_id: int, result: str):
    """Логирование действий админа"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] 👑 Админ {admin_id} -> {action} пользователя {target_id}: {result}"
    print(log_entry)
    
    # Можно также писать в специальный лог-файл
    try:
        with open("admin_actions.log", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except:
        pass

@admin_only
async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    c = update.effective_chat
    await update.effective_message.reply_text(
        f"✅ Вы админ\n"
        f"ID: {u.id}\n"
        f"Чат: {c.id}\n"
        f"Имя: {u.full_name}"
    )

async def _push_menu(context: ContextTypes.DEFAULT_TYPE, uid: int):
    """Обновить меню пользователя"""
    try:
        a = get_access(uid)
        if a.get("is_blocked"):
            await send_block_notice(context.bot, uid)
        else:
            await send_fresh_menu(
                context.bot,
                uid,
                "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
            )
    except Exception as e:
        print(f"❌ Ошибка обновления меню для {uid}: {e}")

@admin_only
async def cmd_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Использование: /free <user_id>\n"
            "Пример: /free 123456789"
        )
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id. Должно быть число.")
        return

    try:
        set_free(uid, True)
        await _push_menu(context, uid)
        await update_user_menu(context.bot, uid)

        a = get_access(uid)
        log_admin_action("FREE включен", update.effective_user.id, uid, "успешно")
        
        await update.effective_message.reply_text(
            f"✅ FREE режим включен для {uid}\n"
            f"Статус: {a}"
        )
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")
        log_admin_action("FREE включен", update.effective_user.id, uid, f"ошибка: {e}")

@admin_only
async def cmd_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Использование: /paid <user_id>\n"
            "Пример: /paid 123456789"
        )
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id. Должно быть число.")
        return

    try:
        set_free(uid, False)
        await _push_menu(context, uid)
        await update_user_menu(context.bot, uid)

        a = get_access(uid)
        log_admin_action("PAID включен", update.effective_user.id, uid, "успешно")
        
        await update.effective_message.reply_text(
            f"✅ PAID режим включен для {uid}\n"
            f"Статус: {a}"
        )
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")
        log_admin_action("PAID включен", update.effective_user.id, uid, f"ошибка: {e}")

@admin_only
async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Использование: /block <user_id>\n"
            "Пример: /block 123456789"
        )
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id. Должно быть число.")
        return

    try:
        set_blocked(uid, True)
        await _push_menu(context, uid)
        await update_user_menu(context.bot, uid)

        log_admin_action("БЛОКИРОВКА", update.effective_user.id, uid, "успешно")
        
        await update.effective_message.reply_text(f"⛔ Пользователь {uid} заблокирован")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")
        log_admin_action("БЛОКИРОВКА", update.effective_user.id, uid, f"ошибка: {e}")

@admin_only
async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Использование: /unblock <user_id>\n"
            "Пример: /unblock 123456789"
        )
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id. Должно быть число.")
        return

    try:
        set_blocked(uid, False)
        await _push_menu(context, uid)
        await update_user_menu(context.bot, uid)

        log_admin_action("РАЗБЛОКИРОВКА", update.effective_user.id, uid, "успешно")
        
        await update.effective_message.reply_text(f"✅ Пользователь {uid} разблокирован")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")
        log_admin_action("РАЗБЛОКИРОВКА", update.effective_user.id, uid, f"ошибка: {e}")

@admin_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Использование: /status <user_id>\n"
            "Пример: /status 123456789"
        )
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id. Должно быть число.")
        return
    
    try:
        a = get_access(uid)
        balance = get_balance(uid)
        
        status_text = (
            f"📊 Статус пользователя {uid}\n\n"
            f"💰 Баланс: {balance} ⭐\n"
            f"💳 Режим: {'FREE' if a.get('is_free') else 'PAID'}\n"
            f"🔒 Блокировка: {'ДА' if a.get('is_blocked') else 'НЕТ'}\n"
            f"🎭 Характер: {a.get('persona', 'friendly')}\n"
            f"📝 Стиль: {a.get('style', 'steps')}\n"
            f"🌐 Язык: {a.get('lang', 'ru')}\n"
            f"⚡ Режим ИИ: {a.get('ai_mode', 'fast')}\n"
            f"💬 Сообщений: {a.get('total_messages', 0)}\n"
            f"🖼 Картинок: {a.get('total_images', 0)}"
        )
        
        await update.effective_message.reply_text(status_text)
        
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")

@admin_only
async def cmd_addstars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.effective_message.reply_text(
            "❌ Использование: /addstars <user_id> <amount>\n"
            "Пример: /addstars 123456789 500"
        )
        return
    
    uid = parse_user_id(context.args[0])
    amount = parse_user_id(context.args[1])
    
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id")
        return
    
    if not amount or amount <= 0:
        await update.effective_message.reply_text("❌ Количество звезд должно быть положительным числом")
        return
    
    if amount > 100000:
        await update.effective_message.reply_text("❌ Слишком много звезд (макс 100000)")
        return
    
    try:
        add_stars(uid, amount, "admin")
        new_balance = get_balance(uid)
        
        log_admin_action(f"ДОБАВЛЕНО {amount}⭐", update.effective_user.id, uid, "успешно")
        
        await update.effective_message.reply_text(
            f"✅ Добавлено {amount} ⭐ пользователю {uid}\n"
            f"💰 Новый баланс: {new_balance} ⭐"
        )
        
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"✨ Вам начислено {amount} звезд!\n"
                     f"💰 Текущий баланс: {new_balance} ⭐"
            )
        except Exception as e:
            print(f"⚠️ Не удалось уведомить пользователя {uid}: {e}")
            
        await update_user_menu(context.bot, uid)
            
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")
        log_admin_action(f"ДОБАВЛЕНО {amount}⭐", update.effective_user.id, uid, f"ошибка: {e}")

# ... остальные команды аналогично ...