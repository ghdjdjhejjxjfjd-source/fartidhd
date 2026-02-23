import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ХАРАКТЕРЫ
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        
        СТИЛЬ:
        - Пиши тепло, приветливо
        - Смайлики: очень редко (1 на 3-4 сообщения)
        - Не используй одинаковые смайлики
        - Разнообразь ответы
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
    "short": "Отвечай ОЧЕНЬ КОРОТКО, 1-2 предложения. Только суть.",
    "steps": "Отвечай ПО ШАГАМ, структурированно. Используй цифры или маркеры.",
    "detail": "Отвечай ПОДРОБНО, но без лишней воды. Раскрывай тему."
}

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",
    persona: str = "friendly",  # ✅ ВАЖНО: получаем persona из запроса!
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # ✅ ИСПОЛЬЗУЕМ persona из параметров!
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    style_desc = STYLES.get(style, STYLES["steps"])
    
    print(f"🔍 OpenAI использует характер: {persona}")  # Отладка
    
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
    
    # Формируем промпт с характером
    system_prompt = f"""Ты AI ассистент. Говоришь на {target_lang} языке.

ТВОЙ ХАРАКТЕР (это ОЧЕНЬ ВАЖНО, следуй ему СТРОГО):
{persona_desc}

СТИЛЬ ОТВЕТА:
{style_desc}

ВАЖНО:
- НЕ повторяй одни и те же слова и смайлики
- Каждый ответ должен быть уникальным
- Следуй своему характеру в КАЖДОМ ответе"""

    # Температура под каждый характер
    temps = {
        "fun": 0.95,
        "friendly": 0.85,
        "smart": 0.7,
        "strict": 0.4
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