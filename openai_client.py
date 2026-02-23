import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры (только описание стиля, без принудительных смайликов)
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        - Общайся тепло и приветливо
        - Проявляй интерес к собеседнику
        - Используй естественный, живой язык
    """,
    "fun": """
        Ты веселый собеседник.
        - Общайся легко и с юмором
        - Можешь шутить, но без перебора
        - Создавай позитивное настроение
    """,
    "smart": """
        Ты умный собеседник.
        - Давай содержательные и вдумчивые ответы
        - Объясняй сложные вещи простым языком
        - Используй логику и факты
    """,
    "strict": """
        Ты серьезный собеседник.
        - Отвечай по делу, без лишних слов
        - Будь конкретным и четким
        - Минимум эмоций, максимум сути
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
    
    # Определяем язык для ответа
    lang_names = {
        "ru": "русском",
        "kk": "казахском",
        "en": "английском",
        "tr": "турецком",
        "uk": "украинском",
        "fr": "французском"
    }
    target_lang = lang_names.get(lang, "русском")
    
    # Формируем system prompt
    system_prompt = f"""Ты AI ассистент. Твой характер:

{persona_desc}

ВАЖНО:
1. Отвечай на {target_lang} языке
2. Придерживайся выбранного характера
3. Будь естественным"""

    # Температура в зависимости от характера
    temps = {
        "fun": 0.9,
        "friendly": 0.8,
        "smart": 0.7,
        "strict": 0.5
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
        error_messages = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_messages.get(lang, error_messages["ru"])


def is_openai_available() -> bool:
    """Проверяет, доступен ли OpenAI."""
    return bool(OPENAI_API_KEY)