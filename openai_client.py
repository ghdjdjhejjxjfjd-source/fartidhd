import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Стили ответов
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point.",
    "steps": "Answer step by step, structured. Use numbers or bullets.",
    "detail": "Answer in detail, but without unnecessary words. Cover the topic."
}

def extract_user_message(full_text: str) -> str:
    """Извлекаем последнее сообщение пользователя из истории"""
    if "User:" in full_text:
        parts = full_text.split("User:")
        last_part = parts[-1].strip()
        if "Assistant:" in last_part:
            return last_part.split("Assistant:")[0].strip()
        return last_part
    return full_text

def detect_user_language(text: str) -> str:
    """
    Простое определение языка по тексту
    Возвращает "ru", "en" и т.д.
    """
    # Русские буквы
    if any('а' <= c.lower() <= 'я' for c in text):
        return "ru"
    # Казахские буквы (специфические)
    if any(c in 'әіңғүұқөһ' for c in text.lower()):
        return "kk"
    # Турецкие буквы
    if any(c in 'çğıöşü' for c in text.lower()):
        return "tr"
    # Украинские буквы
    if any(c in 'їєіґ' for c in text.lower()):
        return "uk"
    # Французские буквы
    if any(c in 'éèêëàâçîïôûù' for c in text.lower()):
        return "fr"
    # По умолчанию - английский
    return "en"

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",  # Этот параметр больше не используется!
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI
    
    Правила:
    1. OpenAI полностью свободен
    2. Отвечает НА ЯЗЫКЕ ПОЛЬЗОВАТЕЛЯ (определяет автоматически)
    3. Если не может определить - отвечает на английском
    4. Следует только стилю ответа (short/steps/detail)
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Определяем язык последнего сообщения пользователя
    last_message = extract_user_message(user_text)
    detected_lang = detect_user_language(last_message)
    
    # Получаем описание стиля
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Создаем system prompt
    system_prompt = f"""You are a free AI assistant. No restrictions on personality.

Your only rule: {style_desc}

LANGUAGE INSTRUCTION (VERY IMPORTANT):
- Look at the user's message and identify its language
- Respond in EXACTLY the SAME language as the user's message
- If the user writes in Russian, answer in Russian
- If the user writes in English, answer in English
- If the user writes in Kazakh, answer in Kazakh
- If the user writes in Turkish, answer in Turkish
- If the user writes in Ukrainian, answer in Ukrainian
- If the user writes in French, answer in French
- If you cannot determine the language, respond in English

This is CRITICAL: Always match the user's language!"""
    
    # Формируем сообщения
    if "Conversation:" in user_text or "User:" in user_text:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=800,
            presence_penalty=0.3,
            frequency_penalty=0.3,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        # Сообщение об ошибке на определенном языке
        error_msgs = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_msgs.get(detected_lang, error_msgs["en"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)