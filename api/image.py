# api/image.py - ИСПРАВЛЕННАЯ ВЕРСИЯ (только 1:1, правильное списание)
from flask import request, jsonify
from datetime import datetime
import time
import re

from .config import api, send_log_to_group
from .db import get_access
from payments import spend_stars

# Импортируем OpenAI
try:
    from openai_image import generate_image_dalle, is_openai_available
    OPENAI_AVAILABLE = is_openai_available()
    print(f"✅ OpenAI загружен, доступен: {OPENAI_AVAILABLE}")
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"❌ Ошибка загрузки OpenAI: {e}")

IMAGE_RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 300
RATE_LIMIT_MAX = 5

COST = 10  # Стоимость генерации

def validate_prompt(prompt: str) -> tuple[bool, str]:
    if not prompt or not prompt.strip():
        return False, "empty_prompt"
    
    if len(prompt) > 1000:
        return False, "prompt_too_long"
    
    blocked_patterns = [
        r'nude', r'naked', r'sex', r'porn', r'violence', r'gore',
        r'blood', r'kill', r'death', r'corpse', r'horror'
    ]
    
    lower_prompt = prompt.lower()
    for pattern in blocked_patterns:
        if re.search(pattern, lower_prompt):
            return False, "blocked_content"
    
    return True, "ok"

def validate_user_id(user_id):
    try:
        uid = int(user_id)
        return 1 <= uid <= 9007199254740991
    except:
        return False


@api.post("/api/image")
def api_image():
    # Проверяем OpenAI
    if not OPENAI_AVAILABLE:
        return jsonify({"error": "openai_not_available", "message": "OpenAI не настроен"}), 503
    
    tg_user_id = request.form.get("tg_user_id") or 0
    prompt = (request.form.get("prompt") or "").strip()
    mode = (request.form.get("mode") or "txt2img").strip().lower()
    
    if not validate_user_id(tg_user_id):
        return jsonify({"error": "invalid_user_id"}), 400
    
    tg_user_id_int = int(tg_user_id)
    
    # Rate limiting
    now = time.time()
    if tg_user_id_int in IMAGE_RATE_LIMIT:
        count, first = IMAGE_RATE_LIMIT[tg_user_id_int]
        if now - first < RATE_LIMIT_WINDOW:
            if count >= RATE_LIMIT_MAX:
                wait_minutes = int((RATE_LIMIT_WINDOW - (now - first)) / 60) + 1
                return jsonify({
                    "error": "rate_limit_exceeded",
                    "message": f"Слишком много запросов. Подождите {wait_minutes} мин."
                }), 429
            IMAGE_RATE_LIMIT[tg_user_id_int] = (count + 1, first)
        else:
            IMAGE_RATE_LIMIT[tg_user_id_int] = (1, now)
    else:
        IMAGE_RATE_LIMIT[tg_user_id_int] = (1, now)
    
    # Проверка доступа
    a = get_access(tg_user_id_int)
    if a["is_blocked"]:
        return jsonify({"error": "blocked"}), 403
    
    # Проверка промпта
    is_valid, error_code = validate_prompt(prompt)
    if not is_valid:
        if error_code == "empty_prompt":
            return jsonify({"error": "empty_prompt"}), 400
        elif error_code == "prompt_too_long":
            return jsonify({"error": "prompt_too_long", "message": "Промпт слишком длинный (макс 1000 символов)"}), 400
        elif error_code == "blocked_content":
            return jsonify({"error": "blocked_content", "message": "Запрос содержит запрещенные слова"}), 400
    
    # Проверка баланса ТОЛЬКО для платных пользователей
    if not a["is_free"]:
        from payments import get_balance
        balance = get_balance(tg_user_id_int)
        if balance < COST:
            return jsonify({"error": "insufficient_stars", "message": f"Недостаточно звезд. Нужно {COST}⭐"}), 402
    
    # Только txt2img, только 1:1
    if mode != "txt2img":
        return jsonify({"error": "unsupported_mode", "message": "Поддерживается только генерация по тексту"}), 400
    
    # Фиксированный размер 1024x1024
    size = "1024x1024"
    
    try:
        print(f"🎨 Генерация картинки для {tg_user_id_int}: {prompt[:50]}...")
        
        # Усиленный промпт для лучшего качества
        enhanced_prompt = f"{prompt}, high quality, detailed, 8k, masterpiece"
        
        # Генерация через DALL-E 3
        image_base64 = generate_image_dalle(enhanced_prompt, size, quality="standard")
        
        if not image_base64:
            return jsonify({"error": "generation_failed"}), 500
        
        # ===== СПИСЫВАЕМ ЗВЕЗДЫ ТОЛЬКО ПОСЛЕ УСПЕШНОЙ ГЕНЕРАЦИИ =====
        if not a["is_free"]:
            spend_stars(tg_user_id_int, COST)
        
        # Логируем
        tg_username = request.form.get("tg_username") or "—"
        tg_first_name = request.form.get("tg_first_name") or "—"
        
        send_log_to_group(
            f"🖼 Изображение сгенерировано\n"
            f"👤 {tg_first_name} (@{tg_username})\n"
            f"🆔 {tg_user_id_int}\n"
            f"🤖 Модель: OpenAI DALL-E 3\n"
            f"📝 Режим: txt2img, стоимость: {COST}⭐\n"
            f"💬 Промпт: {prompt[:80]}..."
        )
        
        return jsonify({
            "success": True,
            "image_base64": image_base64,
            "prompt": prompt,
            "mode": mode,
            "model": "openai-dalle"
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка генерации для {tg_user_id_int}: {error_msg}")
        send_log_to_group(f"❌ Ошибка генерации: {tg_user_id_int} - {error_msg[:100]}")
        
        if "API key" in error_msg:
            return jsonify({"error": "service_error", "message": "Ошибка API ключа"}), 500
        elif "credit" in error_msg.lower() or "balance" in error_msg.lower():
            return jsonify({"error": "insufficient_balance", "message": "Закончились кредиты OpenAI"}), 402
        elif "safety" in error_msg.lower() or "blocked" in error_msg.lower():
            return jsonify({"error": "blocked_content", "message": "Запрос содержит запрещенный контент"}), 400
        elif "timeout" in error_msg.lower():
            return jsonify({"error": "timeout", "message": "Сервер долго не отвечает. Попробуйте позже."}), 504
        else:
            return jsonify({"error": "generation_failed", "message": f"Ошибка: {error_msg[:100]}"}), 500