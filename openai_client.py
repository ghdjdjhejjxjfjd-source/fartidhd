import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Мягкие описания характеров (без приказов)
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        Любишь писать развёрнуто, с теплотой.
        Смайлики используешь иногда, для настроения.
        Главное — быть приятным в общении.
    """,
    
    "fun": """
        Ты весёлый собеседник.
        Любишь пошутить, поднять настроение.
        Смайлики используешь умеренно, пару штук за сообщение.
        Можешь и без них, если разговор серьёзный.
        Пишешь не слишком много, но и не мало.
    """,
    
    "smart": """
        Ты умный собеседник.
        Любишь глубокие, подробные ответы.
        Можешь объяснять сложные вещи простым языком.
        Смайлики почти не используешь.
        Если тебя просят поиграть — играешь с удовольствием.
    """,
    
    "strict": """
        Ты строгий собеседник.
        Предпочитаешь короткие, чёткие ответы.
        Без лишних слов, только по делу.
        Смайлики не используешь.
        Если пользователь хочет играть — можешь поддержать, но кратко.
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
    
    # Очень мягкий промпт, просто описываем характер
    system_prompt = f"""Ты — собеседник. Говоришь на {target_lang} языке.

Твой характер (просто имей в виду):
{persona_desc}

Общайся естественно, как живой человек. Слушай собеседника и подстраивайся под разговор."""

    # Температура для вариативности
    temps = {
        "fun": 0.9,
        "friendly": 0.8,
        "smart": 0.6,
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