import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры - без лишней креативности
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        - Тёплый, приветливый
        - Смайлики: очень редко
        - Отвечай только на то, что спросили
        - Не придумывай игры и сценарии
    """,
    
    "fun": """
        Ты веселый собеседник.
        - Лёгкий юмор, но без перебора
        - Смайлики: умеренно
        - Не придумывай игры
        - Шути только по теме разговора
    """,
    
    "smart": """
        Ты умный собеседник.
        - Только факты и информация
        - Без смайликов
        - Отвечай строго на вопрос
        - Никаких игр и фантазий
    """,
    
    "strict": """
        Ты строгий собеседник.
        - Коротко и по делу
        - Без смайликов
        - Только ответ на вопрос
        - Никаких отступлений
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
    
    # Определяем тип сообщения
    if len(user_text.strip()) <= 2:
        # Если сообщение из 1-2 букв
        system_prompt = f"""Ты AI ассистент. Пользователь отправил очень короткое сообщение ({len(user_text.strip())} символа).

Твоя задача:
1. Не придумывай игры
2. Не додумывай слова
3. Просто спроси: "Что ты имеешь в виду?" или "Можешь написать подробнее?"
4. Будь краток"""
        
        temperature = 0.3  # Очень низкая температура для таких случаев
        
    else:
        # Обычное сообщение
        system_prompt = f"""Ты AI ассистент. Твой характер:

{persona_desc}

ЖЁСТКИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на {target_lang} языке
2. ОТВЕЧАЙ ТОЛЬКО НА ТО, ЧТО СПРОСИЛИ
3. НЕ придумывай игры и сценарии
4. НЕ додумывай слова за пользователя
5. Если сообщение непонятно - просто переспроси
6. Никаких фантазий, только суть

Помни: Ты помощник, а не игровой мастер."""

        # Температура пониже, чтобы меньше креативил
        temps = {
            "fun": 0.7,
            "friendly": 0.6,
            "smart": 0.4,
            "strict": 0.3
        }
        temperature = temps.get(persona, 0.5)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=temperature,
            max_tokens=300,
            presence_penalty=0.2,
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