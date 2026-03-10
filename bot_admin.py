# bot_admin.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import os
import re
import time
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps

from api import set_free, set_blocked, get_access
from bot.utils import send_fresh_menu, send_block_notice, update_user_menu
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

admin_command_usage = {}
COMMAND_LIMIT = 10
COMMAND_WINDOW = 60

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        
        if not user or not chat:
            return
        
        if ADMIN_USER_ID and user.id != ADMIN_USER_ID:
            await update.effective_message.reply_text("⛔ У вас нет прав администратора.")
            return
        
        if ADMIN_GROUP_ID and chat.id != ADMIN_GROUP_ID:
            await update.effective_message.reply_text("⛔ Эта команда работает только в админ-группе.")
            return
        
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
        
        command = update.message.text if update.message else "callback"
        print(f"👑 Админ {user.id} выполнил: {command}")
        
        return await func(update, context)
    return wrapper

def parse_user_id(arg: str) -> int:
    if not arg:
        return 0
    
    s = re.sub(r"[^\d\-]", "", arg.strip())
    
    try:
        user_id = int(s)
        if 1 <= user_id <= 9007199254740991:
            return user_id
        return 0
    except:
        return 0

def log_admin_action(action: str, admin_id: int, target_id: int, result: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] 👑 Админ {admin_id} -> {action} пользователя {target_id}: {result}"
    print(log_entry)
    
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

@admin_only
async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Использование: /balance <user_id>\n"
            "Пример: /balance 123456789"
        )
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id")
        return
    
    balance = get_balance(uid)
    a = get_access(uid)
    free_status = "✅ FREE" if a.get("is_free") else "💰 PAID"
    blocked_status = "⛔ BLOCKED" if a.get("is_blocked") else "✅ ACTIVE"
    
    await update.effective_message.reply_text(
        f"📊 Информация о пользователе {uid}\n\n"
        f"💰 Баланс: {balance} ⭐\n"
        f"💳 Статус: {free_status}\n"
        f"🔒 Блокировка: {blocked_status}"
    )

@admin_only
async def cmd_starstrans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        from payments import get_top_users
        
        limit = 10
        if context.args:
            limit = parse_user_id(context.args[0])
            if limit <= 0 or limit > 50:
                limit = 10
        
        top_users = get_top_users(limit)
        
        if not top_users:
            await update.effective_message.reply_text("📊 Нет данных о звездах")
            return
        
        text = "🏆 Топ пользователей по звездам:\n\n"
        for i, (user_id, balance, total) in enumerate(top_users, 1):
            text += f"{i}. ID: {user_id}\n   💰 {balance} ⭐ (всего куплено: {total})\n\n"
        
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                await update.effective_message.reply_text(part)
        else:
            await update.effective_message.reply_text(text)
            
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")

@admin_only
async def cmd_resetstars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("❌ Использование: /resetstars <user_id>")
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id")
        return
    
    try:
        old_balance = get_balance(uid)
        reset_balance(uid)
        
        log_admin_action("СБРОС БАЛАНСА", update.effective_user.id, uid, f"было {old_balance}⭐")
        
        await update.effective_message.reply_text(
            f"✅ Баланс пользователя {uid} сброшен\n"
            f"Было: {old_balance} ⭐\n"
            f"Стало: 0 ⭐"
        )
        
        await update_user_menu(context.bot, uid)
        
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")