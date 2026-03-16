import os
import threading
import time
import sys
import signal

from api import api
from bot_runner import start_bot

# Railway / ENV
PORT = int(os.getenv("PORT", "8000"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Флаг для отслеживания состояния
bot_running = False

def run_api():
    """Запуск Flask API"""
    try:
        api.run(
            host="0.0.0.0",
            port=PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ API error: {e}")

def signal_handler(sig, frame):
    """Обработка сигналов завершения"""
    print("\n👋 Получен сигнал завершения, останавливаемся...")
    sys.exit(0)

def main():
    global bot_running
    
    print("🚀 Запуск приложения...")
    print(f"📡 PORT: {PORT}")
    
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запускаем API в отдельном потоке
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print("✅ API сервер запущен")
    
    # Небольшая задержка
    time.sleep(2)
    
    # Запускаем бота (только если есть токен)
    if BOT_TOKEN:
        try:
            bot_running = True
            start_bot()
        except Exception as e:
            print(f"❌ Ошибка бота: {e}")
            bot_running = False
    else:
        print("⚠️ BOT_TOKEN не задан, бот не запущен")
    
    # Держим процесс живым
    while True:
        time.sleep(60)
        if not bot_running:
            print("⏳ Бот не работает, но API продолжает работу")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Остановка по Ctrl+C...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Фатальная ошибка: {e}")
        time.sleep(60)