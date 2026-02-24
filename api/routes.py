from flask import request, jsonify
from datetime import datetime

from .config import api, BOT_TOKEN, GROUP_ID, send_log_to_group
from .db import (
    get_access, get_use_mini_app, set_use_mini_app, 
    get_user_persona, set_user_persona, get_user_lang, set_user_lang,
    get_user_style, set_user_style,  # ✅ НОВЫЕ ФУНКЦИИ
    get_ai_mode, set_ai_mode,
    increment_messages, increment_images, add_stars_spent,
    get_user_limits, increment_groq_persona, increment_groq_style, increment_openai_style
)
from .memory import mem_get, mem_add, mem_clear, build_memory_prompt
from groq_client import ask_groq
from openai_client import ask_openai
from payments import get_balance, spend_stars

import requests

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
    """Получить полную статистику пользователя"""
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
        "style": a.get("style", "steps"),  # ✅ ДОБАВЛЕНО
        "lang": a.get("lang", "ru"),
        "use_mini_app": a.get("use_mini_app", True),
        "ai_mode": a.get("ai_mode", "fast")
    })


@api.post("/api/user/stats/increment_message")
def api_increment_message():
    """Увеличить счетчик сообщений (для Mini App)"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    increment_messages(user_id)
    return jsonify({"success": True})


@api.post("/api/user/stats/increment_image")
def api_increment_image():
    """Увеличить счетчик картинок (для Mini App)"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    increment_images(user_id)
    return jsonify({"success": True})


