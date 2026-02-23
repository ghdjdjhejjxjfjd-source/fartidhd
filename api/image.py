from flask import request, jsonify
from datetime import datetime

from .config import api, STABILITY_AVAILABLE, send_log_to_group
from .db import get_access
from payments import spend_stars

# =========================
# IMAGE GENERATION ENDPOINT
# =========================
@api.post("/api/image")
def api_image():
    """Генерация изображения через Stability AI"""
    
    # Проверка доступности Stability AI
    if not STABILITY_AVAILABLE:
        return jsonify({"error": "image_generation_not_available"}), 503
    
    # Получаем данные из формы (поддерживает файлы)
    tg_user_id = request.form.get("tg_user_id") or 0
    prompt = (request.form.get("prompt") or "").strip()
    mode = (request.form.get("mode") or "txt2img").strip().lower()
    
    try:
        tg_user_id_int = int(tg_user_id)
    except Exception:
        tg_user_id_int = 0
    
    # --- ACCESS CHECK ---
    if tg_user_id_int:
        a = get_access(tg_user_id_int)
        if a["is_blocked"]:
            return jsonify({"error": "blocked"}), 403
        if not a["is_free"]:
            # Списываем звезды за генерацию
            from payments import spend_stars
            # Разные цены для разных режимов
            cost = 2  # по умолчанию
            if mode in ["remove_bg", "img2img", "upscale"]:
                cost = 2
            elif mode == "inpaint":
                cost = 3
                
            if not spend_stars(tg_user_id_int, cost):
                return jsonify({"error": "insufficient_stars"}), 402
    else:
        return jsonify({"error": "payment_required"}), 402
    
    # Проверка промпта
    if not prompt and mode == "txt2img":
        return jsonify({"error": "empty_prompt"}), 400
    
    # Получаем файл если есть
    image_file = request.files.get("image")
    image_data = None
    if image_file:
        image_data = image_file.read()
    
    # Проверка режима
    if mode in ["img2img", "remove_bg", "inpaint", "upscale"] and not image_data:
        return jsonify({"error": "image_required_for_this_mode"}), 400
    
    # Получаем дополнительные параметры
    negative_prompt = request.form.get("negative_prompt") or None
    try:
        steps = int(request.form.get("steps") or 30)
        cfg_scale = float(request.form.get("cfg_scale") or 7.0)
        width = int(request.form.get("width") or 1024)
        height = int(request.form.get("height") or 1024)
        strength = float(request.form.get("strength") or 0.7)
    except ValueError:
        steps, cfg_scale, width, height, strength = 30, 7.0, 1024, 1024, 0.7
    
    # Ограничения для безопасности
    steps = min(max(steps, 10), 50)
    cfg_scale = min(max(cfg_scale, 1.0), 20.0)
    width = min(max(width, 256), 2048)
    height = min(max(height, 256), 2048)
    strength = min(max(strength, 0.1), 0.9)
    
    try:
        from stability_client import generate_image, generate_image_from_image
        
        # Генерация в зависимости от режима
        if mode == "txt2img":
            # Текст -> изображение
            image_base64 = generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                steps=steps,
                cfg_scale=cfg_scale,
                width=width,
                height=height,
            )
        
        elif mode == "img2img" and image_data:
            # Изображение -> изображение (смена стиля)
            image_base64 = generate_image_from_image(
                prompt=prompt,
                init_image=image_data,
                strength=strength,
                steps=steps,
                cfg_scale=cfg_scale,
            )
        
        elif mode == "remove_bg" and image_data:
            # Удаление фона
            enhanced_prompt = f"{prompt}, professional product photo, clean white background, no background, isolated object"
            image_base64 = generate_image_from_image(
                prompt=enhanced_prompt,
                init_image=image_data,
                strength=0.6,
                steps=35,
                cfg_scale=8.0,
            )
        
        elif mode == "inpaint" and image_data:
            # Удаление объекта
            enhanced_prompt = f"{prompt}, remove specified object, clean removal, seamless edit"
            image_base64 = generate_image_from_image(
                prompt=enhanced_prompt,
                init_image=image_data,
                strength=0.8,
                steps=40,
                cfg_scale=7.5,
            )
        
        elif mode == "upscale" and image_data:
            # Улучшение качества
            enhanced_prompt = f"{prompt}, high resolution, 8k, detailed, sharp focus, professional photography"
            image_base64 = generate_image_from_image(
                prompt=enhanced_prompt,
                init_image=image_data,
                strength=0.5,
                steps=25,
                cfg_scale=6.0,
            )
        
        else:
            return jsonify({"error": "unsupported_mode"}), 400
        
        if not image_base64:
            return jsonify({"error": "generation_failed"}), 500
        
        # Логируем успешную генерацию
        tg_username = request.form.get("tg_username") or "—"
        tg_first_name = request.form.get("tg_first_name") or "—"
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        send_log_to_group(
            f"🖼 Изображение сгенерировано\n"
            f"🕒 {time_str}\n"
            f"👤 {tg_first_name} (@{tg_username})\n"
            f"🆔 {tg_user_id_int}\n"
            f"📝 Режим: {mode}\n"
            f"💬 Промпт: {prompt[:80]}..."
        )
        
        return jsonify({
            "success": True,
            "image_base64": image_base64,
            "prompt": prompt,
            "mode": mode,
            "width": width,
            "height": height,
            "steps": steps,
        })
        
    except Exception as e:
        # Логируем ошибку
        error_msg = str(e)
        send_log_to_group(f"❌ Ошибка генерации изображения\n🆔 {tg_user_id_int}\n📝 {prompt[:50]}...\n💥 {error_msg}")
        
        # Безопасный ответ с ошибкой
        if "API key" in error_msg:
            return jsonify({"error": "invalid_api_key"}), 500
        elif "credit" in error_msg.lower() or "balance" in error_msg.lower():
            return jsonify({"error": "insufficient_balance"}), 402
        elif "timeout" in error_msg.lower():
            return jsonify({"error": "generation_timeout"}), 504
        else:
            return jsonify({"error": "generation_failed", "detail": error_msg[:100]}), 500