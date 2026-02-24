# payments.py
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

# Пакеты звезд (USD)
STAR_PACKAGES = [
    {
        "id": "starter",
        "name": "Starter",
        "stars": 100,
        "price_usd": 1.99,
        "price_per_star": 0.0199,
        "discount": 0,
        "popular": False,
    },
    {
        "id": "basic",
        "name": "Basic",
        "stars": 500,
        "price_usd": 8.99,
        "price_per_star": 0.0179,
        "discount": 10,
        "popular": False,
    },
    {
        "id": "popular",
        "name": "Popular",
        "stars": 1000,
        "price_usd": 16.99,
        "price_per_star": 0.0169,
        "discount": 15,
        "popular": True,
    },
    {
        "id": "pro",
        "name": "Pro",
        "stars": 2500,
        "price_usd": 39.99,
        "price_per_star": 0.0159,
        "discount": 20,
        "popular": False,
    },
    {
        "id": "premium",
        "name": "Premium",
        "stars": 5000,
        "price_usd": 74.99,
        "price_per_star": 0.0149,
        "discount": 25,
        "popular": False,
    },
    {
        "id": "ultimate",
        "name": "Ultimate",
        "stars": 10000,
        "price_usd": 139.99,
        "price_per_star": 0.0139,
        "discount": 30,
        "popular": False,
    },
]

DB_PATH = "stars.db"

def init_db():
    """Инициализация базы данных звезд"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS star_balances (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            total_purchased INTEGER DEFAULT 0,
            updated_at TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS star_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            package_id TEXT,
            payment_id TEXT,
            status TEXT DEFAULT 'completed',
            created_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Star database initialized")

# Инициализация
init_db()

def get_balance(user_id: int) -> int:
    """Получить баланс звезд"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM star_balances WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def add_stars(user_id: int, amount: int, package_id: Optional[str] = None):
    """Добавить звезды"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cur.execute("""
        INSERT INTO star_balances (user_id, balance, total_purchased, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            balance = balance + ?,
            total_purchased = total_purchased + ?,
            updated_at = ?
    """, (user_id, amount, amount, now, amount, amount, now))
    
    cur.execute("""
        INSERT INTO star_transactions (user_id, amount, package_id, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, amount, package_id, now))
    
    conn.commit()
    conn.close()

def spend_stars(user_id: int, amount: int) -> bool:
    """Списать звезды"""
    current = get_balance(user_id)
    
    if current < amount:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cur.execute("""
        UPDATE star_balances
        SET balance = balance - ?, updated_at = ?
        WHERE user_id = ?
    """, (amount, now, user_id))
    
    cur.execute("""
        INSERT INTO star_transactions (user_id, amount, status, created_at)
        VALUES (?, ?, 'spent', ?)
    """, (user_id, -amount, now))
    
    conn.commit()
    conn.close()
    return True

def get_packages() -> List[Dict]:
    """Получить все пакеты"""
    return STAR_PACKAGES

def get_package(package_id: str) -> Optional[Dict]:
    """Получить пакет по ID"""
    for p in STAR_PACKAGES:
        if p["id"] == package_id:
            return p
    return None

def get_top_users(limit: int = 10) -> List[tuple]:
    """Получить топ пользователей по звездам"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, balance, total_purchased 
        FROM star_balances 
        WHERE balance > 0 
        ORDER BY balance DESC 
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def reset_balance(user_id: int):
    """Сбросить баланс пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cur.execute("""
        UPDATE star_balances 
        SET balance = 0, updated_at = ? 
        WHERE user_id = ?
    """, (now, user_id))
    
    conn.commit()
    conn.close()