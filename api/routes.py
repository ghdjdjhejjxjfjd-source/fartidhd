# api/routes.py - ИСПРАВЛЕННАЯ ВЕРСИЯ (с очисткой памяти при смене характера/стиля)
from flask import request, jsonify
from datetime import datetime
import re
from functools import wraps
from time import time
import os

from .config import api, BOT_TOKEN, GROUP_ID, send_log_to_group
from .db import (
    get_access, get_use_mini_app, set_use_mini_app, 
    get_user_persona, set_user_persona, get_user_lang, set_user_lang,
    get_user_style, set_user_style,
    get_ai_mode, set_ai_mode,
    increment_messages, increment_images, add_stars_spent,
    get_user_limits, increment_groq_persona, increment_groq_style, increment_openai_style,
    mem_clear_last
)
from .memory import mem_get, mem_add, mem_clear, build_memory_prompt
from groq_client import ask_groq
from openai_client import ask_openai
from payments import get_balance, spend_stars

# ✅ Добавляем Pixian.ai для удаления фона
try:
    from pixian_client import remove_background_pixian
    PIXIAN_AVAILABLE = bool(os.getenv("PIXIAN_API_KEY"))
    if PIXIAN_AVAILABLE:
        print("✅ Pixian.ai загружен (удаление фона)")
    else:
        print("⚠️ Pixian.ai: ключ не найден")
except ImportError:
    PIXIAN_AVAILABLE = False
    print("⚠️ Pixian.ai не загружен (файл pixian_client.py не найден)")
except Exception as e:
    PIXIAN_AVAILABLE = False
    print(f"⚠️ Ошибка загрузки Pixian.ai: {e}")

import requests
import traceback

# Rate limiting
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 30

def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json(silent=True) or {}
        tg_user_id = data.get("tg_user_id") or 0
        
        if tg_user_id:
            now = time()
            if tg_user_id in RATE_LIMIT:
                count, first = RATE_LIMIT[tg_user_id]
                if now - first < RATE_LIMIT_WINDOW:
                    if count >= RATE_LIMIT_MAX:
                        return jsonify({"error": "rate_limit_exceeded"}), 429
                    RATE_LIMIT[tg_user_id] = (count + 1, first)
                else:
                    RATE_LIMIT[tg_user_id] = (1, now)
            else:
                RATE_LIMIT[tg_user_id] = (1, now)
        
        return f(*args, **kwargs)
    return decorated

def validate_user_id(user_id):
    try:
        uid = int(user_id)
        return 1 <= uid <= 9007199254740991
    except:
        return False

# =========================
# BASIC ROUTES
# =========================
@api.get("/")
def root():
    return "ok"

@api.get("/health")
def health():
    return "ok"

@api.get("/api/test-log")
def test_log():
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ok, info = send_log_to_group(f"✅ TEST LOG\n🕒 {time_str}")
    return jsonify(
        {
            "ok": ok,
            "group_id": GROUP_ID,
            "has_bot_token": bool(BOT_TOKEN),
            "telegram_response": info,
        }
    ), (200 if ok else 500)

@api.get("/api/access/<int:user_id>")
def api_access(user_id: int):
    return jsonify(get_access(user_id))

# =========================
# STATS ENDPOINTS
# =========================
@api.get("/api/user/stats/<int:user_id>")
def api_user_stats(user_id: int):
    a = get_access(user_id)
    balance = get_balance(user_id)
    
    return jsonify({
        "user_id": user_id,
        "registered_at": a.get("registered_at"),
        "total_messages": a.get("total_messages", 0),
        "total_images": a.get("total_images", 0),
        "total_stars_spent": a.get("total_stars_spent", 0),
        "stars_balance": balance,
        "is_free": a.get("is_free", False),
        "is_blocked": a.get("is_blocked", False),
        "persona": a.get("persona", "friendly"),
        "style": a.get("style", "steps"),
        "lang": a.get("lang", "ru"),
        "use_mini_app": a.get("use_mini_app", True),
        "ai_mode": a.get("ai_mode", "fast")
    })

