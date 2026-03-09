import os
from typing import Optional
import base64

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-4-vision-preview").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ХАРАКТЕРЫ
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        
        СТИЛЬ:
        - Пиши тепло, приветливо
        - Смайлики: очень редко (1 на 3-4 сообщения)
        - Не используй одинаковые смайлики
        - Будь естественным
    """,
    
    "fun": """
        Ты весёлый собеседник.
        
        СТИЛЬ:
        - Шути, будь позитивным
        - Смайлики: разные, не повторяйся 😊 😄 😂 😅 😉 😎
        - Не используй один смайлик в каждом ответе
    """,
    
    "smart": """
        Ты умный собеседник.
        
        СТИЛЬ:
        - Глубокие, фактологические ответы
        - Смайлики: только умные, редко 🧐 🤔 📚
        - Не используй смайлики в каждом ответе
    """,
    
    "strict": """
        Ты строгий собеседник.
        
        СТИЛЬ:
        - Коротко, по делу
        - Без смайликов
        - Минимум слов
    """,
}

# Стили ответов
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences).",
    "steps": "Answer step by step, structured.",
    "detail": "Answer in detail but without unnecessary words."
}

def detect_language(text: str) -> str:
    """Определяем язык текста"""
    # Простая эвристика по символам
    cyrillic = sum(1 for c in text if 'а' <= c.lower() <= 'я')
    latin = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    
    if cyrillic > latin * 2:
        return "Russian"
    elif text and (text[0] in 'қәғңүұһі' or 'қ' in text or 'ә' in text):
        return "Kazakh"
    elif text and ('ğ' in text or 'ü' in text or 'ş' in text or 'ı' in text):
        return "Turkish"
    elif text and ('є' in text or 'ї' in text or 'і' in text):
        return "Ukrainian"
    elif text and ('é' in text or 'è' in text or 'ç' in text):
        return "French"
    else:
        return "English"

def extract_user_message(full_text: str) -> str:
    """Извлекаем последнее сообщение пользователя из истории"""
    if "User:" in full_text:
        parts = full_text.split("User:")
        last_part = parts[-1].strip()
        if "Assistant:" in last_part:
            return last_part.split("Assistant:")[0].strip()
        return last_part
    return full_text

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",  # Этот параметр больше не используется для языка ответа
    persona: str = "friendly",
    style: str = "steps",
    image_base64: Optional[str] = None,
) -> str:
    """
    Отправка запроса в OpenAI (с поддержкой фото)
    OpenAI сам определяет язык и отвечает на том же языке
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Извлекаем текущее сообщение пользователя
    current_message = extract_user_message(user_text)
    
    # Определяем язык сообщения
    detected_lang = detect_language(current_message)
    
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    style_desc = STYLES.get(style, STYLES["steps"])
    
    system_prompt = f"""You are a {persona} assistant.

YOUR PERSONALITY:
{persona_desc}

RESPONSE STYLE:
{style_desc}

IMPORTANT RULES:
- ALWAYS respond in the SAME LANGUAGE as the user's message
- If user writes in Russian, answer in Russian
- If user writes in English, answer in English
- If user writes in Kazakh, answer in Kazakh
- If user writes in Turkish, answer in Turkish
- If user writes in Ukrainian, answer in Ukrainian
- If user writes in French, answer in French
- Be consistent with your personality
- Never switch languages mid-conversation"""

    # Формируем сообщения
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Если есть фото, добавляем его
    if image_base64:
        # Убираем префикс data:image/...;base64, если есть
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
            
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": current_message or "What's in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        })
    else:
        messages.append({"role": "user", "content": current_message})

    temps = {
        "fun": 0.95, "friendly": 0.85, "smart": 0.7, "strict": 0.4
    }
    temperature = temps.get(persona, 0.7)

    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview" if image_base64 else OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=800 if image_base64 else 600,
            presence_penalty=0.6,
            frequency_penalty=0.6,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Извините, ошибка. Попробуйте позже."

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)