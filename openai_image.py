# openai_image.py - ДИАГНОСТИЧЕСКАЯ ВЕРСИЯ
import os
import base64
import requests
from openai import OpenAI
from typing import Optional

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SIZE_MAP = {
    "1024x1024": "1024x1024",
    "832x1040": "1024x1792",
    "1024x576": "1792x1024",
}

def edit_image_dalle(
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
        
        # Подготовка файла
        image_file = ("image.png", image_bytes, "image/png")
        
        # Пробуем разные варианты
        print("🔄 Вариант 1: с model='gpt-image-1'")
        try:
            response = client.images.edit(
                model="gpt-image-1",
                image=image_file,
                prompt=prompt,
                size=openai_size,
                quality=quality,
                n=1
            )
            print("✅ Вариант 1 сработал!")
        except Exception as e1:
            print(f"❌ Вариант 1 ошибка: {e1}")
            
            print("🔄 Вариант 2: без указания модели")
            try:
                response = client.images.edit(
                    image=image_file,
                    prompt=prompt,
                    size=openai_size,
                    n=1
                )
                print("✅ Вариант 2 сработал!")
            except Exception as e2:
                print(f"❌ Вариант 2 ошибка: {e2}")
                
                # Если оба не сработали - показываем детали
                if hasattr(e2, 'response') and e2.response:
                    try:
                        error_detail = e2.response.json()
                        print(f"📋 Детали ошибки: {error_detail}")
                    except:
                        pass
                raise RuntimeError("gpt-image-1 не доступен")
        
        # Проверяем ответ
        if not response:
            print("❌ Пустой ответ от OpenAI")
            raise RuntimeError("Empty response")
        
        if not response.data:
            print("❌ Нет data в ответе")
            raise RuntimeError("No data")
        
        if not response.data[0]:
            print("❌ Первый элемент пустой")
            raise RuntimeError("First item is None")
        
        image_url = response.data[0].url
        if not image_url:
            print("❌ Нет URL в ответе")
            raise RuntimeError("No URL")
        
        print(f"✅ URL получен")
        
        # Скачиваем
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        image_base64 = base64.b64encode(img_response.content).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise RuntimeError(f"Failed to edit image: {str(e)}")

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)