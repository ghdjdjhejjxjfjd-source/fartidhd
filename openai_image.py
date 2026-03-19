# openai_image.py
import os
import base64
import requests
from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Соответствие наших размеров размерам OpenAI
SIZE_MAP = {
    "1024x1024": "1024x1024",
    "832x1040": "1024x1792",  # 4:5 конвертируем в вертикальный
    "1024x576": "1792x1024",   # 16:9 конвертируем в горизонтальный
}

def generate_image_dalle(prompt: str, size: str = "1024x1024") -> str:
    """
    Генерация изображения через DALL-E 3
    size: 1024x1024, 832x1040, 1024x576
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    # Конвертируем наш размер в формат OpenAI
    openai_size = SIZE_MAP.get(size, "1024x1024")
    
    try:
        print(f"🎨 Генерация через DALL-E 3 с размером {openai_size}")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=openai_size,
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        print(f"✅ Изображение получено, URL: {image_url[:50]}...")
        
        # Скачиваем изображение
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        # Конвертируем в base64
        image_base64 = base64.b64encode(img_response.content).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"❌ OpenAI DALL-E error: {e}")
        raise RuntimeError(f"Failed to generate image: {str(e)}")

def is_openai_available() -> bool:
    """Проверка доступности OpenAI"""
    return bool(OPENAI_API_KEY)