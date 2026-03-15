import os
import threading
import time
import sys
import signal

from api import api
from bot_runner import start_bot

# Railway / ENV
PORT = int(os.getenv("PORT", "8000"))
HEALTH_CHECK_INTERVAL = 60  # Проверка здоровья каждую минуту

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
        time.sleep(5)

def health_check():
    """Фоновый поток для проверки здоровья"""
    while True:
        time.sleep(HEALTH_CHECK_INTERVAL)
        print(f"✅ Health check: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def signal_handler(sig, frame):
    """Обработка сигналов завершения"""
    print("\n👋 Получен сигнал завершения, останавливаемся...")
    sys.exit(0)

def main():
    print("🚀 Запуск приложения...")
    print(f"📡 PORT: {PORT}")
    print(f"⏱️  Таймауты: connect=30s, read=30s, pool=30s")
    
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запускаем API в отдельном потоке
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print("✅ API сервер запущен")

    # Запускаем поток проверки здоровья
    health_thread = threading.Thread(target=health_check, daemon=True)
    health_thread.start()
    
    # Небольшая задержка чтобы API успел запуститься
    time.sleep(3)

    # Запускаем бота с защитой от таймаутов
    max_bot_retries = 3
    for attempt in range(max_bot_retries):
        try:
            print(f"🔄 Попытка запуска бота {attempt + 1}/{max_bot_retries}")
            start_bot()
            break
        except Exception as e:
            print(f"❌ Ошибка бота (попытка {attempt + 1}): {e}")
            if attempt < max_bot_retries - 1:
                wait_time = 10 * (attempt + 1)  # Увеличиваем задержку с каждой попыткой
                print(f"⏳ Ждем {wait_time} секунд перед следующей попыткой...")
                time.sleep(wait_time)
            else:
                print("❌ Бот не запустился после всех попыток")
                print("🔄 API продолжает работать")
    
    # Держим процесс живым
    print("✅ Приложение запущено, ждем сигналов...")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Остановка по Ctrl+C...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Фатальная ошибка: {e}")
        # Не даем процессу умереть
        while True:
            time.sleep(60)