# openai_image.py — ГОТОВЫЙ ИСПРАВЛЕННЫЙ

import os
import base64
from openai import OpenAI
from typing import Optional

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
print(f"🔑 OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SIZE_MAP = {
    "1024x1024": "1024x1024",
    "832x1040": "1024x1792",
    "1024x576": "1792x1024",
}


def edit_image_gpt(
    prompt: str,
    image_bytes: bytes,
    size: str = "1024x1024",
    quality: str = "low"
) -> str:
    """Редактирование изображения (фото → стиль) через OpenAI"""

    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    openai_size = SIZE_MAP.get(size, "1024x1024")

    try:
        print(f"🎨 OpenAI edit: {openai_size}")
        print(f"📦 Image size: {len(image_bytes)} bytes")

        # ✅ ГЛАВНОЕ ИСПРАВЛЕНИЕ: добавлен model
        response = client.images.edit(
            model="gpt-image-1",
            image=image_bytes,
            prompt=prompt,
            size=openai_size
        )

        if not response or not response.data or len(response.data) == 0:
            print("❌ Пустой ответ от OpenAI")
            raise RuntimeError("Empty response from OpenAI")

        # ✅ Используем base64 (НЕ url)
        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise RuntimeError("No base64 in response")

        print("✅ Картинка получена (base64)")

        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print(f"❌ Ошибка OpenAI edit: {e}")
        raise RuntimeError(f"Failed to edit image: {str(e)}")


def generate_image_dalle(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard"
) -> str:
    """Генерация изображения через DALL-E 3"""

    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    openai_size = SIZE_MAP.get(size, "1024x1024")

    try:
        print(f"🎨 DALL-E 3: {openai_size}, quality={quality}")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=openai_size,
            quality=quality
        )

        if not response or not response.data or len(response.data) == 0:
            raise RuntimeError("Empty response from OpenAI")

        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise RuntimeError("No base64 in response")

        print("✅ DALL-E картинка получена")

        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print(f"❌ DALL-E error: {e}")
        raise RuntimeError(f"Failed to generate image: {str(e)}")


def remove_bg_gpt(
    image_bytes: bytes,
    prompt: Optional[str] = None,
    size: str = "1024x1024"
) -> str:
    """Удаление фона"""
    bg_prompt = prompt or "Remove background, keep subject, transparent background"
    return edit_image_gpt(bg_prompt, image_bytes, size, "low")


def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)


print("✅ openai_image.py загружен!")