# bot/chat.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from telegram import Update
from telegram.ext import ContextTypes
import requests

from api import get_access, get_user_persona, get_user_lang, increment_messages, add_stars_spent
from payments import get_balance
from .config import send_log_http

API_BASE = "https://fayrat-production.up.railway.app"  # Замени на свой URL

async def api_chat_request(uid: int, text: str, lang: str, persona: str) -> str:
    """Отправка запроса к API чата"""
    try:
        response = requests.post(
            f"{API_BASE}/api/chat",
            json={
                "tg_user_id": uid,
                "text": text,
                "lang": lang,
                "persona": persona,
                "style": "steps"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("reply", "")
        elif response.status_code == 402:
            return "❌ Недостаточно звезд. Купите в меню."
        else:
            return "❌ Ошибка сервера. Попробуйте позже."
    except requests.exceptions.Timeout:
        return "📡 Таймаут. Сервер долго отвечает."
    except Exception as e:
        print(f"API chat error: {e}")
        return "❌ Ошибка соединения."

async def inline_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < 1:
        await query.message.reply_text(
            "❌ Недостаточно звезд.\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await query.message.reply_text(
        "💬 Напиши сообщение для ИИ.\n"
        "Отправь текст, и я отвечу.\n\n"
        "Для отмены напиши /cancel"
    )
    
    context.user_data["in_chat_mode"] = True

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, text: str):
    a = get_access(uid)
    lang = get_user_lang(uid)
    persona = get_user_persona(uid)
    
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    balance = get_balance(uid)
    if not a.get("is_free") and balance < 1:
        await update.message.reply_text(
            "❌ Недостаточно звезд.\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    await update.message.reply_text("🤔 Думаю...")
    
    try:
        reply = await api_chat_request(uid, text, lang, persona)
        
        if reply:
            await update.message.reply_text(reply)
            increment_messages(uid)
            send_log_http(f"💬 Чат в боте: {uid} -> {text[:50]}...")
        else:
            await update.message.reply_text("❌ Ошибка получения ответа")
            
    except Exception as e:
        error_msg = str(e)
        if "insufficient_stars" in error_msg:
            await update.message.reply_text("❌ Недостаточно звезд. Купите в меню.")
        elif "network" in error_msg.lower():
            await update.message.reply_text("📡 Проблема с интернетом. Попробуйте позже.")
        else:
            await update.message.reply_text(f"❌ Ошибка: {error_msg[:100]}")