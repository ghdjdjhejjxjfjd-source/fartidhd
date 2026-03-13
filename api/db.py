# api/db.py - ПОЛНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ (с блокировкой при 0/8)
import sqlite3
import time
import threading
import warnings
from datetime import datetime
from typing import Any, Dict, Tuple, Optional
from contextlib import contextmanager

from .config import DB_PATH

db_lock = threading.Lock()

@contextmanager
def db_connection():
    """Безопасное соединение с БД с retry при блокировке"""
    conn = None
    for attempt in range(3):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5.0)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise
        finally:
            if conn:
                conn.close()

# ВРЕМЕННАЯ ФУНКЦИЯ ДЛЯ СОВМЕСТИМОСТИ
def db_conn():
    """Старая функция для обратной совместимости"""
    warnings.warn("db_conn устарела, используй db_connection()", DeprecationWarning)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def db_init():
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS access (
                user_id INTEGER PRIMARY KEY,
                is_free INTEGER DEFAULT 0,
                is_blocked INTEGER DEFAULT 0,
                updated_at TEXT,
                last_menu_chat_id INTEGER,
                last_menu_message_id INTEGER,
                use_mini_app INTEGER DEFAULT 1,
                persona TEXT DEFAULT 'friendly',
                style TEXT DEFAULT 'steps',
                lang TEXT DEFAULT 'ru',
                ai_lang TEXT DEFAULT 'ru',
                registered_at TEXT,
                total_messages INTEGER DEFAULT 0,
                total_images INTEGER DEFAULT 0,
                total_stars_spent INTEGER DEFAULT 0,
                ai_mode TEXT DEFAULT 'fast',
                ai_mode_changes INTEGER DEFAULT 0,
                last_ai_mode_change TEXT
            )
            """
        )
        
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_limits (
                user_id INTEGER PRIMARY KEY,
                last_reset_date TEXT,
                groq_persona_changes INTEGER DEFAULT 0,
                groq_style_changes INTEGER DEFAULT 0,
                openai_style_changes INTEGER DEFAULT 0,
                ai_mode_changes INTEGER DEFAULT 0,
                last_ai_mode_change TEXT,
                FOREIGN KEY (user_id) REFERENCES access(user_id)
            )
            """
        )
        
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT
            )
            """
        )

db_init()

DEFAULT_ACCESS = {
    "user_id": 0,
    "is_free": False,
    "is_blocked": False,
    "updated_at": None,
    "last_menu_chat_id": None,
    "last_menu_message_id": None,
    "use_mini_app": True,
    "persona": "friendly",
    "style": "steps",
    "lang": "ru",
    "ai_lang": "ru",
    "registered_at": None,
    "total_messages": 0,
    "total_images": 0,
    "total_stars_spent": 0,
    "ai_mode": "fast",
    "ai_mode_changes": 0,
    "last_ai_mode_change": None,
}

def _ensure_columns():
    with db_connection() as conn:
        cur = conn.cursor()
        
        columns_to_add = [
            "last_menu_chat_id INTEGER",
            "last_menu_message_id INTEGER",
            "use_mini_app INTEGER DEFAULT 1",
            "persona TEXT DEFAULT 'friendly'",
            "style TEXT DEFAULT 'steps'",
            "lang TEXT DEFAULT 'ru'",
            "ai_lang TEXT DEFAULT 'ru'",
            "registered_at TEXT",
            "total_messages INTEGER DEFAULT 0",
            "total_images INTEGER DEFAULT 0",
            "total_stars_spent INTEGER DEFAULT 0",
            "ai_mode TEXT DEFAULT 'fast'",
            "ai_mode_changes INTEGER DEFAULT 0",
            "last_ai_mode_change TEXT"
        ]
        
        for col in columns_to_add:
            try:
                cur.execute(f"ALTER TABLE access ADD COLUMN {col}")
            except Exception:
                pass

_ensure_columns()

# =========================
# ACCESS
# =========================
def set_free(user_id: int, value: bool) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM access WHERE user_id = ?", (user_id,))
        exists = cur.fetchone()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if exists:
            cur.execute(
                "UPDATE access SET is_free = ?, updated_at = ? WHERE user_id = ?",
                (1 if value else 0, now, user_id)
            )
        else:
            cur.execute(
                """
                INSERT INTO access (user_id, is_free, is_blocked, updated_at, registered_at, ai_mode, style, ai_lang, lang, persona)
                VALUES (?, ?, 0, ?, ?, 'fast', 'steps', 'ru', 'ru', 'friendly')
                """,
                (user_id, 1 if value else 0, now, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def set_blocked(user_id: int, value: bool) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute(
            """
            UPDATE access
            SET is_blocked = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (1 if value else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        if cur.rowcount == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO access (user_id, is_free, is_blocked, updated_at, registered_at, ai_mode, style, ai_lang, lang, persona)
                VALUES (?, 0, ?, ?, ?, 'fast', 'steps', 'ru', 'ru', 'friendly')
                """,
                (user_id, 1 if value else 0, now, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def get_access(user_id: int) -> Dict[str, Any]:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT is_free, is_blocked, updated_at, last_menu_chat_id, 
                   last_menu_message_id, use_mini_app, persona, style, lang, ai_lang,
                   registered_at, total_messages, total_images, total_stars_spent,
                   ai_mode, ai_mode_changes, last_ai_mode_change
            FROM access WHERE user_id=?
            """,
            (user_id,),
        )
        row = cur.fetchone()
    
    if not row:
        result = DEFAULT_ACCESS.copy()
        result["user_id"] = user_id
        return result
    
    return {
        "user_id": user_id,
        "is_free": bool(row[0]),
        "is_blocked": bool(row[1]),
        "updated_at": row[2],
        "last_menu_chat_id": row[3],
        "last_menu_message_id": row[4],
        "use_mini_app": bool(row[5]) if row[5] is not None else True,
        "persona": row[6] if row[6] else "friendly",
        "style": row[7] if row[7] else "steps",
        "lang": row[8] if row[8] else "ru",
        "ai_lang": row[9] if row[9] else "ru",
        "registered_at": row[10],
        "total_messages": row[11] or 0,
        "total_images": row[12] or 0,
        "total_stars_spent": row[13] or 0,
        "ai_mode": row[14] if row[14] else "fast",
        "ai_mode_changes": row[15] or 0,
        "last_ai_mode_change": row[16],
    }

