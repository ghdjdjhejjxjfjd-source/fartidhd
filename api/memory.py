# api/memory.py - ИСПРАВЛЕННАЯ ПОЛНАЯ ВЕРСИЯ
from datetime import datetime
from typing import List, Dict

from .db import db_connection

def mem_add(user_id: int, role: str, text: str) -> None:
    """Добавить сообщение в память чата"""
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_memory (user_id, role, text, created_at) VALUES (?, ?, ?, ?)",
            (user_id, role, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

def mem_get(user_id: int, limit: int = 24) -> List[Dict[str, str]]:
    """Получить последние сообщения из памяти чата"""
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT role, text
            FROM chat_memory
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
    
    out = []
    for r in reversed(rows):
        out.append({"role": r[0], "text": r[1]})
    return out

def mem_clear(user_id: int) -> None:
    """Очистить память чата пользователя"""
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_memory WHERE user_id=?", (user_id,))
    print(f"🧹 Memory cleared for user {user_id}")

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