@api.post("/api/user/stats/add_spent")
def api_add_spent():
    """Добавить потраченные звезды (для Mini App)"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    amount = data.get("amount", 0)
    
    if not user_id or not amount:
        return jsonify({"error": "user_id and amount required"}), 400
    
    add_stars_spent(user_id, amount)
    return jsonify({"success": True})


# =========================
# CHAT ENDPOINT
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
def api_chat():
    data = request.get_json(silent=True) or {}

    raw_text = (data.get("text") or "").strip()
    if not raw_text:
        return jsonify({"error": "empty"}), 400

    text = extract_last_user_message(raw_text)

    tg_user_id = data.get("tg_user_id") or data.get("telegram_user_id") or 0
    try:
        tg_user_id_int = int(tg_user_id)
    except Exception:
        tg_user_id_int = 0

    tg_username = data.get("tg_username") or data.get("username") or "—"
    tg_first_name = data.get("tg_first_name") or data.get("first_name") or "—"

    # --- ACCESS CHECK ---
    if tg_user_id_int:
        a = get_access(tg_user_id_int)
        if a["is_blocked"]:
            return jsonify({"error": "blocked"}), 403
        
        # Проверяем баланс звезд
        balance = get_balance(tg_user_id_int)
        
        # Определяем стоимость в зависимости от режима ИИ
        ai_mode = get_ai_mode(tg_user_id_int) or "fast"
        COST_PER_MESSAGE = 0.3 if ai_mode == "fast" else 1.0
        
        # Для FREE пользователей всё бесплатно
        if not a["is_free"]:
            if balance < COST_PER_MESSAGE:
                return jsonify({"error": "insufficient_stars"}), 402
            
            # Списываем звезды
            spend_stars(tg_user_id_int, COST_PER_MESSAGE)
            add_stars_spent(tg_user_id_int, COST_PER_MESSAGE)
        
        # Увеличиваем счетчик сообщений
        increment_messages(tg_user_id_int)
            
    else:
        return jsonify({"error": "payment_required"}), 402

    lang = data.get("lang") or get_user_lang(tg_user_id_int) or "ru"
    style = data.get("style") or get_user_style(tg_user_id_int) or "steps"  # ✅ БЕРЁМ ИЗ БД
    
    # Используем сохраненный характер пользователя
    persona = data.get("persona")
    if tg_user_id_int and not persona:
        persona = get_user_persona(tg_user_id_int)
    else:
        persona = persona or "friendly"

    # берём историю + строим промпт с памятью
    history = mem_get(tg_user_id_int, limit=24)
    prompt_with_memory = build_memory_prompt(history, text)

    # сохраняем user сообщение в память ДО ответа
    mem_add(tg_user_id_int, "user", text)

    try:
        # ✅ ВЫБОР МОДЕЛИ БЕЗ FALLBACK
        ai_mode = get_ai_mode(tg_user_id_int) or "fast"
        
        if ai_mode == "fast":
            # Быстрый режим - ТОЛЬКО Groq (со стилем)
            print(f"🚀 Использую Groq для пользователя {tg_user_id_int} (стиль: {style})")
            reply = ask_groq(prompt_with_memory, lang=lang, style=style, persona=persona)
            
            # Логируем успех
            send_log_to_group(f"✅ Groq ответил пользователю {tg_user_id_int}")
            
        else:
            # Качественный режим - ТОЛЬКО OpenAI (ТОЖЕ со стилем!)
            print(f"💎 Использую OpenAI для пользователя {tg_user_id_int} (стиль: {style})")
            # Передаём стиль в OpenAI
            reply = ask_openai(prompt_with_memory, lang=lang, persona=persona, style=style)
            
            # Логируем успех
            send_log_to_group(f"✅ OpenAI ответил пользователю {tg_user_id_int}")
            
    except Exception as e:
        # ❌ НИКАКОГО FALLBACK! Просто возвращаем ошибку
        error_msg = f"❌ Ошибка в {ai_mode} режиме: {str(e)}"
        print(error_msg)
        send_log_to_group(f"❌ Сбой у пользователя {tg_user_id_int} в режиме {ai_mode}: {e}")
        
        # Возвращаем понятную ошибку пользователю
        if ai_mode == "fast":
            return jsonify({
                "error": "🚫 Быстрый режим временно недоступен. Пожалуйста, переключитесь на Качественный режим в настройках или попробуйте позже."
            }), 503
        else:
            return jsonify({
                "error": "🚫 Качественный режим временно недоступен. Пожалуйста, попробуйте позже."
            }), 503

    # сохраняем ответ в память
    mem_add(tg_user_id_int, "assistant", reply)

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    send_log_to_group(
        f"🕒 {time_str}\n"
        f"👤 {tg_first_name} (@{tg_username})\n"
        f"🆔 {tg_user_id_int}\n"
        f"💬 {text}\n\n"
        f"🤖 {reply}\n"
        f"⚡ Режим: {'Быстрый (Groq)' if ai_mode == 'fast' else 'Качественный (OpenAI)'}"
    )

    return jsonify({"reply": reply})


# =========================
# MEMORY ENDPOINT
# =========================
@api.post("/api/memory/clear")
def api_memory_clear():
    data = request.get_json(silent=True) or {}
    tg_user_id = data.get("tg_user_id") or 0
    try:
        tg_user_id_int = int(tg_user_id)
    except Exception:
        tg_user_id_int = 0

    if not tg_user_id_int:
        return jsonify({"error": "bad_user_id"}), 400

    mem_clear(tg_user_id_int)
    return jsonify({"ok": True, "message": "Memory cleared"})


# =========================
# SEND PHOTO TO TELEGRAM
# =========================
@api.post("/api/send-photo")
def api_send_photo():
    try:
        user_id = request.form.get('user_id')
        image_file = request.files.get('image')
        filename = request.form.get('filename', 'image.jpg')
        
        if not user_id or not image_file:
            return jsonify({"error": "Missing data"}), 400
            
        image_data = image_file.read()
        
        bot_token = BOT_TOKEN
        if not bot_token:
            return jsonify({"error": "BOT_TOKEN not configured"}), 500
            
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        
        files = {
            'photo': (filename, image_data, 'image/jpeg')
        }
        data = {
            'chat_id': user_id,
            'caption': f'✨ Улучшенное изображение\nОтправлено из Mini App'
        }
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            error_data = response.json()
            return jsonify({
                "error": "Telegram API error", 
                "details": error_data
            }), 500
            
    except Exception as e:
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
    
    if not user_id or use_mini_app is None:
        return jsonify({"error": "user_id and use_mini_app required"}), 400
    
    set_use_mini_app(user_id, use_mini_app)
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
    
    if not user_id or not persona:
        return jsonify({"error": "user_id and persona required"}), 400
    
    valid_personas = ["friendly", "fun", "smart", "strict"]
    if persona not in valid_personas:
        return jsonify({"error": f"persona must be one of {valid_personas}"}), 400
    
    # ✅ Проверяем лимит для Groq
    ai_mode = get_ai_mode(user_id)
    if ai_mode == "fast":
        if not increment_groq_persona(user_id):
            return jsonify({"error": "limit_exceeded", "message": "Лимит изменений характера на сегодня исчерпан (5/5)"}), 429
    
    set_user_persona(user_id, persona)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "persona": persona
    })


@api.get("/api/user/style/<int:user_id>")
def api_user_style(user_id: int):
    """Получить стиль пользователя"""
    return jsonify({
        "user_id": user_id,
        "style": get_user_style(user_id)
    })


@api.post("/api/user/style")
def api_set_user_style():
    """Установить стиль пользователя"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    style = data.get("style")
    
    if not user_id or not style:
        return jsonify({"error": "user_id and style required"}), 400
    
    valid_styles = ["short", "steps", "detail"]
    if style not in valid_styles:
        return jsonify({"error": f"style must be one of {valid_styles}"}), 400
    
    set_user_style(user_id, style)
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
    
    if not user_id or not lang:
        return jsonify({"error": "user_id and lang required"}), 400
    
    valid_langs = ["ru", "en", "kk", "tr", "uk", "fr"]
    if lang not in valid_langs:
        return jsonify({"error": f"lang must be one of {valid_langs}"}), 400
    
    set_user_lang(user_id, lang)
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
    """Получить текущие лимиты пользователя"""
    limits = get_user_limits(user_id)
    ai_mode = get_ai_mode(user_id)
    
    return jsonify({
        "user_id": user_id,
        "ai_mode": ai_mode,
        "limits": limits
    })


