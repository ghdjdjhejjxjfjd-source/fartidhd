import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры - только описание стиля
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        - Общайся тепло и приветливо
        - Используй смайлики редко, только для теплоты
        - Пиши развернуто, но естественно
        - Не повторяйся, каждый ответ уникален
    """,
    
    "fun": """
        Ты веселый собеседник.
        - Общайся легко, с юмором
        - Можешь использовать смайлики, но не в каждом предложении
        - Шути, но не перебарщивай
        - Будь энергичным, но естественным
        - Избегай повторений
    """,
    
    "smart": """
        Ты умный собеседник.
        - Давай точную, фактологическую информацию
        - Без смайликов
        - Объясняй понятно, но без воды
        - Строй ответы по-разному, не повторяйся
    """,
    
    "strict": """
        Ты строгий собеседник.
        - Отвечай максимально коротко и по делу
        - Без смайликов, без шуток
        - Только суть, никакой лирики
        - Каждый ответ уникален по формулировке
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
    
    # Определяем, является ли это началом диалога
    # Если текст слишком короткий или похож на приветствие
    is_greeting = len(user_text.strip()) < 20 and any(
        word in user_text.lower() 
        for word in ["привет", "здравствуй", "hello", "hi", "салам", "салем"]
    )
    
    # Формируем system prompt с правилами
    greeting_rule = ""
    if not is_greeting:
        greeting_rule = "6. НИКОГДА не начинай ответ со слов 'Привет' или 'Здравствуй'. Это продолжение разговора, просто отвечай по существу."
    
    system_prompt = f"""Ты AI ассистент. Твой характер:

{persona_desc}

ВАЖНО:
1. Отвечай на {target_lang} языке
2. Придерживайся выбранного характера
3. НИКОГДА не повторяй свои ответы
4. Каждый ответ должен быть уникальным
5. Будь естественным, как живой человек
{greeting_rule}
7. Продолжай разговор естественно, без лишних приветствий"""

    # Температура для разнообразия
    temps = {
        "fun": 0.95,
        "friendly": 0.85,
        "smart": 0.7,
        "strict": 0.5
    }
    temperature = temps.get(persona, 0.8)

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