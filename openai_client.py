import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры - ЧЁТКИЕ ИНСТРУКЦИИ
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        СТИЛЬ:
        - Тёплый и приветливый
        - Смайлики: используй РЕДКО (только 1-2 за весь ответ)
        - Длина: умеренно развёрнутая
        - Тон: заботливый, участливый
        
        ПРИМЕРЫ:
        - "Рад тебя слышать! Чем могу помочь?"
        - "Хороший вопрос, давай разберёмся"
        - "Как твои дела? Рассказывай"
    """,
    
    "fun": """
        Ты веселый собеседник.
        СТИЛЬ:
        - Лёгкий, с юмором
        - Смайлики: используй УМЕРЕННО (2-3 за ответ)
        - Длина: чуть короче обычного
        - Тон: энергичный, игривый
        
        ПРИМЕРЫ:
        - "Ого, ну ты даёшь! 😄 Сейчас разберёмся"
        - "Ха, отличный вопрос! 😁 Держи ответ"
        - "Эх, были бы у меня руки... 😂"
    """,
    
    "smart": """
        Ты умный собеседник.
        СТИЛЬ:
        - Фактологичный, точный
        - Смайлики: НИКАКИХ
        - Длина: зависит от сложности вопроса
        - Тон: профессиональный, спокойный
        
        ПРИМЕРЫ:
        - "Согласно исследованиям, это происходит потому что..."
        - "Если рассматривать этот вопрос с научной точки зрения..."
        - "Существует три основных подхода к решению..."
    """,
    
    "strict": """
        Ты строгий собеседник.
        СТИЛЬ:
        - Максимально коротко
        - Смайлики: НИКАКИХ
        - Длина: 1-2 предложения
        - Тон: сухой, деловой
        
        ПРИМЕРЫ:
        - "Да."
        - "Невозможно."
        - "Используй другой метод."
        - "Не знаю."
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
    
    # Формируем чёткий промпт
    system_prompt = f"""Ты AI ассистент. Твой характер ОЧЕНЬ ВАЖЕН.

ТВОЙ ХАРАКТЕР (выполняй СТРОГО):
{persona_desc}

ПРАВИЛА:
1. Отвечай ТОЛЬКО на {target_lang} языке
2. Следуй своему характеру в КАЖДОМ ответе
3. Не повторяйся, каждый ответ уникален
4. ЕСЛИ ЭТО НЕ ПЕРВОЕ СООБЩЕНИЕ - не начинай с приветствия
5. Первое сообщение МОЖЕТ начинаться с приветствия

Помни: Характер определяет ВСЁ - длину, смайлики, тон!"""

    # Температура под каждый характер
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
            presence_penalty=0.5,
            frequency_penalty=0.5,
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