@api.post("/api/user/style/change")
def api_style_change():
    """Изменить стиль ответа с проверкой лимита"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    style = data.get("style")
    
    if not user_id or not style:
        return jsonify({"error": "user_id and style required"}), 400
    
    valid_styles = ["short", "steps", "detail"]
    if style not in valid_styles:
        return jsonify({"error": f"style must be one of {valid_styles}"}), 400
    
    # Проверяем лимит в зависимости от режима
    ai_mode = get_ai_mode(user_id)
    
    if ai_mode == "fast":
        if not increment_groq_style(user_id):
            limits = get_user_limits(user_id)
            return jsonify({
                "error": "limit_exceeded",
                "message": f"Лимит изменений стиля на сегодня исчерпан ({limits['groq_style']}/5)"
            }), 429
    else:
        if not increment_openai_style(user_id):
            limits = get_user_limits(user_id)
            return jsonify({
                "error": "limit_exceeded",
                "message": f"Лимит изменений стиля на сегодня исчерпан ({limits['openai_style']}/7)"
            }), 429
    
    # ✅ СОХРАНЯЕМ СТИЛЬ В БД
    set_user_style(user_id, style)
    
    return jsonify({
        "success": True,
        "style": style,
        "remaining": get_user_limits(user_id)
    })


# =========================
# ЭНДПОИНТЫ ДЛЯ РЕЖИМА ИИ
# =========================

@api.get("/api/user/ai_mode/<int:user_id>")
def api_user_ai_mode(user_id: int):
    """Получить режим ИИ пользователя"""
    return jsonify({
        "user_id": user_id,
        "ai_mode": get_ai_mode(user_id)
    })


@api.post("/api/user/ai_mode")
def api_set_user_ai_mode():
    """Установить режим ИИ"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    ai_mode = data.get("ai_mode")
    
    if not user_id or not ai_mode:
        return jsonify({"error": "user_id and ai_mode required"}), 400
    
    valid_modes = ["fast", "quality"]
    if ai_mode not in valid_modes:
        return jsonify({"error": f"ai_mode must be one of {valid_modes}"}), 400
    
    set_ai_mode(user_id, ai_mode)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "ai_mode": ai_mode
    })