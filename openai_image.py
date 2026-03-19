# openai_image.py — ПОЛНЫЙ РАБОЧИЙ

import os
import io
import base64
import requests
from typing import Optional
from PIL import Image
from openai import OpenAI

# --- КЛЮЧ ---
OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
print("RAW KEY:", OPENAI_API_KEY[:8] + "..." if OPENAI_API_KEY else None)
print(f"🔑 OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY НЕ НАЙДЕН В ENV")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- УТИЛИТЫ ---
def convert_to_png(image_bytes: bytes) -> bytes:
    """Конвертирует любое изображение в PNG (RGBA)"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def ensure_png_and_limit(image_bytes: bytes, max_bytes: int = 4 * 1024 * 1024) -> bytes:
    """Гарантирует PNG и размер < 4MB (при необходимости пережимает)"""
    png = convert_to_png(image_bytes)

    # если больше 4MB — уменьшаем размер (ресайз)
    if len(png) > max_bytes:
        img = Image.open(io.BytesIO(png))
        w, h = img.size

        # уменьшаем пропорционально пока не влезет
        while len(png) > max_bytes and max(w, h) > 512:
            w = int(w * 0.8)
            h = int(h * 0.8)
            img = img.resize((w, h))
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            png = buf.getvalue()

    if len(png) > max_bytes:
        raise RuntimeError("Image too large (>4MB) even after resize")

    return png

# --- ОСНОВНАЯ ФУНКЦИЯ: ФОТО → СТИЛЬ ---
def edit_image_gpt(
    prompt: str,
    image_bytes: bytes,
    size: str = "1024x1024",
    quality: str = "low"
) -> str:
    """
    img2img через DALL·E 2 (требует PNG < 4MB)
    """

    try:
        print("🔄 Конвертация в PNG + проверка размера...")
        png_bytes = ensure_png_and_limit(image_bytes)
        print(f"📦 PNG size: {len(png_bytes)} bytes")

        print("🎨 DALL-E 2 edit...")

        response = client.images.edit(
            model="dall-e-2",
            image=("image.png", png_bytes, "image/png"),
            prompt=prompt,
            size=size
        )

        if not response or not response.data or len(response.data) == 0:
            raise RuntimeError("Empty response from OpenAI")

        image_url = response.data[0].url
        if not image_url:
            raise RuntimeError("No URL returned")

        # скачиваем результат
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        image_base64 = base64.b64encode(img_response.content).decode("utf-8")
        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print("❌ ERROR edit_image_gpt:", e)
        raise RuntimeError(str(e))

# --- ГЕНЕРАЦИЯ С НУЛЯ ---
def generate_image_dalle(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard"
) -> str:
    """
    Генерация через DALL·E 3
    """
    try:
        print(f"🎨 DALL-E 3 generate: {size}, quality={quality}")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality
        )

        if not response or not response.data or len(response.data) == 0:
            raise RuntimeError("Empty response from OpenAI")

        image_url = response.data[0].url

        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        image_base64 = base64.b64encode(img_response.content).decode("utf-8")
        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print("❌ ERROR generate_image_dalle:", e)
        raise RuntimeError(str(e))

# --- УДАЛЕНИЕ ФОНА (через тот же edit) ---
def remove_bg_gpt(
    image_bytes: bytes,
    prompt: Optional[str] = None,
    size: str = "1024x1024"
) -> str:
    bg_prompt = prompt or "remove background, transparent background, keep subject"
    return edit_image_gpt(bg_prompt, image_bytes, size)

# --- ПРОВЕРКА ---
def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)

print("✅ openai_image.py READY")