@api.post("/api/user/stats/increment_message")
def api_increment_message():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    
    if not user_id or not validate_user_id(user_id):
        return jsonify({"error": "user_id required"}), 400
    
    increment_messages(int(user_id))
    return jsonify({"success": True})

@api.post("/api/user/stats/increment_image")
def api_increment_image():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    
    if not user_id or not validate_user_id(user_id):
        return jsonify({"error": "user_id required"}), 400
    
    increment_images(int(user_id))
    return jsonify({"success": True})

@api.post("/api/user/stats/add_spent")
def api_add_spent():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    amount = data.get("amount", 0)
    
    if not user_id or not validate_user_id(user_id) or not amount:
        return jsonify({"error": "user_id and amount required"}), 400
    
    add_stars_spent(int(user_id), amount)
    return jsonify({"success": True})

# =========================
# CHAT ENDPOINT - С ПОЛНЫМИ ЛОГАМИ
# =========================
def extract_last_user_message(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if "Conversation:" in s or "\nUser:" in s or s.startswith("You are "):
        idx = s.rfind("User:")
        if idx != -1:
            s2 = s[idx + len("User:") :].strip()
            cut = s2.find("\nAssistant:")
            if cut != -1:
                s2 = s2[:cut].strip()
            return s2
    return s

@api.post("/api/chat")
@rate_limit
def api_chat():
    data = request.get_json(silent=True) or {}
    
    # Валидация
    tg_user_id = data.get("tg_user_id") or 0
    if not validate_user_id(tg_user_id):
        return jsonify({"error": "invalid_user_id"}), 400
    
    raw_text = (data.get("text") or "").strip()
    if not raw_text:
        return jsonify({"error": "empty"}), 400
    
    text = extract_last_user_message(raw_text)
    tg_user_id_int = int(tg_user_id)
    
    # Получаем данные пользователя для логов
    tg_username = data.get("tg_username") or "—"
    tg_first_name = data.get("tg_first_name") or "—"
    
    # Проверка доступа
    a = get_access(tg_user_id_int)
    if a["is_blocked"]:
        return jsonify({"error": "blocked"}), 403
    
    # Проверка баланса
    balance = get_balance(tg_user_id_int)
    ai_mode = get_ai_mode(tg_user_id_int) or "fast"
    COST_PER_MESSAGE = 0.3 if ai_mode == "fast" else 1.0
    
    if not a["is_free"] and balance < COST_PER_MESSAGE:
        return jsonify({"error": "insufficient_stars"}), 402
    
    # Настройки
    lang = data.get("lang") or get_user_lang(tg_user_id_int) or "ru"
    style = data.get("style") or get_user_style(tg_user_id_int) or "steps"
    persona = data.get("persona") or get_user_persona(tg_user_id_int) or "friendly"
    
    # Названия для режима ИИ
    ai_mode_names = {
        "fast": "🚀 Быстрый",
        "quality": "💎 Качественный"
    }
    
    # Названия для характера
    persona_names = {
        "friendly": "😊 Общительный",
        "fun": "😂 Весёлый",
        "smart": "🧐 Умный",
        "strict": "😐 Строгий"
    }
    
    # Названия для стиля
    style_names = {
        "short": "📏 Коротко",
        "steps": "📋 По шагам",
        "detail": "📚 Подробно"
    }
    
    # Сохраняем сообщение
    mem_add(tg_user_id_int, "user", text)
    
    # История
    history = mem_get(tg_user_id_int, limit=100)
    prompt_with_memory = build_memory_prompt(history, text)
    
    try:
        if ai_mode == "fast":
            reply = ask_groq(prompt_with_memory, lang=lang, style=style, persona=persona)
        else:
            reply = ask_openai(prompt_with_memory, lang=lang, persona=persona, style=style)
        
        # ✅ ТОЛЬКО ЗДЕСЬ списываем звезды
        if not a["is_free"]:
            spend_stars(tg_user_id_int, COST_PER_MESSAGE)
            add_stars_spent(tg_user_id_int, COST_PER_MESSAGE)
        
        increment_messages(tg_user_id_int)
        mem_add(tg_user_id_int, "assistant", reply)
        
        # Получаем новый баланс после списания
        new_balance = get_balance(tg_user_id_int)
        
        # 🟢 ПОЛНЫЙ ЛОГ НА РУССКОМ С ОТСТУПАМИ
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_text = (
            f"🕒 {time_str}\n"
            f"👤 {tg_first_name} (@{tg_username})\n"
            f"🆔 {tg_user_id_int}\n"
            f"💰 Баланс: {new_balance} ⭐\n"
            f"\n"
            f"💬 Запрос:\n"
            f"{text}\n"
            f"\n\n\n\n\n"
            f"🤖 Ответ:\n"
            f"{reply}\n"
            f"\n\n\n\n\n"
            f"⚡ Режим: {ai_mode_names.get(ai_mode, ai_mode)}, стоимость: {COST_PER_MESSAGE} ⭐\n"
            f"🎭 Характер: {persona_names.get(persona, persona)}\n"
            f"📝 Стиль: {style_names.get(style, style)}"
        )
        
        send_log_to_group(log_text)
        
        return jsonify({
            "reply": reply,
            "balance": new_balance,
            "cost": COST_PER_MESSAGE
        })
        
    except Exception as e:
        # При ошибке удаляем сообщение из памяти
        mem_clear_last(tg_user_id_int)
        
        error_msg = str(e)
        print(f"❌ Ошибка у {tg_user_id_int}: {error_msg}")
        
        # Лог ошибки
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        send_log_to_group(
            f"❌ ОШИБКА\n"
            f"🕒 {time_str}\n"
            f"👤 {tg_first_name} (@{tg_username})\n"
            f"🆔 {tg_user_id_int}\n"
            f"💬 Запрос: {text[:100]}\n"
            f"💥 Ошибка: {error_msg[:200]}"
        )
        
        if "Failed to fetch" in error_msg or "timeout" in error_msg.lower():
            return jsonify({
                "error": "network_error",
                "message": "📡 Проблема с интернетом. Проверьте подключение."
            }), 503
        
        return jsonify({"error": "ai_unavailable"}), 503

# =========================
# MEMORY ENDPOINT
# =========================
@api.post("/api/memory/clear")
def api_memory_clear():
    data = request.get_json(silent=True) or {}
    tg_user_id = data.get("tg_user_id") or 0
    
    if not validate_user_id(tg_user_id):
        return jsonify({"error": "bad_user_id"}), 400

    mem_clear(int(tg_user_id))
    return jsonify({"ok": True, "message": "Memory cleared"})

# =========================
# SEND PHOTO TO TELEGRAM - ИСПРАВЛЕННАЯ ВЕРСИЯ
# =========================
@api.post("/api/send-photo")
def api_send_photo():
    try:
        user_id = request.form.get('user_id')
        image_file = request.files.get('image')
        filename = request.form.get('filename', 'image.png')
        
        print(f"📸 Send photo request: user_id={user_id}, filename={filename}, file exists={image_file is not None}")
        
        if not user_id or not validate_user_id(user_id) or not image_file:
            print(f"❌ Missing data: user_id={user_id}, file={image_file is not None}")
            return jsonify({"error": "Missing data"}), 400
            
        image_data = image_file.read()
        print(f"✅ Image read: {len(image_data)} bytes")
        
        bot_token = BOT_TOKEN
        if not bot_token:
            print("❌ BOT_TOKEN not configured")
            return jsonify({"error": "BOT_TOKEN not configured"}), 500
        
        # Определяем MIME тип
        if filename.endswith('.png'):
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'
            if not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
                filename = 'image.jpg'
        
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        
        files = {
            'photo': (filename, image_data, mime_type)
        }
        data = {
            'chat_id': user_id,
            'caption': f'✨ Сгенерированное изображение\nОтправлено из Mini App'
        }
        
        print(f"📤 Sending to Telegram: chat_id={user_id}, mime={mime_type}")
        
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"📥 Telegram response: status={response.status_code}")
        
        if response.status_code == 200:
            print("✅ Photo sent successfully")
            return jsonify({"success": True})
        else:
            error_data = response.json()
            print(f"❌ Telegram API error: {error_data}")
            return jsonify({
                "error": "Telegram API error", 
                "details": error_data
            }), 500
            
    except Exception as e:
        print(f"❌ Error in api_send_photo: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =========================
# USER SETTINGS ENDPOINTS
# =========================

@api.get("/api/user/mode/<int:user_id>")
def api_user_mode(user_id: int):
    return jsonify({
        "user_id": user_id,
        "use_mini_app": get_use_mini_app(user_id)
    })

@api.post("/api/user/mode")
def api_set_user_mode():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    use_mini_app = data.get("use_mini_app")
    
    if not user_id or not validate_user_id(user_id) or use_mini_app is None:
        return jsonify({"error": "user_id and use_mini_app required"}), 400
    
    set_use_mini_app(int(user_id), use_mini_app)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "use_mini_app": use_mini_app
    })

