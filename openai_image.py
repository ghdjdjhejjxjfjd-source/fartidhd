# openai_image.py — ФИНАЛ (PNG FIX)

import os
import base64
import requests
from openai import OpenAI
from typing import Optional
from PIL import Image
import io

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
print(f"🔑 OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def convert_to_png(image_bytes: bytes) -> bytes:
    """Конвертируем любое изображение в PNG"""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    
    output = io.BytesIO()
    image.save(output, format="PNG")
    
    return output.getvalue()


def edit_image_gpt(
    prompt: str,
    image_bytes: bytes,
    size: str = "1024x1024",
    quality: str = "low"
) -> str:

    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    try:
        print("🔄 Конвертация в PNG...")
        image_bytes = convert_to_png(image_bytes)

        print(f"📦 PNG size: {len(image_bytes)} bytes")

        # ⚠️ проверка размера
        if len(image_bytes) > 4 * 1024 * 1024:
            raise RuntimeError("Image too large (>4MB)")

        print("🎨 DALL-E 2 edit...")

        response = client.images.edit(
            model="dall-e-2",
            image=("image.png", image_bytes, "image/png"),
            prompt=prompt,
            size="1024x1024"
        )

        if not response.data:
            raise RuntimeError("Empty response")

        image_url = response.data[0].url

        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        image_base64 = base64.b64encode(img_response.content).decode("utf-8")

        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print("❌ ERROR:", e)
        raise RuntimeError(str(e))


def generate_image_dalle(prompt: str) -> str:
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024"
    )

    image_url = response.data[0].url

    img_response = requests.get(image_url)
    image_base64 = base64.b64encode(img_response.content).decode("utf-8")

    return f"data:image/png;base64,{image_base64}"


def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)


print("✅ openai_image.py FINAL FIX LOADED")