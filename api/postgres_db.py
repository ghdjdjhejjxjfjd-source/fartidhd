# api/postgres_db.py
import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Any, Dict, Tuple, Optional, List

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем пул соединений (для производительности)
connection_pool = None

if DATABASE_URL:
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # минимум соединений
            20,  # максимум соединений
            DATABASE_URL
        )
        print("✅ PostgreSQL connection pool created")
    except Exception as e:
        print(f"❌ Failed to create connection pool: {e}")

def get_db():
    """Получить соединение из пула"""
    if connection_pool:
        return connection_pool.getconn()
    return None

def return_db(conn):
    """Вернуть соединение в пул"""
    if connection_pool and conn:
        connection_pool.putconn(conn)

def init_db():
    """Создать таблицы если их нет"""
    conn = get_db()
    if not conn:
        print("❌ No database connection")
        return
    
    cur = conn.cursor()
    
    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            is_free BOOLEAN DEFAULT FALSE,
            is_blocked BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP,
            last_menu_chat_id BIGINT,
            last_menu_message_id BIGINT,
            use_mini_app BOOLEAN DEFAULT TRUE,
            persona TEXT DEFAULT 'friendly',
            style TEXT DEFAULT 'steps',
            lang TEXT DEFAULT 'ru',
            registered_at TIMESTAMP,
            total_messages INTEGER DEFAULT 0,
            total_images INTEGER DEFAULT 0,
            total_stars_spent INTEGER DEFAULT 0,
            ai_mode TEXT DEFAULT 'fast',
            ai_mode_changes INTEGER DEFAULT 0,
            last_ai_mode_change TIMESTAMP
        )
    """)
    
    # Таблица лимитов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_limits (
            user_id BIGINT PRIMARY KEY,
            last_reset_date DATE,
            groq_persona_changes INTEGER DEFAULT 0,
            groq_style_changes INTEGER DEFAULT 0,
            openai_style_changes INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Таблица памяти чата
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_memory (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    cur.close()
    return_db(conn)
    print("✅ PostgreSQL tables initialized")

# Инициализация
init_db()

# =========================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
# =========================

def get_user(user_id: int) -> Dict[str, Any]:
    """Получить данные пользователя"""
    conn = get_db()
    if not conn:
        return {}
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return_db(conn)
    
    if not row:
        return {
            "user_id": user_id,
            "is_free": False,
            "is_blocked": False,
            "use_mini_app": True,
            "persona": "friendly",
            "style": "steps",
            "lang": "ru",
            "total_messages": 0,
            "total_images": 0,
            "total_stars_spent": 0,
            "ai_mode": "fast",
            "ai_mode_changes": 0,
        }
    
    return dict(row)

def create_user(user_id: int) -> None:
    """Создать нового пользователя"""
    conn = get_db()
    if not conn:
        return
    
    now = datetime.now()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (
            user_id, registered_at, updated_at, style, ai_mode
        ) VALUES (%s, %s, %s, 'steps', 'fast')
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, now, now))
    
    cur.execute("""
        INSERT INTO user_limits (user_id, last_reset_date)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)