@api.get("/api/user/persona/<int:user_id>")
def api_user_persona(user_id: int):
    return jsonify({
        "user_id": user_id,
        "persona": get_user_persona(user_id)
    })

@api.post("/api/user/persona")
def api_set_user_persona():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    persona = data.get("persona")
    
    if not user_id or not validate_user_id(user_id) or not persona:
        return jsonify({"error": "user_id and persona required"}), 400
    
    valid_personas = ["friendly", "fun", "smart", "strict"]
    if persona not in valid_personas:
        return jsonify({"error": f"persona must be one of {valid_personas}"}), 400
    
    ai_mode = get_ai_mode(int(user_id))
    if ai_mode == "fast":
        if not increment_groq_persona(int(user_id)):
            return jsonify({"error": "limit_exceeded", "message": "Лимит изменений характера на сегодня исчерпан (5/5)"}), 429
    
    set_user_persona(int(user_id), persona)
    
    # ✅ ОЧИЩАЕМ ИСТОРИЮ ЧАТА ПРИ СМЕНЕ ХАРАКТЕРА
    from .memory import mem_clear
    mem_clear(int(user_id))
    print(f"🧹 Очищена память для пользователя {user_id} при смене характера")
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "persona": persona
    })

@api.get("/api/user/style/<int:user_id>")
def api_user_style(user_id: int):
    return jsonify({
        "user_id": user_id,
        "style": get_user_style(user_id)
    })

