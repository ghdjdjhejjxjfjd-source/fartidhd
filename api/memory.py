# api/memory.py
from datetime import datetime
from typing import List, Dict

# ✅ ИСПРАВЛЕНО: импортируем из postgres_db
from .postgres_db import get_db, return_db

# =========================
# MEMORY FUNCTIONS
# =========================
def mem_add(user_id: int, role: str, text: str) -> None:
    """Добавить сообщение в память чата"""
    conn = get_db()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_memory (user_id, role, text, created_at) VALUES (%s, %s, %s, %s)",
            (user_id, role, text, datetime.now()),
        )
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"❌ Error in mem_add: {e}")
    finally:
        return_db(conn)


def mem_get(user_id: int, limit: int = 24) -> List[Dict[str, str]]:
    """Получить последние сообщения из памяти чата"""
    conn = get_db()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT role, text
            FROM chat_memory
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
        cur.close()
        
        rows.reverse()
        out = []
        for r in rows:
            out.append({"role": r[0], "text": r[1]})
        return out
    except Exception as e:
        print(f"❌ Error in mem_get: {e}")
        return []
    finally:
        return_db(conn)


def mem_clear(user_id: int) -> None:
    """Очистить память чата пользователя"""
    conn = get_db()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_memory WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        print(f"🧹 Memory cleared for user {user_id}")
    except Exception as e:
        print(f"❌ Error in mem_clear: {e}")
    finally:
        return_db(conn)


def build_memory_prompt(history: List[Dict[str, str]], user_text: str) -> str:
    """Собрать промпт с историей для Groq"""
    lines = []
    lines.append("Conversation:")
    if history:
        for m in history:
            role = "User" if m.get("role") == "user" else "Assistant"
            lines.append(f"{role}: {m.get('text','')}")
    else:
        lines.append("(empty)")
    lines.append("")
    lines.append(f"User: {user_text}")
    lines.append("Assistant:")
    return "\n".join(lines)