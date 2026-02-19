# stability_client.py
import os
import base64
from typing import Optional
import requests

# --- ENV ---
STABILITY_API_KEY = (os.getenv("STABILITY_API_KEY") or "").strip()

# --- Stability Client ---
print(f"🔧 STABILITY_API_KEY loaded: {'Yes' if STABILITY_API_KEY else 'No'}")

def translate_text(text: str) -> str:
    """
    Перевод текста на английский через Google Translate
    """
    if not text or not text.strip():
        return text
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "en",
            "dt": "t",
            "q": text
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            translated = ""
            for item in data[0]:
                if item[0]:
                    translated += item[0]
            return translated.strip()
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
    
    return text

def generate_image(
    prompt: str,
    negative_prompt: Optional[str] = None,
    steps: int = 30,
    cfg_scale: float = 7.0,
    width: int = 1024,
    height: int = 1024,
    samples: int = 1,
) -> str:
    """
    Генерация изображения через Stability AI SD3.5 Large
    """
    if not STABILITY_API_KEY:
        raise RuntimeError("STABILITY_API_KEY is not set")
    
    if not prompt:
        raise ValueError("Prompt is empty")
    
    # Переводим на английский
    translated = translate_text(prompt)
    print(f"📝 Original: {prompt}")
    print(f"📝 Translated: {translated}")
    
    # SD3.5 Large
    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"  # Ждем изображение напрямую
    }
    
    # Стандартный negative prompt
    default_negative = "blurry, low quality, distorted, ugly, bad anatomy, watermark, text, logo, signature, worst quality, low resolution, grainy, deformed, disfigured, bad proportions, extra limbs, extra fingers, mutated, disgusting"
    
    # Формируем данные (только то что принимает API)
    data = {
        "prompt": translated,
        "model": "sd3.5-large",  # Правильное имя модели
        "aspect_ratio": "1:1",
        "output_format": "png",
        "negative_prompt": negative_prompt or default_negative,
    }
    
    try:
        print(f"🔄 Sending to Stability AI (sd3.5-large)...")
        
        # Важно: используем data=, не files= и не json=
        response = requests.post(
            url, 
            headers=headers,
            data=data,  # Простой form data
            timeout=60
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code != 200:
            # Пробуем получить детали ошибки
            error_detail = "Unknown error"
            try:
                error_json = response.json()
                error_detail = error_json.get('message', str(error_json))
            except:
                error_detail = response.text[:200]
            
            raise RuntimeError(f"Stability API error {response.status_code}: {error_detail}")
        
        # Ответ должен быть изображением
        image_data = response.content
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        print(f"✅ Image generated successfully ({len(image_data)} bytes)")
        return f"data:image/png;base64,{image_base64}"
        
    except requests.exceptions.Timeout:
        raise RuntimeError("Request timeout - try again")
    except Exception as e:
        print(f"❌ Generation error: {str(e)}")
        raise RuntimeError(f"Image generation failed: {str(e)}")


def generate_image_fallback(
    prompt: str,
    negative_prompt: Optional[str] = None,
) -> str:
    """
    Запасной вариант со старой моделью если SD3.5 не работает
    """
    print("⚠️ Using fallback model (SDXL)")
    
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1.0
            },
            {
                "text": negative_prompt or "blurry, low quality, distorted, ugly",
                "weight": -1.0
            }
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise RuntimeError(f"Fallback API error {response.status_code}")
    
    data = response.json()
    image_base64 = data["artifacts"][0]["base64"]
    return f"data:image/png;base64,{image_base64}"


def generate_image_from_image(
    prompt: str,
    init_image: bytes,
    strength: float = 0.7,
    steps: int = 30,
    cfg_scale: float = 7.0,
) -> str:
    """
    Генерация на основе изображения (используем старую модель)
    """
    if not STABILITY_API_KEY:
        raise RuntimeError("STABILITY_API_KEY is not set")
    
    if not prompt:
        raise ValueError("Prompt is empty")
    
    if not init_image:
        raise ValueError("Init image is required")
    
    # Переводим на английский
    translated = translate_text(prompt)
    
    # Используем старый API для img2img
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json"
    }
    
    files = {
        "init_image": ("image.png", init_image, "image/png")
    }
    
    data = {
        "text_prompts[0][text]": translated,
        "text_prompts[0][weight]": "1.0",
        "cfg_scale": str(cfg_scale),
        "steps": str(steps),
        "style_preset": "photographic"
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=90)
        
        if response.status_code != 200:
            error_detail = "Unknown error"
            try:
                error_json = response.json()
                error_detail = error_json.get('message', str(error_json))
            except:
                error_detail = response.text[:200]
            raise RuntimeError(f"Stability API error {response.status_code}: {error_detail}")
        
        data = response.json()
        image_base64 = data["artifacts"][0]["base64"]
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        raise RuntimeError(f"Image-to-image generation failed: {str(e)}")


def is_stability_available() -> bool:
    """Проверяет, доступен ли Stability AI."""
    return bool(STABILITY_API_KEY)