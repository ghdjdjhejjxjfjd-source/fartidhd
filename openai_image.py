# openai_image.py - ДИАГНОСТИЧЕСКАЯ ВЕРСИЯ
import os
import base64
import requests
from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
print(f"🔑 OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

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
    print(f"🎨 edit_image_dalle вызвана!")
    print(f"📝 Prompt: {prompt[:50]}...")
    print(f"📦 Image size: {len(image_bytes)} bytes")
    
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    
    openai_size = SIZE_MAP.get(size, "1024x1024")
    
    try:
        print(f"🔄 Пробуем gpt-image-1...")
        image_file = ("image.png", image_bytes, "image/png")
        
        response = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size=openai_size,
            n=1
        )
        
        if response and response.data and response.data[0]:
            image_url = response.data[0].url
            print(f"✅ URL получен")
            
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            
            image_base64 = base64.b64encode(img_response.content).decode('utf-8')
            return f"data:image/png;base64,{image_base64}"
        else:
            raise RuntimeError("Пустой ответ")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                print(f"📋 Детали: {e.response.json()}")
            except:
                print(f"📋 Текст: {e.response.text}")
        raise

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)

print("✅ openai_image.py загружен!")