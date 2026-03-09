# api/image.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С REMOVE_BG
from flask import request, jsonify
from datetime import datetime
import time
import re

from .config import api, STABILITY_AVAILABLE, send_log_to_group
from .db import get_access
from payments import spend_stars

IMAGE_RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 300
RATE_LIMIT_MAX = 5

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
    if not STABILITY_AVAILABLE:
        return jsonify({"error": "image_generation_not_available"}), 503
    
    tg_user_id = request.form.get("tg_user_id") or 0
    prompt = (request.form.get("prompt") or "").strip()
    mode = (request.form.get("mode") or "txt2img").strip().lower()
    
    if not validate_user_id(tg_user_id):
        return jsonify({"error": "invalid_user_id"}), 400
    
    tg_user_id_int = int(tg_user_id)
    
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
    
    a = get_access(tg_user_id_int)
    if a["is_blocked"]:
        return jsonify({"error": "blocked"}), 403
    
    is_valid, error_code = validate_prompt(prompt)
    if not is_valid:
        if error_code == "empty_prompt":
            return jsonify({"error": "empty_prompt"}), 400
        elif error_code == "prompt_too_long":
            return jsonify({"error": "prompt_too_long", "message": "Промпт слишком длинный (макс 1000 символов)"}), 400
        elif error_code == "blocked_content":
            return jsonify({"error": "blocked_content", "message": "Запрос содержит запрещенные слова"}), 400
    
    cost = 2
    if mode in ["remove_bg", "upscale"]:
        cost = 2
    elif mode == "inpaint":
        cost = 3
    
    if not a["is_free"]:
        from payments import get_balance
        balance = get_balance(tg_user_id_int)
        if balance < cost:
            return jsonify({"error": "insufficient_stars"}), 402
    
    image_file = request.files.get("image")
    image_data = None
    if image_file:
        image_file.seek(0, 2)
        size = image_file.tell()
        image_file.seek(0)
        
        if size > 5 * 1024 * 1024:
            return jsonify({"error": "file_too_large", "message": "Файл слишком большой (макс 5MB)"}), 400
        image_data = image_file.read()
    
    if mode in ["img2img", "remove_bg", "inpaint", "upscale"] and not image_data:
        return jsonify({"error": "image_required_for_this_mode"}), 400
    
    try:
        steps = int(request.form.get("steps") or 30)
        steps = min(max(steps, 10), 50)
    except:
        steps = 30
    
    try:
        cfg_scale = float(request.form.get("cfg_scale") or 7.0)
        cfg_scale = min(max(cfg_scale, 1.0), 20.0)
    except:
        cfg_scale = 7.0
    
    try:
        width = int(request.form.get("width") or 1024)
        height = int(request.form.get("height") or 1024)
        width = min(max(width, 256), 2048)
        height = min(max(height, 256), 2048)
    except:
        width, height = 1024, 1024
    
    try:
        strength = float(request.form.get("strength") or 0.7)
        strength = min(max(strength, 0.1), 0.9)
    except:
        strength = 0.7
    
    negative_prompt = request.form.get("negative_prompt") or None
    
    try:
        # ✅ ИМПОРТИРУЕМ ВСЕ ФУНКЦИИ
        from stability_client import generate_image, generate_image_from_image, remove_background
        
        # ===== ОБРАБОТКА РАЗНЫХ РЕЖИМОВ =====
        if mode == "txt2img":
            # Генерация по тексту
            image_base64 = generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                steps=steps,
                cfg_scale=cfg_scale,
                width=width,
                height=height,
            )
            
        elif mode == "remove_bg":
            # ⭐ УДАЛЕНИЕ ФОНА
            print(f"🖼 Processing remove_bg for user {tg_user_id_int}")
            image_base64 = remove_background(
                init_image=image_data,
                prompt=prompt or "subject on transparent background, white background",
                strength=0.6,  # Низкий strength чтобы сохранить объект
                steps=steps,
            )
            
        elif mode in ["img2img", "inpaint", "upscale"]:
            # Обычный image-to-image
            image_base64 = generate_image_from_image(
                prompt=prompt,
                init_image=image_data,
                strength=strength if mode == "img2img" else 0.6,
                steps=steps,
                cfg_scale=cfg_scale,
            )
        else:
            return jsonify({"error": "unsupported_mode"}), 400
        
        if not image_base64:
            return jsonify({"error": "generation_failed"}), 500
        
        # Списываем звезды если не FREE
        if not a["is_free"]:
            spend_stars(tg_user_id_int, cost)
        
        tg_username = request.form.get("tg_username") or "—"
        tg_first_name = request.form.get("tg_first_name") or "—"
        
        send_log_to_group(
            f"🖼 Изображение сгенерировано\n"
            f"👤 {tg_first_name} (@{tg_username})\n"
            f"🆔 {tg_user_id_int}\n"
            f"📝 Режим: {mode}, стоимость: {cost}⭐\n"
            f"💬 Промпт: {prompt[:80]}..."
        )
        
        return jsonify({
            "success": True,
            "image_base64": image_base64,
            "prompt": prompt,
            "mode": mode,
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error in api_image: {error_msg}")
        send_log_to_group(f"❌ Ошибка генерации: {tg_user_id_int} - {error_msg[:100]}")
        
        if "API key" in error_msg:
            return jsonify({"error": "service_error", "message": "Ошибка сервиса генерации"}), 500
        elif "credit" in error_msg.lower() or "balance" in error_msg.lower():
            return jsonify({"error": "insufficient_balance", "message": "Закончились кредиты на сервере"}), 402
        elif "timeout" in error_msg.lower():
            return jsonify({"error": "timeout", "message": "Сервер долго не отвечает. Попробуйте позже."}), 504
        else:
            return jsonify({"error": "generation_failed", "message": "Не удалось сгенерировать. Попробуйте другой промпт."}), 500