def set_last_menu(user_id: int, chat_id: int, message_id: int) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute(
            """
            UPDATE access
            SET last_menu_chat_id = ?, last_menu_message_id = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (chat_id, message_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        
        if cur.rowcount == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO access (user_id, is_free, is_blocked, updated_at, 
                                   last_menu_chat_id, last_menu_message_id, registered_at, 
                                   ai_mode, style, ai_lang, lang, persona)
                VALUES (?, 0, 0, ?, ?, ?, ?, 'fast', 'steps', 'ru', 'ru', 'friendly')
                """,
                (user_id, now, chat_id, message_id, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def clear_last_menu(user_id: int) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE access
            SET last_menu_chat_id = NULL, last_menu_message_id = NULL, updated_at = ?
            WHERE user_id = ?
            """,
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )

def get_last_menu(user_id: int) -> Tuple[Optional[int], Optional[int]]:
    a = get_access(user_id)
    return a.get("last_menu_chat_id"), a.get("last_menu_message_id")

def mem_clear_last(user_id: int) -> None:
    """Удалить последнее сообщение пользователя (при ошибке)"""
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM chat_memory 
            WHERE id = (
                SELECT id FROM chat_memory 
                WHERE user_id = ? AND role = 'user' 
                ORDER BY id DESC LIMIT 1
            )
        """, (user_id,))

# =========================
# ФУНКЦИИ ДЛЯ НАСТРОЕК
# =========================
def get_use_mini_app(user_id: int) -> bool:
    a = get_access(user_id)
    return a.get("use_mini_app", True)

def set_use_mini_app(user_id: int, value: bool) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE access
            SET use_mini_app = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (1 if value else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        if cur.rowcount == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO access (user_id, use_mini_app, updated_at, registered_at, 
                                   ai_mode, style, ai_lang, lang, persona)
                VALUES (?, ?, ?, ?, 'fast', 'steps', 'ru', 'ru', 'friendly')
                """,
                (user_id, 1 if value else 0, now, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def get_user_persona(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("persona", "friendly")

def set_user_persona(user_id: int, persona: str) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE access
            SET persona = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (persona, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        if cur.rowcount == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO access (user_id, persona, updated_at, registered_at, 
                                   ai_mode, style, ai_lang, lang)
                VALUES (?, ?, ?, ?, 'fast', 'steps', 'ru', 'ru')
                """,
                (user_id, persona, now, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def get_user_style(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("style", "steps")

def set_user_style(user_id: int, style: str) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE access
            SET style = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (style, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        if cur.rowcount == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO access (user_id, style, updated_at, registered_at, 
                                   ai_mode, ai_lang, lang, persona)
                VALUES (?, ?, ?, ?, 'fast', 'ru', 'ru', 'friendly')
                """,
                (user_id, style, now, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def get_user_lang(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("lang", "ru")

def set_user_lang(user_id: int, lang: str) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE access
            SET lang = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (lang, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        if cur.rowcount == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO access (user_id, lang, updated_at, registered_at, 
                                   ai_mode, style, ai_lang, persona)
                VALUES (?, ?, ?, ?, 'fast', 'steps', 'ru', 'friendly')
                """,
                (user_id, lang, now, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

# =========================
# НОВЫЕ ФУНКЦИИ ДЛЯ ЯЗЫКА ИИ
# =========================
def get_user_ai_lang(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("ai_lang", "ru")

def set_user_ai_lang(user_id: int, lang: str) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE access
            SET ai_lang = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (lang, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        if cur.rowcount == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO access (user_id, ai_lang, updated_at, registered_at, 
                                   ai_mode, style, lang, persona)
                VALUES (?, ?, ?, ?, 'fast', 'steps', 'ru', 'friendly')
                """,
                (user_id, lang, now, now)
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

# =========================
# ФУНКЦИИ ДЛЯ РЕЖИМА ИИ - ИСПРАВЛЕНО (с проверкой лимита)
# =========================
def get_ai_mode(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("ai_mode", "fast")

def set_ai_mode(user_id: int, mode: str) -> bool:
    """Возвращает True если режим успешно изменен, False если лимит исчерпан"""
    if mode not in ["fast", "quality"]:
        mode = "fast"
    
    with db_connection() as conn:
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Проверяем существует ли пользователь
        cur.execute("SELECT user_id FROM access WHERE user_id = ?", (user_id,))
        exists = cur.fetchone()
        
        if exists:
            # Получаем текущее количество изменений
            cur.execute(
                "SELECT ai_mode_changes, last_ai_mode_change FROM access WHERE user_id = ?",
                (user_id,)
            )
            row = cur.fetchone()
            changes = row[0] or 0
            last_change = row[1]
            
            # Проверяем не прошли ли сутки
            if last_change:
                try:
                    last_date = datetime.strptime(last_change, "%Y-%m-%d %H:%M:%S")
                    now_date = datetime.now()
                    delta = now_date - last_date
                    if delta.days >= 1:
                        # Сбрасываем счетчик
                        changes = 0
                except:
                    pass
            
            # Проверяем лимит
            if changes >= 8:
                return False  # Лимит исчерпан
            
            # Обновляем существующего пользователя
            cur.execute(
                """
                UPDATE access
                SET ai_mode = ?, 
                    ai_mode_changes = COALESCE(ai_mode_changes, 0) + 1, 
                    last_ai_mode_change = ?, 
                    updated_at = ?
                WHERE user_id = ?
                """,
                (mode, now, now, user_id)
            )
        else:
            # Создаем нового пользователя
            cur.execute(
                """
                INSERT INTO access (
                    user_id, ai_mode, ai_mode_changes, last_ai_mode_change, 
                    updated_at, registered_at, style, ai_lang, lang, persona
                )
                VALUES (?, ?, 1, ?, ?, ?, 'steps', 'ru', 'ru', 'friendly')
                """,
                (user_id, mode, now, now, now)
            )
            
            # Создаем запись в user_limits
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )
    
    return True  # Успешно изменено

async def get_ai_mode_changes(user_id: int) -> int:
    with db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute(
            "SELECT ai_mode_changes, last_ai_mode_change FROM access WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
    
    if not row:
        return 8
    
    changes = row[0] or 0
    last_change = row[1]
    
    # Проверяем не прошли ли сутки
    if last_change:
        try:
            last_date = datetime.strptime(last_change, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            delta = now - last_date
            if delta.days >= 1:
                # Сбрасываем счетчик
                with db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE access SET ai_mode_changes = 0 WHERE user_id = ?",
                        (user_id,)
                    )
                return 8
        except:
            pass
    
    remaining = 8 - changes
    return max(0, remaining)

# =========================
# ФУНКЦИИ ДЛЯ ЛИМИТОВ - ИСПРАВЛЕНО
# =========================
def check_and_reset_limits(user_id: int) -> None:
    with db_connection() as conn:
        cur = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cur.execute(
            "SELECT last_reset_date FROM user_limits WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        
        if not row:
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date, groq_persona_changes, groq_style_changes, openai_style_changes)
                VALUES (?, ?, 0, 0, 0)
                """,
                (user_id, today)
            )
        elif row[0] != today:
            cur.execute(
                """
                UPDATE user_limits
                SET last_reset_date = ?,
                    groq_persona_changes = 0,
                    groq_style_changes = 0,
                    openai_style_changes = 0
                WHERE user_id = ?
                """,
                (today, user_id)
            )

def get_user_limits(user_id: int) -> Dict[str, Any]:
    check_and_reset_limits(user_id)
    
    with db_connection() as conn:
        cur = conn.cursor()
        
        # Получаем лимиты из user_limits
        cur.execute(
            """
            SELECT groq_persona_changes, groq_style_changes, openai_style_changes
            FROM user_limits WHERE user_id = ?
            """,
            (user_id,)
        )
        limits_row = cur.fetchone()
        
        # Получаем ai_mode_changes из access
        cur.execute(
            """
            SELECT ai_mode_changes, last_ai_mode_change
            FROM access WHERE user_id = ?
            """,
            (user_id,)
        )
        access_row = cur.fetchone()
    
    # Базовая структура с максимальными значениями
    result = {
        "groq_persona": 0,
        "groq_style": 0,
        "openai_style": 0,
        "ai_mode_changes": 0,
        "last_ai_mode_change": None,
        "groq_persona_max": 5,
        "groq_style_max": 5,
        "openai_style_max": 7,
        "ai_mode_changes_max": 8  # Максимум смен режима в день
    }
    
    # Заполняем из user_limits если есть
    if limits_row:
        result["groq_persona"] = limits_row[0] or 0
        result["groq_style"] = limits_row[1] or 0
        result["openai_style"] = limits_row[2] or 0
    
    # Заполняем из access если есть
    if access_row:
        # Проверяем не прошли ли сутки
        changes = access_row[0] or 0
        last_change = access_row[1]
        
        if last_change:
            try:
                last_date = datetime.strptime(last_change, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                delta = now - last_date
                if delta.days >= 1:
                    changes = 0  # Сбрасываем для отображения
            except:
                pass
        
        result["ai_mode_changes"] = changes
        result["last_ai_mode_change"] = last_change
    
    return result

def increment_groq_persona(user_id: int) -> bool:
    with db_connection() as conn:
        cur = conn.cursor()
        
        check_and_reset_limits(user_id)
        
        cur.execute(
            "SELECT groq_persona_changes FROM user_limits WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        
        if not row or row[0] < 5:
            cur.execute(
                """
                UPDATE user_limits
                SET groq_persona_changes = groq_persona_changes + 1
                WHERE user_id = ?
                """,
                (user_id,)
            )
            return True
    
    return False

def increment_groq_style(user_id: int) -> bool:
    with db_connection() as conn:
        cur = conn.cursor()
        
        check_and_reset_limits(user_id)
        
        cur.execute(
            "SELECT groq_style_changes FROM user_limits WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        
        if not row or row[0] < 5:
            cur.execute(
                """
                UPDATE user_limits
                SET groq_style_changes = groq_style_changes + 1
                WHERE user_id = ?
                """,
                (user_id,)
            )
            return True
    
    return False

def increment_openai_style(user_id: int) -> bool:
    with db_connection() as conn:
        cur = conn.cursor()
        
        check_and_reset_limits(user_id)
        
        cur.execute(
            "SELECT openai_style_changes FROM user_limits WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        
        if not row or row[0] < 7:
            cur.execute(
                """
                UPDATE user_limits
                SET openai_style_changes = openai_style_changes + 1
                WHERE user_id = ?
                """,
                (user_id,)
            )
            return True
    
    return False

# =========================
# ФУНКЦИИ ДЛЯ СТАТИСТИКИ
# =========================
def increment_messages(user_id: int):
    with db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM access WHERE user_id = ?", (user_id,))
        exists = cur.fetchone()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if exists:
            cur.execute("""
                UPDATE access 
                SET total_messages = total_messages + 1,
                    updated_at = ?
                WHERE user_id = ?
            """, (now, user_id))
        else:
            cur.execute("""
                INSERT INTO access (user_id, total_messages, updated_at, registered_at, 
                                   ai_mode, style, ai_lang, lang, persona)
                VALUES (?, 1, ?, ?, 'fast', 'steps', 'ru', 'ru', 'friendly')
            """, (user_id, now, now))
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def increment_images(user_id: int):
    with db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM access WHERE user_id = ?", (user_id,))
        exists = cur.fetchone()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if exists:
            cur.execute("""
                UPDATE access 
                SET total_images = total_images + 1,
                    updated_at = ?
                WHERE user_id = ?
            """, (now, user_id))
        else:
            cur.execute("""
                INSERT INTO access (user_id, total_images, updated_at, registered_at, 
                                   ai_mode, style, ai_lang, lang, persona)
                VALUES (?, 1, ?, ?, 'fast', 'steps', 'ru', 'ru', 'friendly')
            """, (user_id, now, now))
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )

def add_stars_spent(user_id: int, amount: int):
    with db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM access WHERE user_id = ?", (user_id,))
        exists = cur.fetchone()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if exists:
            cur.execute("""
                UPDATE access 
                SET total_stars_spent = total_stars_spent + ?,
                    updated_at = ?
                WHERE user_id = ?
            """, (amount, now, user_id))
        else:
            cur.execute("""
                INSERT INTO access (user_id, total_stars_spent, updated_at, registered_at, 
                                   ai_mode, style, ai_lang, lang, persona)
                VALUES (?, ?, ?, ?, 'fast', 'steps', 'ru', 'ru', 'friendly')
            """, (user_id, amount, now, now))
            cur.execute(
                """
                INSERT OR IGNORE INTO user_limits (user_id, last_reset_date)
                VALUES (?, ?)
                """,
                (user_id, now[:10])
            )