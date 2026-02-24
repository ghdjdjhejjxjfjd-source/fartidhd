# api/db.py
import os
from datetime import datetime
from typing import Any, Dict, Tuple, Optional

# Импортируем PostgreSQL функции
from .postgres_db import (
    get_db, return_db, get_user, create_user
)

# Для обратной совместимости оставляем функцию db_conn
def db_conn():
    """Временная заглушка для совместимости"""
    print("⚠️ Используется устаревшая функция db_conn(), нужно обновить код")
    return None

# =========================
# ACCESS
# =========================
def set_free(user_id: int, value: bool) -> None:
    """Установить статус FREE"""
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    # Проверяем существует ли пользователь
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
    exists = cur.fetchone()
    
    if exists:
        cur.execute(
            "UPDATE users SET is_free = %s, updated_at = %s WHERE user_id = %s",
            (value, now, user_id)
        )
    else:
        cur.execute("""
            INSERT INTO users (user_id, is_free, is_blocked, updated_at, registered_at, ai_mode, style)
            VALUES (%s, %s, FALSE, %s, %s, 'fast', 'steps')
        """, (user_id, value, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def set_blocked(user_id: int, value: bool) -> None:
    """Заблокировать/разблокировать пользователя"""
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute(
        "UPDATE users SET is_blocked = %s, updated_at = %s WHERE user_id = %s",
        (value, now, user_id)
    )
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, is_free, is_blocked, updated_at, registered_at, ai_mode, style)
            VALUES (%s, FALSE, %s, %s, %s, 'fast', 'steps')
        """, (user_id, value, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def get_access(user_id: int) -> Dict[str, Any]:
    """Получить доступ пользователя"""
    return get_user(user_id)


def set_last_menu(user_id: int, chat_id: int, message_id: int) -> None:
    """Сохранить последнее меню"""
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users
        SET last_menu_chat_id = %s, last_menu_message_id = %s, updated_at = %s
        WHERE user_id = %s
    """, (chat_id, message_id, now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, last_menu_chat_id, last_menu_message_id, updated_at, registered_at, ai_mode, style)
            VALUES (%s, %s, %s, %s, %s, 'fast', 'steps')
        """, (user_id, chat_id, message_id, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def clear_last_menu(user_id: int) -> None:
    """Очистить последнее меню"""
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users
        SET last_menu_chat_id = NULL, last_menu_message_id = NULL, updated_at = %s
        WHERE user_id = %s
    """, (now, user_id))
    
    conn.commit()
    cur.close()
    return_db(conn)


def get_last_menu(user_id: int) -> Tuple[Optional[int], Optional[int]]:
    """Получить последнее меню"""
    user = get_user(user_id)
    return user.get("last_menu_chat_id"), user.get("last_menu_message_id")


# =========================
# ФУНКЦИИ ДЛЯ НАСТРОЕК
# =========================
def get_use_mini_app(user_id: int) -> bool:
    user = get_user(user_id)
    return user.get("use_mini_app", True)


def set_use_mini_app(user_id: int, value: bool) -> None:
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users
        SET use_mini_app = %s, updated_at = %s
        WHERE user_id = %s
    """, (value, now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, use_mini_app, updated_at, registered_at, ai_mode, style)
            VALUES (%s, %s, %s, %s, 'fast', 'steps')
        """, (user_id, value, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def get_user_persona(user_id: int) -> str:
    user = get_user(user_id)
    return user.get("persona", "friendly")


def set_user_persona(user_id: int, persona: str) -> None:
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users
        SET persona = %s, updated_at = %s
        WHERE user_id = %s
    """, (persona, now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, persona, updated_at, registered_at, ai_mode, style)
            VALUES (%s, %s, %s, %s, 'fast', 'steps')
        """, (user_id, persona, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def get_user_style(user_id: int) -> str:
    user = get_user(user_id)
    return user.get("style", "steps")


def set_user_style(user_id: int, style: str) -> None:
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users
        SET style = %s, updated_at = %s
        WHERE user_id = %s
    """, (style, now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, style, updated_at, registered_at, ai_mode)
            VALUES (%s, %s, %s, %s, 'fast')
        """, (user_id, style, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def get_user_lang(user_id: int) -> str:
    user = get_user(user_id)
    return user.get("lang", "ru")


def set_user_lang(user_id: int, lang: str) -> None:
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users
        SET lang = %s, updated_at = %s
        WHERE user_id = %s
    """, (lang, now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, lang, updated_at, registered_at, ai_mode, style)
            VALUES (%s, %s, %s, %s, 'fast', 'steps')
        """, (user_id, lang, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


# =========================
# ФУНКЦИИ ДЛЯ РЕЖИМА ИИ
# =========================
def get_ai_mode(user_id: int) -> str:
    user = get_user(user_id)
    return user.get("ai_mode", "fast")


def set_ai_mode(user_id: int, mode: str) -> None:
    if mode not in ["fast", "quality"]:
        mode = "fast"
    
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    # Получаем текущее значение счетчика
    cur.execute(
        "SELECT ai_mode_changes FROM users WHERE user_id = %s",
        (user_id,)
    )
    row = cur.fetchone()
    
    if row:
        cur.execute("""
            UPDATE users
            SET ai_mode = %s, ai_mode_changes = ai_mode_changes + 1, last_ai_mode_change = %s, updated_at = %s
            WHERE user_id = %s
        """, (mode, now, now, user_id))
    else:
        cur.execute("""
            INSERT INTO users (user_id, ai_mode, ai_mode_changes, last_ai_mode_change, updated_at, registered_at, style)
            VALUES (%s, %s, 1, %s, %s, %s, 'steps')
        """, (user_id, mode, now, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


async def get_ai_mode_changes(user_id: int) -> int:
    """Получить количество оставшихся смен режима (максимум 8)"""
    user = get_user(user_id)
    changes = user.get("ai_mode_changes", 0)
    last_change = user.get("last_ai_mode_change")
    
    # Если прошло больше 24 часов - сбрасываем
    if last_change:
        delta = datetime.now() - last_change
        if delta.days >= 1:
            # Сбрасываем счетчик
            conn = get_db()
            if conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET ai_mode_changes = 0 WHERE user_id = %s",
                    (user_id,)
                )
                conn.commit()
                cur.close()
                return_db(conn)
            return 8
    
    remaining = 8 - changes
    return max(0, remaining)


# =========================
# ФУНКЦИИ ДЛЯ СТАТИСТИКИ
# =========================
def increment_messages(user_id: int):
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users 
        SET total_messages = total_messages + 1, updated_at = %s
        WHERE user_id = %s
    """, (now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, total_messages, updated_at, registered_at, ai_mode, style)
            VALUES (%s, 1, %s, %s, 'fast', 'steps')
        """, (user_id, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def increment_images(user_id: int):
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users 
        SET total_images = total_images + 1, updated_at = %s
        WHERE user_id = %s
    """, (now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, total_images, updated_at, registered_at, ai_mode, style)
            VALUES (%s, 1, %s, %s, 'fast', 'steps')
        """, (user_id, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)


def add_stars_spent(user_id: int, amount: int):
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    now = datetime.now()
    
    cur.execute("""
        UPDATE users 
        SET total_stars_spent = total_stars_spent + %s, updated_at = %s
        WHERE user_id = %s
    """, (amount, now, user_id))
    
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO users (user_id, total_stars_spent, updated_at, registered_at, ai_mode, style)
            VALUES (%s, %s, %s, %s, 'fast', 'steps')
        """, (user_id, amount, now, now))
        
        cur.execute("""
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, now.date()))
    
    conn.commit()
    cur.close()
    return_db(conn)