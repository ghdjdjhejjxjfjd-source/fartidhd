# openai_image.py - ИСПРАВЛЕНО
import os
import base64
import requests
from openai import OpenAI
from typing import Optional

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Соответствие наших размеров размерам OpenAI
SIZE_MAP = {
    "1024x1024": "1024x1024",
    "832x1040": "1024x1792",  # 4:5 конвертируем в вертикальный
    "1024x576": "1792x1024",   # 16:9 конвертируем в горизонтальный
}

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
        
        image_url = response.data[0].url
        print(f"✅ Изображение получено, URL: {image_url[:50]}...")
        
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        image_base64 = base64.b64encode(img_response.content).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"❌ OpenAI DALL-E error: {e}")
        raise RuntimeError(f"Failed to generate image: {str(e)}")

def edit_image_dalle(
    prompt: str,
    image_bytes: bytes,
    size: str = "1024x1024",
    quality: str = "low"
) -> str:
    """
    Редактирование изображения через gpt-image-1
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    openai_size = SIZE_MAP.get(size, "1024x1024")
    
    try:
        print(f"🎨 gpt-image-1 edit: {openai_size}, quality={quality}")
        
        # ✅ ПРАВИЛЬНО: передаем как файл
        image_file = ("image.png", image_bytes, "image/png")
        
        response = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size=openai_size,
            quality=quality,
            n=1
        )
        
        image_url = response.data[0].url
        print(f"✅ Редактирование успешно, URL: {image_url[:50]}...")
        
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        image_base64 = base64.b64encode(img_response.content).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"❌ gpt-image-1 edit error: {e}")
        raise RuntimeError(f"Failed to edit image: {str(e)}")

def remove_bg_dalle(
    image_bytes: bytes,
    prompt: Optional[str] = None,
    size: str = "1024x1024"
) -> str:
    """Удаление фона через gpt-image-1"""
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    bg_prompt = prompt or "subject on transparent background, white background, isolated object, no background"
    
    return edit_image_dalle(
        prompt=bg_prompt,
        image_bytes=image_bytes,
        size=size,
        quality="low"
    )

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)

def is_gpt_image_1_available() -> bool:
    return bool(OPENAI_API_KEY)