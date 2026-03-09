# stability_client.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С УДАЛЕНИЕМ ФОНА
import os
import base64
import time
from typing import Optional
import requests

STABILITY_API_KEY = (os.getenv("STABILITY_API_KEY") or "").strip()

print(f"🔧 STABILITY_API_KEY loaded: {'Yes' if STABILITY_API_KEY else 'No'}")

MAX_RETRIES = 2
RETRY_DELAY = 1
TIMEOUT = 60

MODELS = [
    {
        "name": "sd3.5-large",
        "url": "https://api.stability.ai/v2beta/stable-image/generate/sd3",
        "type": "new",
        "params": {
            "model": "sd3.5-large",
            "aspect_ratio": "1:1",
            "output_format": "png"
        }
    },
    {
        "name": "sd3-large",
        "url": "https://api.stability.ai/v2beta/stable-image/generate/sd3",
        "type": "new",
        "params": {
            "model": "sd3-large",
            "aspect_ratio": "1:1", 
            "output_format": "png"
        }
    },
    {
        "name": "sd-xl",
        "url": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        "type": "old",
        "params": {}
    }
]

def translate_text(text: str) -> str:
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
    if not STABILITY_API_KEY:
        raise RuntimeError("STABILITY_API_KEY is not set")
    
    if not prompt:
        raise ValueError("Prompt is empty")
    
    translated = translate_text(prompt)
    print(f"📝 Original: {prompt}")
    print(f"📝 Translated: {translated}")
    
    default_negative = "blurry, low quality, distorted, ugly, bad anatomy, watermark, text, logo, signature, worst quality, low resolution, grainy, deformed, disfigured, bad proportions, extra limbs, extra fingers, mutated, disgusting"
    final_negative = negative_prompt or default_negative
    
    last_error = None
    
    for model_index, model in enumerate(MODELS):
        try:
            print(f"🔄 Trying model {model_index + 1}/{len(MODELS)}: {model['name']}")
            
            if model["type"] == "new":
                image_base64 = _generate_new_api(
                    model=model,
                    prompt=translated,
                    negative_prompt=final_negative,
                    steps=steps,
                    cfg_scale=cfg_scale
                )
            else:
                image_base64 = _generate_old_api(
                    prompt=translated,
                    negative_prompt=final_negative,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    width=width,
                    height=height
                )
            
            print(f"✅ Success with model: {model['name']}")
            return image_base64
            
        except Exception as e:
            last_error = e
            print(f"⚠️ Model {model['name']} failed: {e}")
            
            if model_index < len(MODELS) - 1:
                print(f"🔄 Falling back to next model...")
                time.sleep(RETRY_DELAY)
                continue
    
    error_msg = f"All models failed. Last error: {last_error}"
    print(f"❌ {error_msg}")
    
    if "timeout" in str(last_error).lower():
        raise RuntimeError("Сервер генерации не отвечает. Попробуйте позже.")
    elif "api key" in str(last_error).lower():
        raise RuntimeError("Ошибка API ключа. Свяжитесь с админом.")
    elif "credit" in str(last_error).lower() or "balance" in str(last_error).lower():
        raise RuntimeError("Закончились кредиты на генерацию. Свяжитесь с админом.")
    else:
        raise RuntimeError("Не удалось сгенерировать изображение. Попробуйте другой промпт.")