@api.post("/api/user/style")
def api_set_user_style():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    style = data.get("style")
    
    if not user_id or not validate_user_id(user_id) or not style:
        return jsonify({"error": "user_id and style required"}), 400
    
    valid_styles = ["short", "steps", "detail"]
    if style not in valid_styles:
        return jsonify({"error": f"style must be one of {valid_styles}"}), 400
    
    set_user_style(int(user_id), style)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "style": style
    })

@api.get("/api/user/lang/<int:user_id>")
def api_user_lang(user_id: int):
    return jsonify({
        "user_id": user_id,
        "lang": get_user_lang(user_id)
    })

@api.post("/api/user/lang")
def api_set_user_lang():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    lang = data.get("lang")
    
    if not user_id or not validate_user_id(user_id) or not lang:
        return jsonify({"error": "user_id and lang required"}), 400
    
    valid_langs = ["ru", "en", "kk", "tr", "uk", "fr"]
    if lang not in valid_langs:
        return jsonify({"error": f"lang must be one of {valid_langs}"}), 400
    
    set_user_lang(int(user_id), lang)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "lang": lang
    })

# =========================
# ЭНДПОИНТЫ ДЛЯ ЛИМИТОВ
# =========================

@api.get("/api/user/limits/<int:user_id>")
def api_user_limits(user_id: int):
    limits = get_user_limits(user_id)
    ai_mode = get_ai_mode(user_id)
    
    return jsonify({
        "user_id": user_id,
        "ai_mode": ai_mode,
        "limits": limits
    })

