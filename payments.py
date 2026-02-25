# payments.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С БЛОКИРОВКАМИ
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from contextlib import contextmanager

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
CACHE_TTL = 60
balance_cache = {}

@contextmanager
def db_connection():
    """Безопасное соединение с БД с блокировкой"""
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

def init_db():
    with db_connection() as conn:
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
        
        # Индексы для скорости
        cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON star_transactions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON star_transactions(created_at)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_balances_balance ON star_balances(balance)")
        
        conn.commit()

init_db()

def get_balance(user_id: int) -> int:
    now = time.time()
    
    # Проверка кэша
    if user_id in balance_cache:
        balance, timestamp = balance_cache[user_id]
        if now - timestamp < CACHE_TTL:
            return balance
    
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM star_balances WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
    
    balance = row[0] if row else 0
    balance_cache[user_id] = (balance, now)
    return balance

def add_stars(user_id: int, amount: int, package_id: Optional[str] = None):
    with db_connection() as conn:
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
    
    if user_id in balance_cache:
        del balance_cache[user_id]

def spend_stars(user_id: int, amount: int) -> bool:
    current = get_balance(user_id)
    
    if current < amount:
        return False
    
    with db_connection() as conn:
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
    
    if user_id in balance_cache:
        del balance_cache[user_id]
    
    return True

def get_packages() -> List[Dict]:
    return STAR_PACKAGES

def get_package(package_id: str) -> Optional[Dict]:
    for p in STAR_PACKAGES:
        if p["id"] == package_id:
            return p
    return None

def get_top_users(limit: int = 10) -> List[tuple]:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, balance, total_purchased 
            FROM star_balances 
            WHERE balance > 0 
            ORDER BY balance DESC 
            LIMIT ?
        """, (limit,))
        return cur.fetchall()

def reset_balance(user_id: int):
    with db_connection() as conn:
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cur.execute("""
            UPDATE star_balances 
            SET balance = 0, updated_at = ? 
            WHERE user_id = ?
        """, (now, user_id))
        
        conn.commit()
    
    if user_id in balance_cache:
        del balance_cache[user_id]

def cleanup_old_transactions(days=30):
    with db_connection() as conn:
        cur = conn.cursor()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        
        cur.execute("""
            DELETE FROM star_transactions 
            WHERE created_at < ? AND status = 'completed'
        """, (cutoff,))
        
        deleted = cur.rowcount
        conn.commit()
        print(f"🧹 Удалено старых транзакций: {deleted}")
        return deleted