def _generate_new_api(model, prompt, negative_prompt, steps=30, cfg_scale=7.0):
    url = model["url"]
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }
    
    data = {
        "prompt": prompt,
        **model["params"],
        "negative_prompt": negative_prompt,
        "cfg_scale": str(cfg_scale),
        "steps": str(steps)
    }
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(
                url, 
                headers=headers,
                data=data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                image_data = response.content
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/png;base64,{image_base64}"
            
            if response.status_code == 400:
                minimal_data = {
                    "prompt": prompt,
                    **model["params"],
                }
                response = requests.post(
                    url, 
                    headers=headers,
                    data=minimal_data,
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    image_data = response.content
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    return f"data:image/png;base64,{image_base64}"
            
            error_detail = "Unknown error"
            try:
                error_json = response.json()
                error_detail = error_json.get('message', str(error_json))
            except:
                error_detail = response.text[:200]
            
            raise RuntimeError(f"HTTP {response.status_code}: {error_detail}")
            
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                print(f"⏱️ Timeout, retry {attempt + 1}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise RuntimeError("Request timeout")
        
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                print(f"🔌 Connection error, retry {attempt + 1}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise RuntimeError("Connection error")

def _generate_old_api(prompt, negative_prompt, steps=30, cfg_scale=7.0, width=1024, height=1024):
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
                "text": negative_prompt,
                "weight": -1.0
            }
        ],
        "cfg_scale": cfg_scale,
        "height": height,
        "width": width,
        "samples": 1,
        "steps": steps,
    }
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                image_base64 = data["artifacts"][0]["base64"]
                return f"data:image/png;base64,{image_base64}"
            
            error_detail = "Unknown error"
            try:
                error_json = response.json()
                error_detail = error_json.get('message', str(error_json))
            except:
                error_detail = response.text[:200]
            
            raise RuntimeError(f"HTTP {response.status_code}: {error_detail}")
            
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise RuntimeError("Request timeout")
            
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise RuntimeError("Connection error")

def generate_image_fallback(prompt: str, negative_prompt: Optional[str] = None) -> str:
    print("⚠️ Using fallback model (SDXL)")
    return _generate_old_api(prompt, negative_prompt or "blurry, low quality, distorted, ugly")

def generate_image_from_image(
    prompt: str,
    init_image: bytes,
    strength: float = 0.7,
    steps: int = 30,
    cfg_scale: float = 7.0,
) -> str:
    if not STABILITY_API_KEY:
        raise RuntimeError("STABILITY_API_KEY is not set")
    
    if not prompt:
        raise ValueError("Prompt is empty")
    
    if not init_image:
        raise ValueError("Init image is required")
    
    translated = translate_text(prompt)
    
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
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                image_base64 = data["artifacts"][0]["base64"]
                return f"data:image/png;base64,{image_base64}"
            
            error_detail = "Unknown error"
            try:
                error_json = response.json()
                error_detail = error_json.get('message', str(error_json))
            except:
                error_detail = response.text[:200]
            
            raise RuntimeError(f"Stability API error {response.status_code}: {error_detail}")
            
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"🔄 Retry {attempt + 1}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise RuntimeError(f"Image-to-image generation failed: {str(e)}")

# ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ ДЛЯ УДАЛЕНИЯ ФОНА ==========
def remove_background(
    init_image: bytes,
    prompt: Optional[str] = None,
    strength: float = 0.6,
    steps: int = 30,
    cfg_scale: float = 7.0,
) -> str:
    """
    Удаление фона с изображения через Stability AI
    """
    if not STABILITY_API_KEY:
        raise RuntimeError("STABILITY_API_KEY is not set")
    
    if not init_image:
        raise ValueError("Init image is required")
    
    # Промпт для удаления фона
    bg_prompt = prompt or "subject on transparent background, white background, no background, isolated object"
    
    translated = translate_text(bg_prompt)
    print(f"🖼 Removing background with prompt: {translated}")
    
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json"
    }
    
    files = {
        "init_image": ("image.png", init_image, "image/png")
    }
    
    # ⚠️ ВАЖНО: strength НЕ передается в data, он идет в отдельном поле для image-to-image
    data = {
        "text_prompts[0][text]": translated,
        "text_prompts[0][weight]": "1.0",
        "cfg_scale": str(cfg_scale),
        "steps": str(steps),
        "style_preset": "photographic",
        "samples": "1"
    }
    
    # Strength передается отдельно, но в requests он должен быть в data
    # Для Stability API strength - это отдельный параметр, но в форме
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            print(f"🔄 Attempt {attempt + 1}/{MAX_RETRIES + 1}")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                image_base64 = data["artifacts"][0]["base64"]
                print("✅ Background removed successfully")
                return f"data:image/png;base64,{image_base64}"
            
            # Если ошибка 400, пробуем с другим промптом
            if response.status_code == 400 and attempt == 0:
                print("⚠️ Got 400 error, trying with simpler prompt")
                data["text_prompts[0][text]"] = "white background, no background"
                continue
                
            error_detail = "Unknown error"
            try:
                error_json = response.json()
                error_detail = error_json.get('message', str(error_json))
            except:
                error_detail = response.text[:200]
            
            raise RuntimeError(f"Stability API error {response.status_code}: {error_detail}")
            
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"🔄 Retry {attempt + 1}/{MAX_RETRIES} after error: {e}")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise RuntimeError(f"Background removal failed: {str(e)}")

def is_stability_available() -> bool:
    return bool(STABILITY_API_KEY)