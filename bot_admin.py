import os
import re
from telegram import Update
from telegram.ext import ContextTypes

from api import set_free, set_blocked, get_access
from bot_handlers import send_fresh_menu, send_block_notice, update_user_menu
from payments import add_stars, get_balance

ADMIN_USER_ID_RAW = (os.getenv("ADMIN_USER_ID") or "0").strip()
try:
    ADMIN_USER_ID = int(ADMIN_USER_ID_RAW)
except Exception:
    ADMIN_USER_ID = 0

# где разрешены админ-команды (в группе логов)
GROUP_ID_RAW = (os.getenv("TARGET_GROUP_ID") or os.getenv("LOG_GROUP_ID") or "0").strip()
try:
    ADMIN_GROUP_ID = int(GROUP_ID_RAW)
except Exception:
    ADMIN_GROUP_ID = 0


def is_admin(update: Update) -> bool:
    u = update.effective_user
    c = update.effective_chat
    if not u or not c:
        return False
    if ADMIN_USER_ID and u.id != ADMIN_USER_ID:
        return False
    if ADMIN_GROUP_ID and c.id != ADMIN_GROUP_ID:
        return False
    return True


def parse_user_id(arg: str) -> int:
    s = (arg or "").strip()
    s = re.sub(r"[^\d\-]", "", s)
    try:
        return int(s)
    except Exception:
        return 0


async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    u = update.effective_user
    await update.effective_message.reply_text(f"✅ ты админ\nuser_id: {u.id}")


async def _push_menu(context: ContextTypes.DEFAULT_TYPE, uid: int):
    a = get_access(uid)
    if a.get("is_blocked"):
        await send_block_notice(context.bot, uid)
    else:
        await send_fresh_menu(
            context.bot,
            uid,
            "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
        )


async def cmd_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    if not context.args:
        await update.effective_message.reply_text("Использование: /free <user_id>")
        return
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Не вижу user_id. Нужно число.")
        return

    set_free(uid, True)
    await _push_menu(context, uid)
    await update_user_menu(context.bot, uid)  # Обновляем меню

    a = get_access(uid)
    await update.effective_message.reply_text(f"✅ FREE включен для {uid}\n{a}")


async def cmd_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    if not context.args:
        await update.effective_message.reply_text("Использование: /paid <user_id>")
        return
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Не вижу user_id. Нужно число.")
        return

    set_free(uid, False)
    await _push_menu(context, uid)
    await update_user_menu(context.bot, uid)  # Обновляем меню

    a = get_access(uid)
    await update.effective_message.reply_text(f"✅ Теперь платно для {uid}\n{a}")


async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    if not context.args:
        await update.effective_message.reply_text("Использование: /block <user_id>")
        return
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Не вижу user_id. Нужно число.")
        return

    set_blocked(uid, True)
    await _push_menu(context, uid)
    await update_user_menu(context.bot, uid)  # Обновляем меню

    a = get_access(uid)
    await update.effective_message.reply_text(f"⛔ Заблокирован {uid}\n{a}")


async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    if not context.args:
        await update.effective_message.reply_text("Использование: /unblock <user_id>")
        return
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Не вижу user_id. Нужно число.")
        return

    set_blocked(uid, False)
    await _push_menu(context, uid)
    await update_user_menu(context.bot, uid)  # Обновляем меню

    a = get_access(uid)
    await update.effective_message.reply_text(f"✅ Разблокирован {uid}\n{a}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    if not context.args:
        await update.effective_message.reply_text("Использование: /status <user_id>")
        return
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Не вижу user_id. Нужно число.")
        return
    a = get_access(uid)
    await update.effective_message.reply_text(f"ℹ️ Статус {uid}\n{a}")


# =========================
#   НОВЫЕ КОМАНДЫ ДЛЯ ЗВЕЗД
# =========================

async def cmd_addstars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить звезды пользователю: /addstars <user_id> <amount>"""
    if not is_admin(update):
        return
    
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
    
    try:
        add_stars(uid, amount, "admin")
        new_balance = get_balance(uid)
        
        await update.effective_message.reply_text(
            f"✅ Добавлено {amount} ⭐ пользователю {uid}\n"
            f"💰 Новый баланс: {new_balance} ⭐"
        )
        
        # Отправляем уведомление пользователю
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"✨ Вам начислено {amount} звезд!\n"
                     f"💰 Текущий баланс: {new_balance} ⭐"
            )
        except:
            pass
            
        # ✅ Обновляем меню пользователя
        await update_user_menu(context.bot, uid)
            
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс пользователя: /balance <user_id>"""
    if not is_admin(update):
        return
    
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


async def cmd_starstrans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать топ пользователей по звездам: /starstrans [limit]"""
    if not is_admin(update):
        return
    
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


async def cmd_resetstars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сбросить баланс пользователя: /resetstars <user_id>"""
    if not is_admin(update):
        return
    
    if not context.args:
        await update.effective_message.reply_text("❌ Использование: /resetstars <user_id>")
        return
    
    uid = parse_user_id(context.args[0])
    if not uid:
        await update.effective_message.reply_text("❌ Неверный user_id")
        return
    
    try:
        from payments import reset_balance
        
        old_balance = get_balance(uid)
        reset_balance(uid)
        
        await update.effective_message.reply_text(
            f"✅ Баланс пользователя {uid} сброшен\n"
            f"Было: {old_balance} ⭐\n"
            f"Стало: 0 ⭐"
        )
        
        # ✅ Обновляем меню пользователя
        await update_user_menu(context.bot, uid)
        
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Ошибка: {e}")


# Функции для payments.py
def get_top_users(limit: int = 10):
    """Получить топ пользователей по звездам"""
    import sqlite3
    from payments import DB_PATH
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, balance, total_purchased 
        FROM star_balances 
        WHERE balance > 0 
        ORDER BY balance DESC 
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def reset_balance(user_id: int):
    """Сбросить баланс пользователя"""
    import sqlite3
    from payments import DB_PATH
    from datetime import datetime
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cur.execute("""
        UPDATE star_balances 
        SET balance = 0, updated_at = ? 
        WHERE user_id = ?
    """, (now, user_id))
    
    conn.commit()
    conn.close()