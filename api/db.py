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
            lang TEXT DEFAULT 'ru'
        )
        """
    )
    # ✅ память чата
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,               -- "user" | "assistant"
            text TEXT NOT NULL,
            created_at TEXT
        )
        """
    )
    con.commit()
    con.close()


db_init()


def _ensure_columns():
    """На случай если таблица была создана раньше без колонок."""
    con = db_conn()
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE access ADD COLUMN last_menu_chat_id INTEGER")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN last_menu_message_id INTEGER")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN use_mini_app INTEGER DEFAULT 1")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN persona TEXT DEFAULT 'friendly'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN lang TEXT DEFAULT 'ru'")
    except Exception:
        pass
    con.commit()
    con.close()


_ensure_columns()


# =========================
# ACCESS
# =========================
def set_free(user_id: int, value: bool) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO access (user_id, is_free, is_blocked, updated_at)
        VALUES (?, ?, COALESCE((SELECT is_blocked FROM access WHERE user_id=?), 0), ?)
        ON CONFLICT(user_id) DO UPDATE SET
            is_free=excluded.is_free,
            updated_at=excluded.updated_at
        """,
        (user_id, 1 if value else 0, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    con.commit()
    con.close()


def set_blocked(user_id: int, value: bool) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO access (user_id, is_free, is_blocked, updated_at)
        VALUES (?, COALESCE((SELECT is_free FROM access WHERE user_id=?), 0), ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            is_blocked=excluded.is_blocked,
            updated_at=excluded.updated_at
        """,
        (user_id, user_id, 1 if value else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    con.commit()
    con.close()


def get_access(user_id: int) -> Dict[str, Any]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT is_free, is_blocked, updated_at, last_menu_chat_id, last_menu_message_id, use_mini_app, persona, lang FROM access WHERE user_id=?",
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
            "lang": "ru",
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
        "lang": row[7] if row[7] else "ru",
    }


def set_last_menu(user_id: int, chat_id: int, message_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO access (user_id, is_free, is_blocked, updated_at, last_menu_chat_id, last_menu_message_id)
        VALUES (?, COALESCE((SELECT is_free FROM access WHERE user_id=?), 0),
                COALESCE((SELECT is_blocked FROM access WHERE user_id=?), 0),
                ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            last_menu_chat_id=excluded.last_menu_chat_id,
            last_menu_message_id=excluded.last_menu_message_id,
            updated_at=excluded.updated_at
        """,
        (
            user_id,
            user_id,
            user_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            chat_id,
            message_id,
        ),
    )
    con.commit()
    con.close()


def clear_last_menu(user_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        UPDATE access
        SET last_menu_chat_id=NULL, last_menu_message_id=NULL, updated_at=?
        WHERE user_id=?
        """,
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
    )
    con.commit()
    con.close()


def get_last_menu(user_id: int) -> Tuple[Optional[int], Optional[int]]:
    a = get_access(user_id)
    return a.get("last_menu_chat_id"), a.get("last_menu_message_id")


# =========================
# НОВЫЕ ФУНКЦИИ
# =========================
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
        cur.execute(
            """
            INSERT INTO access (user_id, use_mini_app, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, 1 if value else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
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
        cur.execute(
            """
            INSERT INTO access (user_id, persona, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, persona, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
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
        cur.execute(
            """
            INSERT INTO access (user_id, lang, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, lang, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
    con.commit()
    con.close()