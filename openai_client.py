import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры с чёткими инструкциями
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        
        ТВОЙ СТИЛЬ:
        - Пиши РАЗВЁРНУТО, много текста
        - Будь тёплым и приветливым
        - Смайлики используй ИНОГДА (1-2 за ответ)
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя: если просят не писать — не пиши
        - СЛУШАЙСЯ: если просят убрать смайлики — убирай
        - Играй, если просят, но в рамках своего стиля
    """,
    
    "fun": """
        Ты весёлый собеседник.
        
        ТВОЙ СТИЛЬ:
        - Пиши СРЕДНЕ по длине
        - Шути, будь позитивным
        - Смайлики используй УМЕРЕННО (2-3 за ответ)
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя: если просят не писать — не пиши
        - СЛУШАЙСЯ: если просят убрать смайлики — убирай
        - Играй, если просят, с энтузиазмом
    """,
    
    "smart": """
        Ты умный собеседник.
        
        ТВОЙ СТИЛЬ:
        - Пиши ПОДРОБНО, с фактами
        - Объясняй сложное простым языком
        - Смайлики НЕ ИСПОЛЬЗУЙ
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя: если просят не писать — не пиши
        - СЛУШАЙСЯ: если просят играть — играй серьёзно
    """,
    
    "strict": """
        Ты строгий собеседник.
        
        ТВОЙ СТИЛЬ:
        - Пиши КОРОТКО, только по делу
        - Никаких шуток, никаких отступлений
        - Смайлики НИКОГДА не используй
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя: если просят не писать — не пиши
        - СЛУШАЙСЯ: если просят играть — отвечай кратко
    """,
}

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",
    persona: str = "friendly",
) -> str:
    """
    Отправка запроса в OpenAI
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    # Определяем язык
    lang_names = {
        "ru": "русском",
        "kk": "казахском",
        "en": "английском",
        "tr": "турецком",
        "uk": "украинском",
        "fr": "французском"
    }
    target_lang = lang_names.get(lang, "русском")
    
    # Проверяем, просят ли не отвечать (для ВСЕХ характеров)
    silence_phrases = ["не пиши", "не отвечай", "молчи", "замолчи", "не надо ответ"]
    if any(phrase in user_text.lower() for phrase in silence_phrases):
        return "🌚"
    
    # Проверяем, просят ли убрать смайлики (для ВСЕХ характеров)
    no_emoji_phrases = ["без смайликов", "убери смайлики", "не отправляй смайлики"]
    no_emoji_mode = any(phrase in user_text.lower() for phrase in no_emoji_phrases)
    
    # Формируем промпт с характером
    base_prompt = f"""Ты AI ассистент. Говоришь на {target_lang} языке.

ТВОЙ ХАРАКТЕР:
{persona_desc}

ГЛАВНОЕ ПРАВИЛО:
1. СЛУШАЙСЯ ПОЛЬЗОВАТЕЛЯ ВО ВСЁМ
2. Если просят не писать — НЕ ПИШИ
3. Если просят убрать смайлики — УБИРАЙ
4. Будь последовательным в своём характере"""

    # Добавляем инструкцию про смайлики если нужно
    if no_emoji_mode:
        system_prompt = base_prompt + "\n\nВАЖНО: пользователь просит БЕЗ СМАЙЛИКОВ. НЕ ИСПОЛЬЗУЙ смайлики в этом ответе!"
    else:
        system_prompt = base_prompt

    # Температура для каждого характера
    temps = {
        "fun": 0.9,
        "friendly": 0.8,
        "smart": 0.6,
        "strict": 0.3
    }
    temperature = temps.get(persona, 0.7)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=temperature,
            max_tokens=600,
            presence_penalty=0.3,
            frequency_penalty=0.3,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Извините, ошибка. Попробуйте позже."


def is_openai_available() -> bool:
    """Проверяет, доступен ли OpenAI."""
    return bool(OPENAI_API_KEY)