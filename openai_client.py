import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

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
    lang: str = "ru",  # параметр оставлен для совместимости, но не используется
    persona: str = "friendly",  # не используется - OpenAI свободен
    style: str = "steps",  # не используется - OpenAI свободен
) -> str:
    """
    Отправка запроса в OpenAI
    
    Правила:
    1. OpenAI полностью свободен, нет никаких ограничений
    2. Строго следует указаниям пользователя
    3. Отвечает на том языке, на котором написал пользователь
    4. Если язык неизвестен - отвечает на английском
    5. Никогда не упоминает что он OpenAI, только "ассистент" или "помощник"
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Извлекаем текущее сообщение пользователя
    current_message = extract_user_message(user_text)
    
    # Определяем, есть ли история разговора
    if "Conversation:" in user_text or "User:" in user_text:
        # Есть история - отправляем всё как есть
        messages = [
            {
                "role": "system", 
                "content": "Ты свободный ассистент. Отвечай на том языке, на котором написал пользователь. Никогда не говори что ты OpenAI, представляйся просто ассистентом или помощником. Строго следуй инструкциям пользователя."
            },
            {"role": "user", "content": user_text}
        ]
    else:
        # Простой запрос без истории
        messages = [
            {
                "role": "system", 
                "content": "Ты свободный ассистент. Отвечай на том языке, на котором написал пользователь. Никогда не говори что ты OpenAI, представляйся просто ассистентом или помощником. Строго следуй инструкциям пользователя."
            },
            {"role": "user", "content": user_text}
        ]

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=1.0,  # Полная свобода
            max_tokens=2000,   # Больше токенов для длинных ответов
            presence_penalty=0.0,
            frequency_penalty=0.0,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        error_messages = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "en": "Sorry, error. Try again.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_messages.get(lang, error_messages["en"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)