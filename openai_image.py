# openai_image.py - РАБОЧАЯ ВЕРСИЯ С gpt-image-1
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
    "832x1040": "1024x1792",
    "1024x576": "1792x1024",
}

def edit_image_gpt(
    prompt: str,
    image_bytes: bytes,
    size: str = "1024x1024",
    quality: str = "low"
) -> str:
    """Редактирование изображения через gpt-image-1"""
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    openai_size = SIZE_MAP.get(size, "1024x1024")
    
    try:
        print(f"🎨 gpt-image-1 edit: {openai_size}, quality={quality}")
        print(f"📦 Image size: {len(image_bytes)} bytes")
        
        # ✅ Правильный формат для gpt-image-1
        files = {
            "image": ("image.png", image_bytes, "image/png"),
            "prompt": (None, prompt),
        }
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }
        
        # Добавляем параметры если нужно
        data = {
            "model": "gpt-image-1",
            "size": openai_size,
            "n": "1"
        }
        
        if quality:
            data["quality"] = quality
        
        response = requests.post(
            "https://api.openai.com/v1/images/edits",
            headers=headers,
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code != 200:
            error_detail = response.json()
            print(f"❌ Ошибка API: {error_detail}")
            raise RuntimeError(f"OpenAI error: {error_detail}")
        
        result = response.json()
        if not result or not result.get("data") or not result["data"][0].get("url"):
            raise RuntimeError("Пустой ответ от OpenAI")
        
        image_url = result["data"][0]["url"]
        print(f"✅ URL получен")
        
        # Скачиваем изображение
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        # Конвертируем в base64
        image_base64 = base64.b64encode(img_response.content).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"❌ Ошибка gpt-image-1: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                print(f"📋 Детали: {e.response.json()}")
            except:
                print(f"📋 Текст: {e.response.text}")
        raise RuntimeError(f"Failed to edit image: {str(e)}")

def generate_image_dalle(
    prompt: str, 
    size: str = "1024x1024", 
    quality: str = "medium"
) -> str:
    """Генерация изображения через DALL-E 3"""
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    openai_size = SIZE_MAP.get(size, "1024x1024")
    
    quality_map = {
        "low": "low",
        "medium": "medium", 
        "standard": "standard"
    }
    dalle_quality = quality_map.get(quality, "medium")
    
    try:
        print(f"🎨 DALL-E 3: {openai_size}, quality={dalle_quality}")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=openai_size,
            quality=dalle_quality,
            n=1
        )
        
        if not response or not response.data or not response.data[0]:
            raise RuntimeError("Empty response from OpenAI")
        
        image_url = response.data[0].url
        print(f"✅ URL получен")
        
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        image_base64 = base64.b64encode(img_response.content).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"❌ DALL-E error: {e}")
        raise RuntimeError(f"Failed to generate image: {str(e)}")

def remove_bg_gpt(
    image_bytes: bytes,
    prompt: Optional[str] = None,
    size: str = "1024x1024"
) -> str:
    """Удаление фона через gpt-image-1"""
    bg_prompt = prompt or "subject on transparent background, white background, isolated object, no background"
    return edit_image_gpt(bg_prompt, image_bytes, size, "low")

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)

print("✅ openai_image.py с gpt-image-1 загружен!")