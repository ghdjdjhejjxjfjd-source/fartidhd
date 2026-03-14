import os
import time
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update

from bot.handlers import start, on_button
from bot.old_handlers import handle_message  # ← ИСПРАВЛЕНО: явно берем из old_handlers
from bot_admin import (
    cmd_whoami,
    cmd_free,
    cmd_paid,
    cmd_block,
    cmd_unblock,
    cmd_status,
    cmd_addstars,
    cmd_balance,
    cmd_starstrans,
    cmd_resetstars,
)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()

async def post_init(app: Application):
    await app.bot.set_my_commands([
        ("start", "🚀 Запустить бота"),
    ])
    
    group_id_raw = (os.getenv("TARGET_GROUP_ID") or os.getenv("LOG_GROUP_ID") or "0").strip()
    try:
        group_id = int(group_id_raw)
        if group_id:
            await app.bot.set_my_commands(
                [
                    ("whoami", "👤 Проверка админа"),
                    ("free", "⭐ Сделать бесплатным: /free <id>"),
                    ("paid", "💰 Сделать платным: /paid <id>"),
                    ("block", "⛔ Заблокировать: /block <id>"),
                    ("unblock", "✅ Разблокировать: /unblock <id>"),
                    ("status", "ℹ️ Статус: /status <id>"),
                    ("addstars", "✨ Добавить звезды: /addstars <id> <кол-во>"),
                    ("balance", "💎 Баланс: /balance <id>"),
                    ("starstrans", "🏆 Топ звезд: /starstrans [лимит]"),
                    ("resetstars", "🔄 Сбросить баланс: /resetstars <id>"),
                ],
                scope={"type": "chat", "chat_id": group_id}
            )
            print(f"✅ Админ-команды установлены для группы {group_id}")
    except Exception as e:
        print(f"⚠️ Не удалось установить админ-команды: {e}")

async def error_handler(update: Update, context):
    try:
        if update and update.effective_user:
            user_id = update.effective_user.id
            print(f"❌ Ошибка для пользователя {user_id}: {context.error}")
            
            if "Conflict" in str(context.error):
                print("🔄 Конфликт, перезапуск...")
            elif "Timed out" in str(context.error):
                print("🔄 Таймаут, переподключение...")
        else:
            print(f"❌ Ошибка: {context.error}")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

def start_bot():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    # ТЕПЕРЬ ТОЛЬКО ОДИН ОБРАБОТЧИК - правильный, с проверкой флага
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("free", cmd_free))
    app.add_handler(CommandHandler("paid", cmd_paid))
    app.add_handler(CommandHandler("block", cmd_block))
    app.add_handler(CommandHandler("unblock", cmd_unblock))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("addstars", cmd_addstars))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("starstrans", cmd_starstrans))
    app.add_handler(CommandHandler("resetstars", cmd_resetstars))
    
    app.add_error_handler(error_handler)

    print("🤖 Telegram bot started")
    print("✅ В личке: только /start")
    print("✅ В админ-группе: все команды")

    while True:
        try:
            print("🔄 Запуск polling...")
            app.run_polling(
                stop_signals=None, 
                close_loop=False,
                drop_pending_updates=True,
                allowed_updates=['message', 'callback_query'],
                poll_interval=1.0,
                timeout=30
            )
            break
        except Exception as e:
            print(f"❌ Ошибка polling: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
            continue