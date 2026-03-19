# openai_image.py — РАБОЧИЙ (img2img через dall-e-2)

import os
import base64
import requests
from openai import OpenAI
from typing import Optional

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
print(f"🔑 OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SIZE_MAP = {
    "1024x1024": "1024x1024",
    "832x1040": "1024x1024",
    "1024x576": "1024x1024",
}


def edit_image_gpt(
    prompt: str,
    image_bytes: bytes,
    size: str = "1024x1024",
    quality: str = "low"
) -> str:
    """Фото → стиль (img2img через DALL·E 2)"""

    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    openai_size = SIZE_MAP.get(size, "1024x1024")

    try:
        print(f"🎨 DALL-E 2 edit: {openai_size}")
        print(f"📦 Image size: {len(image_bytes)} bytes")

        # ⚠️ ВАЖНО: используем dall-e-2
        response = client.images.edit(
            model="dall-e-2",
            image=image_bytes,
            prompt=prompt,
            size=openai_size
        )

        if not response or not response.data or len(response.data) == 0:
            raise RuntimeError("Empty response from OpenAI")

        image_url = response.data[0].url

        if not image_url:
            raise RuntimeError("No URL returned")

        print("✅ URL получен")

        # скачиваем изображение
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        image_base64 = base64.b64encode(img_response.content).decode("utf-8")

        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print(f"❌ Ошибка OpenAI edit: {e}")
        raise RuntimeError(f"Failed to edit image: {str(e)}")


def generate_image_dalle(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard"
) -> str:
    """Обычная генерация через DALL·E 3"""

    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    try:
        print(f"🎨 DALL-E 3: {size}")

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
        print(f"❌ DALL-E error: {e}")
        raise RuntimeError(f"Failed to generate image: {str(e)}")


def remove_bg_gpt(
    image_bytes: bytes,
    prompt: Optional[str] = None,
    size: str = "1024x1024"
) -> str:
    """Удаление фона"""
    bg_prompt = prompt or "remove background, transparent background"
    return edit_image_gpt(bg_prompt, image_bytes, size)


def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)


print("✅ openai_image.py загружен!")