@api.post("/api/user/style/change")
def api_style_change():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    style = data.get("style")
    
    if not user_id or not validate_user_id(user_id) or not style:
        return jsonify({"error": "user_id and style required"}), 400
    
    valid_styles = ["short", "steps", "detail"]
    if style not in valid_styles:
        return jsonify({"error": f"style must be one of {valid_styles}"}), 400
    
    ai_mode = get_ai_mode(int(user_id))
    
    if ai_mode == "fast":
        if not increment_groq_style(int(user_id)):
            limits = get_user_limits(int(user_id))
            return jsonify({
                "error": "limit_exceeded",
                "message": f"Лимит изменений стиля на сегодня исчерпан ({limits['groq_style']}/5)"
            }), 429
    else:
        if not increment_openai_style(int(user_id)):
            limits = get_user_limits(int(user_id))
            return jsonify({
                "error": "limit_exceeded",
                "message": f"Лимит изменений стиля на сегодня исчерпан ({limits['openai_style']}/7)"
            }), 429
    
    set_user_style(int(user_id), style)
    
    # ✅ ОЧИЩАЕМ ИСТОРИЮ ЧАТА ПРИ СМЕНЕ СТИЛЯ
    from .memory import mem_clear
    mem_clear(int(user_id))
    print(f"🧹 Очищена память для пользователя {user_id} при смене стиля")
    
    return jsonify({
        "success": True,
        "style": style,
        "remaining": get_user_limits(int(user_id))
    })

# =========================
# ЭНДПОИНТЫ ДЛЯ РЕЖИМА ИИ - ИСПРАВЛЕНО!
# =========================

@api.get("/api/user/ai_mode/<int:user_id>")
def api_user_ai_mode(user_id: int):
    return jsonify({
        "user_id": user_id,
        "ai_mode": get_ai_mode(user_id)
    })

@api.post("/api/user/ai_mode")
def api_set_user_ai_mode():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    ai_mode = data.get("ai_mode")
    
    if not user_id or not validate_user_id(user_id) or not ai_mode:
        return jsonify({"error": "user_id and ai_mode required"}), 400
    
    valid_modes = ["fast", "quality"]
    if ai_mode not in valid_modes:
        return jsonify({"error": f"ai_mode must be one of {valid_modes}"}), 400
    
    try:
        # Запоминаем старый режим на случай ошибки
        old_mode = get_ai_mode(int(user_id))
        
        # Пытаемся установить новый режим
        set_ai_mode(int(user_id), ai_mode)
        
        # Возвращаем успех с новым режимом
        return jsonify({
            "success": True,
            "user_id": user_id,
            "ai_mode": ai_mode,
            "old_mode": old_mode
        })
        
    except Exception as e:
        print(f"❌ Error setting AI mode for {user_id}: {e}")
        # При ошибке возвращаем старый режим
        return jsonify({
            "error": "failed_to_set_mode",
            "message": "Не удалось сменить режим. Попробуйте позже.",
            "current_mode": get_ai_mode(int(user_id))
        }), 500

# =========================
# ЭНДПОИНТ ДЛЯ УДАЛЕНИЯ ФОНА ЧЕРЕЗ PIXIAN.AI
# =========================
@api.post("/api/remove-bg")
def api_remove_bg():
    """
    Удаление фона через Pixian.ai
    """
    try:
        # Получаем данные
        user_id = request.form.get('user_id')
        image_file = request.files.get('image')
        
        if not user_id or not validate_user_id(user_id):
            return jsonify({"error": "invalid_user_id"}), 400
        
        if not image_file:
            return jsonify({"error": "image_required"}), 400
        
        # Проверяем доступность Pixian
        if not PIXIAN_AVAILABLE:
            return jsonify({"error": "pixian_not_available"}), 503
        
        # Читаем изображение
        image_data = image_file.read()
        
        if len(image_data) > 5 * 1024 * 1024:
            return jsonify({"error": "file_too_large", "message": "Максимум 5MB"}), 400
        
        # Удаляем фон
        result_base64 = remove_background_pixian(image_data)
        
        # Логируем
        send_log_to_group(
            f"🧹 Удаление фона через Pixian\n"
            f"👤 Пользователь: {user_id}\n"
            f"📦 Размер: {len(image_data)} байт"
        )
        
        return jsonify({
            "success": True,
            "image_base64": result_base64
        })
        
    except Exception as e:
        print(f"❌ Ошибка в api_remove_bg: {e}")
        return jsonify({"error": str(e)}), 500