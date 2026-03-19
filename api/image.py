# api/image.py - версия с gpt-image-1
from flask import request, jsonify
from datetime import datetime
import time
import re

from .config import api, send_log_to_group
from .db import get_access
from payments import spend_stars

# Импортируем OpenAI
try:
    from openai_image import (
        generate_image_dalle,
        edit_image_gpt,
        remove_bg_gpt,
        is_openai_available
    )
    OPENAI_AVAILABLE = is_openai_available()
    print(f"✅ OpenAI загружен, доступен: {OPENAI_AVAILABLE}")
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"❌ OpenAI error: {e}")

# Stability больше не нужен, но оставим как fallback
try:
    from stability_client import generate_image, generate_image_from_image, remove_background
    STABILITY_AVAILABLE = True
except:
    STABILITY_AVAILABLE = False

IMAGE_RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 300
RATE_LIMIT_MAX = 5

# ... остальные функции validate_prompt, validate_user_id ...

@api.post("/api/image")
def api_image():
    # Приоритет - OpenAI
    if not OPENAI_AVAILABLE:
        if STABILITY_AVAILABLE:
            print("⚠️ OpenAI не доступен, используем Stability")
        else:
            return jsonify({"error": "image_generation_not_available"}), 503
    
    tg_user_id = request.form.get("tg_user_id") or 0
    prompt = (request.form.get("prompt") or "").strip()
    mode = (request.form.get("mode") or "txt2img").strip().lower()
    
    # ... валидация ...
    
    try:
        image_base64 = None
        model_used = "unknown"
        
        if mode == "txt2img":
            # Генерация по тексту - DALL-E 3
            size = f"{width}x{height}"
            enhanced_prompt = f"{prompt}, high quality, detailed, 8k, masterpiece"
            image_base64 = generate_image_dalle(enhanced_prompt, size, quality="medium")
            model_used = "openai-dalle"
            
        elif mode in ["img2img", "remove_bg", "inpaint"]:
            # Редактирование - gpt-image-1
            print(f"🎨 Using gpt-image-1 for {mode}")
            
            if mode == "remove_bg":
                image_base64 = remove_bg_gpt(
                    image_bytes=image_data,
                    prompt=prompt,
                    size=f"{width}x{height}"
                )
            else:
                image_base64 = edit_image_gpt(
                    prompt=prompt,
                    image_bytes=image_data,
                    size=f"{width}x{height}",
                    quality="low"
                )
            model_used = "openai-gpt-image-1"
            
        else:
            return jsonify({"error": "unsupported_mode"}), 400
        
        # ... остальной код ...
        
    except Exception as e:
        # Если OpenAI упал, пробуем Stability
        if STABILITY_AVAILABLE:
            print(f"⚠️ OpenAI error, fallback to Stability: {e}")
            # ... код для Stability ...
        else:
            raise