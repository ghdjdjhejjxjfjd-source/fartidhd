import sqlite3
from datetime import datetime
from typing import Any, Dict, Tuple, Optional

from .config import DB_PATH

def db_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def db_init():
    con = db_conn()
    cur = con.cursor()
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
            openai_style_changes INTEGER DEFAULT 0
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
    con.commit()
    con.close()

db_init()

def _ensure_columns():
    con = db_conn()
    cur = con.cursor()
    columns_to_add = [
        "last_menu_chat_id INTEGER",
        "last_menu_message_id INTEGER",
        "use_mini_app INTEGER DEFAULT 1",
        "persona TEXT DEFAULT 'friendly'",
        "style TEXT DEFAULT 'steps'",
        "lang TEXT DEFAULT 'ru'",
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
    con.commit()
    con.close()

_ensure_columns()

def set_free(user_id: int, value: bool) -> None:
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, is_free, is_blocked, updated_at, registered_at, ai_mode, style)
            VALUES (?, ?, 0, ?, ?, 'fast', 'steps')
            """,
            (user_id, 1 if value else 0, now, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def set_blocked(user_id: int, value: bool) -> None:
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, is_free, is_blocked, updated_at, registered_at, ai_mode, style)
            VALUES (?, 0, ?, ?, ?, 'fast', 'steps')
            """,
            (user_id, 1 if value else 0, now, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def get_access(user_id: int) -> Dict[str, Any]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        SELECT is_free, is_blocked, updated_at, last_menu_chat_id, 
               last_menu_message_id, use_mini_app, persona, style, lang,
               registered_at, total_messages, total_images, total_stars_spent,
               ai_mode, ai_mode_changes, last_ai_mode_change
        FROM access WHERE user_id=?
        """,
        (user_id,),
    )
    row = cur.fetchone()
    con.close()
    
    if not row:
        return {
            "user_id": user_id,
            "is_free": False,
            "is_blocked": False,
            "updated_at": None,
            "last_menu_chat_id": None,
            "last_menu_message_id": None,
            "use_mini_app": True,
            "persona": "friendly",
            "style": "steps",
            "lang": "ru",
            "registered_at": None,
            "total_messages": 0,
            "total_images": 0,
            "total_stars_spent": 0,
            "ai_mode": "fast",
            "ai_mode_changes": 0,
            "last_ai_mode_change": None,
        }
    
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
        "registered_at": row[9],
        "total_messages": row[10] or 0,
        "total_images": row[11] or 0,
        "total_stars_spent": row[12] or 0,
        "ai_mode": row[13] if row[13] else "fast",
        "ai_mode_changes": row[14] or 0,
        "last_ai_mode_change": row[15],
    }

def set_last_menu(user_id: int, chat_id: int, message_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
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
                               last_menu_chat_id, last_menu_message_id, registered_at, ai_mode, style)
            VALUES (?, 0, 0, ?, ?, ?, ?, 'fast', 'steps')
            """,
            (user_id, now, chat_id, message_id, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def clear_last_menu(user_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        UPDATE access
        SET last_menu_chat_id = NULL, last_menu_message_id = NULL, updated_at = ?
        WHERE user_id = ?
        """,
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
    )
    con.commit()
    con.close()

def get_last_menu(user_id: int) -> Tuple[Optional[int], Optional[int]]:
    a = get_access(user_id)
    return a.get("last_menu_chat_id"), a.get("last_menu_message_id")

def get_use_mini_app(user_id: int) -> bool:
    a = get_access(user_id)
    return a.get("use_mini_app", True)

def set_use_mini_app(user_id: int, value: bool) -> None:
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, use_mini_app, updated_at, registered_at, ai_mode, style)
            VALUES (?, ?, ?, ?, 'fast', 'steps')
            """,
            (user_id, 1 if value else 0, now, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def get_user_persona(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("persona", "friendly")

def set_user_persona(user_id: int, persona: str) -> None:
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, persona, updated_at, registered_at, ai_mode, style)
            VALUES (?, ?, ?, ?, 'fast', 'steps')
            """,
            (user_id, persona, now, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def get_user_style(user_id: int) -> str:
    """Получить стиль ответа пользователя"""
    a = get_access(user_id)
    return a.get("style", "steps")

def set_user_style(user_id: int, style: str) -> None:
    """Установить стиль ответа пользователя"""
    con = db_conn()
    cur = con.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        """
        UPDATE access
        SET style = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (style, now, user_id),
    )
    if cur.rowcount == 0:
        cur.execute(
            """
            INSERT INTO access (user_id, style, updated_at, registered_at, ai_mode)
            VALUES (?, ?, ?, ?, 'fast')
            """,
            (user_id, style, now, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def get_user_lang(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("lang", "ru")

def set_user_lang(user_id: int, lang: str) -> None:
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, lang, updated_at, registered_at, ai_mode, style)
            VALUES (?, ?, ?, ?, 'fast', 'steps')
            """,
            (user_id, lang, now, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def get_ai_mode(user_id: int) -> str:
    a = get_access(user_id)
    return a.get("ai_mode", "fast")

def set_ai_mode(user_id: int, mode: str) -> None:
    if mode not in ["fast", "quality"]:
        mode = "fast"
    con = db_conn()
    cur = con.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        """
        UPDATE access
        SET ai_mode = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (mode, now, user_id),
    )
    if cur.rowcount == 0:
        cur.execute(
            """
            INSERT INTO access (user_id, ai_mode, updated_at, registered_at, style)
            VALUES (?, ?, ?, ?, 'steps')
            """,
            (user_id, mode, now, now)
        )
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def check_and_reset_limits(user_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute(
        "SELECT last_reset_date FROM user_limits WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    if not row:
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date, groq_persona_changes, groq_style_changes, openai_style_changes)
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
    con.commit()
    con.close()

def get_user_limits(user_id: int) -> Dict[str, Any]:
    check_and_reset_limits(user_id)
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        SELECT groq_persona_changes, groq_style_changes, openai_style_changes
        FROM user_limits WHERE user_id = ?
        """,
        (user_id,)
    )
    row = cur.fetchone()
    con.close()
    if not row:
        return {
            "groq_persona": 0,
            "groq_style": 0,
            "openai_style": 0,
            "groq_persona_max": 5,
            "groq_style_max": 5,
            "openai_style_max": 7
        }
    return {
        "groq_persona": row[0] or 0,
        "groq_style": row[1] or 0,
        "openai_style": row[2] or 0,
        "groq_persona_max": 5,
        "groq_style_max": 5,
        "openai_style_max": 7
    }

def increment_groq_persona(user_id: int) -> bool:
    con = db_conn()
    cur = con.cursor()
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
        con.commit()
        con.close()
        return True
    con.close()
    return False

def increment_groq_style(user_id: int) -> bool:
    con = db_conn()
    cur = con.cursor()
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
        con.commit()
        con.close()
        return True
    con.close()
    return False

def increment_openai_style(user_id: int) -> bool:
    con = db_conn()
    cur = con.cursor()
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
        con.commit()
        con.close()
        return True
    con.close()
    return False

def increment_messages(user_id: int):
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, total_messages, updated_at, registered_at, ai_mode, style)
            VALUES (?, 1, ?, ?, 'fast', 'steps')
        """, (user_id, now, now))
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def increment_images(user_id: int):
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, total_images, updated_at, registered_at, ai_mode, style)
            VALUES (?, 1, ?, ?, 'fast', 'steps')
        """, (user_id, now, now))
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def add_stars_spent(user_id: int, amount: int):
    con = db_conn()
    cur = con.cursor()
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
            INSERT INTO access (user_id, total_stars_spent, updated_at, registered_at, ai_mode, style)
            VALUES (?, ?, ?, ?, 'fast', 'steps')
        """, (user_id, amount, now, now))
        cur.execute(
            """
            INSERT INTO user_limits (user_id, last_reset_date)
            VALUES (?, ?)
            """,
            (user_id, now[:10])
        )
    con.commit()
    con.close()

def get_ai_mode_changes(user_id: int) -> int:
    """Получить количество оставшихся смен режима (максимум 8)"""
    conn = db_conn()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT ai_mode_changes, last_ai_mode_change FROM access WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return 8
    
    changes = row[0] or 0
    last_change = row[1]
    
    if last_change:
        last_date = datetime.strptime(last_change, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        delta = now - last_date
        if delta.days >= 1:
            con = db_conn()
            cur = con.cursor()
            cur.execute(
                "UPDATE access SET ai_mode_changes = 0 WHERE user_id = ?",
                (user_id,)
            )
            con.commit()
            con.close()
            return 8
    
    remaining = 8 - changes
    return max(0, remaining)