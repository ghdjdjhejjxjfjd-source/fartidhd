import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, Tuple, Optional, List

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from groq_client import ask_groq
from payments import get_balance, add_stars, spend_stars, get_packages

# ✅ Проверка Stability AI
try:
    from stability_client import generate_image, generate_image_from_image
    STABILITY_AVAILABLE = True
except ImportError:
    STABILITY_AVAILABLE = False
    print("⚠️ Stability AI not available - stability_client.py not found")
except Exception as e:
    STABILITY_AVAILABLE = False
    print(f"⚠️ Stability AI import error: {e}")

# Переменные окружения
BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()

# Группа для логов
GROUP_ID_RAW = (os.getenv("TARGET_GROUP_ID") or os.getenv("LOG_GROUP_ID") or "0").strip()
try:
    GROUP_ID = int(GROUP_ID_RAW)
except Exception:
    GROUP_ID = 0

# Путь к БД (SQLite)
DB_PATH = os.getenv("ACCESS_DB_PATH") or "access.db"

# Flask приложение
api = Flask(__name__)
CORS(api, origins=["https://fayrat11.github.io", "https://*.github.io"])

# =========================
# LOG FUNCTION
# =========================
def send_log_to_group(text: str):
    """Отправить лог в Telegram группу"""
    if not BOT_TOKEN:
        return False, "BOT_TOKEN is empty"
    if not GROUP_ID:
        return False, "GROUP_ID is empty"

    if len(text) > 3900:
        text = text[:3900] + "\n…(truncated)"

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": GROUP_ID, "text": text},
            timeout=12,
        )
        return r.ok, r.text
    except Exception as e:
        return False, f"requests error: {e}"