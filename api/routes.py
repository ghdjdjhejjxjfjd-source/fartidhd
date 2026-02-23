from flask import request, jsonify
from datetime import datetime

from .config import api, BOT_TOKEN, GROUP_ID, send_log_to_group
from .db import get_access, get_use_mini_app, set_use_mini_app, get_user_persona, set_user_persona, get_user_lang, set_user_lang
from .memory import mem_get, mem_add, mem_clear, build_memory_prompt
from groq_client import ask_groq
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
        
        # ✅ Проверяем баланс звезд
        balance = get_balance(tg_user_id_int)
        
        # Стоимость одного запроса - 1 звезда
        COST_PER_MESSAGE = 1
        
        if balance < COST_PER_MESSAGE and not a["is_free"]:
            return jsonify({"error": "insufficient_stars"}), 402
            
        # Если пользователь не FREE - списываем звезды
        if not a["is_free"]:
            spend_stars(tg_user_id_int, COST_PER_MESSAGE)
            
    else:
        return jsonify({"error": "payment_required"}), 402

    lang = data.get("lang") or get_user_lang(tg_user_id_int) or "ru"
    style = data.get("style") or "steps"
    
    # ✅ Используем сохраненный характер пользователя
    persona = data.get("persona")
    if tg_user_id_int and not persona:
        persona = get_user_persona(tg_user_id_int)
    else:
        persona = persona or "friendly"

    # ✅ берём историю + строим промпт с памятью
    history = mem_get(tg_user_id_int, limit=24)
    prompt_with_memory = build_memory_prompt(history, text)

    # ✅ сохраняем user сообщение в память ДО ответа
    mem_add(tg_user_id_int, "user", text)

    try:
        reply = ask_groq(prompt_with_memory, lang=lang, style=style, persona=persona)
    except Exception as e:
        send_log_to_group(f"❌ Ошибка /api/chat: {e}")
        return jsonify({"error": str(e)}), 500

    # ✅ сохраняем ответ в память
    mem_add(tg_user_id_int, "assistant", reply)

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    send_log_to_group(
        f"🕒 {time_str}\n"
        f"👤 {tg_first_name} (@{tg_username})\n"
        f"🆔 {tg_user_id_int}\n"
        f"💬 {text}\n\n"
        f"🤖 {reply}"
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
    
    set_user_persona(user_id, persona)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "persona": persona
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