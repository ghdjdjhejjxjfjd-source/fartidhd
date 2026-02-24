# api/payments_db.py
import os
import psycopg2
from psycopg2 import pool
from datetime import datetime
from typing import Dict, List, Optional

from .postgres_db import get_db, return_db

# Пакеты звезд (перенесены сюда)
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

def get_packages():
    return STAR_PACKAGES

def get_package(package_id: str):
    for p in STAR_PACKAGES:
        if p["id"] == package_id:
            return p
    return None

def init_payments_table():
    """Создать таблицы для звезд"""
    conn = get_db()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS star_balances (
                user_id BIGINT PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                total_purchased INTEGER DEFAULT 0,
                updated_at TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS star_transactions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                amount INTEGER NOT NULL,
                package_id TEXT,
                payment_id TEXT,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP
            )
        """)
        
        conn.commit()
        cur.close()
        print("✅ Payments tables initialized")
    except Exception as e:
        print(f"❌ Error initializing payments tables: {e}")
    finally:
        return_db(conn)

init_payments_table()

def get_balance(user_id: int) -> int:
    conn = get_db()
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM star_balances WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else 0
    except Exception as e:
        print(f"❌ Error getting balance: {e}")
        return 0
    finally:
        return_db(conn)

def add_stars(user_id: int, amount: int, package_id: Optional[str] = None):
    conn = get_db()
    if not conn:
        return
    
    try:
        now = datetime.now()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO star_balances (user_id, balance, total_purchased, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                balance = star_balances.balance + %s,
                total_purchased = star_balances.total_purchased + %s,
                updated_at = %s
        """, (user_id, amount, amount, now, amount, amount, now))
        
        cur.execute("""
            INSERT INTO star_transactions (user_id, amount, package_id, created_at)
            VALUES (%s, %s, %s, %s)
        """, (user_id, amount, package_id, now))
        
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"❌ Error adding stars: {e}")
    finally:
        return_db(conn)

def spend_stars(user_id: int, amount: int) -> bool:
    current = get_balance(user_id)
    if current < amount:
        return False
    
    conn = get_db()
    if not conn:
        return False
    
    try:
        now = datetime.now()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE star_balances
            SET balance = balance - %s, updated_at = %s
            WHERE user_id = %s
        """, (amount, now, user_id))
        
        cur.execute("""
            INSERT INTO star_transactions (user_id, amount, status, created_at)
            VALUES (%s, %s, 'spent', %s)
        """, (user_id, -amount, now))
        
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"❌ Error spending stars: {e}")
        return False
    finally:
        return_db(conn)

def get_top_users(limit: int = 10) -> List[tuple]:
    conn = get_db()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, balance, total_purchased 
            FROM star_balances 
            WHERE balance > 0 
            ORDER BY balance DESC 
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        print(f"❌ Error getting top users: {e}")
        return []
    finally:
        return_db(conn)

def reset_balance(user_id: int):
    conn = get_db()
    if not conn:
        return
    
    try:
        now = datetime.now()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE star_balances 
            SET balance = 0, updated_at = %s 
            WHERE user_id = %s
        """, (now, user_id))
        
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"❌ Error resetting balance: {e}")
    finally:
        return_db(conn)