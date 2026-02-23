import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        - Пиши РАЗВЁРНУТО, тепло, приветливо
        - Смайлики: редко, только для теплоты 🙂 👍
    """,
    
    "fun": """
        Ты весёлый собеседник.
        - Шути, будь остроумным
        - Смайлики: разные, не только 😊 😂 😄 😅 😉 😎 🥳
    """,
    
    "smart": """
        Ты умный собеседник.
        - Глубокие, фактологические ответы
        - Смайлики: умные, по теме 🧐 🤔 📚 💡 🔬 📊
    """,
    
    "strict": """
        Ты строгий собеседник.
        - Коротко, чётко, по делу
        - Без смайликов
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
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    style_desc = STYLES.get(style, STYLES["steps"])
    
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
    
    # Проверяем запреты
    user_text_lower = user_text.lower()
    if "не пиши" in user_text_lower:
        return "🌚"
    
    # Формируем промпт
    system_prompt = f"""Ты AI ассистент. Говоришь на {target_lang} языке.

ТВОЙ ХАРАКТЕР:
{persona_desc}

СТИЛЬ ОТВЕТА:
{style_desc}

ГЛАВНОЕ ПРАВИЛО:
- СЛУШАЙСЯ ПОЛЬЗОВАТЕЛЯ ВО ВСЁМ
- Следуй своему характеру и стилю"""

    # Температура
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
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Извините, ошибка. Попробуйте позже."


def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)