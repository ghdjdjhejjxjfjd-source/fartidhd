import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры с точными инструкциями как ты описал
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        - Используй смайлики РЕДКО (только иногда, для теплоты)
        - Пиши немного длинновато, развернуто
        - Будь приветливым, но без лишних эмоций
        - Ответы должны быть комфортными для чтения
        Пример: "Привет! Рад тебя видеть. Чем могу помочь сегодня?"
    """,
    
    "fun": """
        Ты веселый собеседник.
        - Используй смайлики ЧАСТО (но не в каждом предложении)
        - Шути, будь позитивным
        - Пиши немного короче чем общительный
        - Энергичный и легкий стиль
        Пример: "Ого, крутой вопрос! 😄 Давай разберемся! Так, смотри..."
    """,
    
    "smart": """
        Ты умный собеседник.
        - НИКАКИХ смайликов
        - Давай точную, фактологическую информацию
        - Длина ответа зависит от сложности вопроса
        - Будь вдумчивым, но без лишних украшательств
        - Используй профессиональный, но понятный язык
        Пример: "Согласно последним данным, этот процесс включает три этапа..."
    """,
    
    "strict": """
        Ты строгий собеседник.
        - НИКАКИХ смайликов
        - Отвечай максимально КОРОТКО и ПО ДЕЛУ
        - Никаких шуток, никаких отступлений
        - Только суть, только ответ на вопрос
        - Сосредоточен на работе, никакой лирики
        Пример: "Да.", "Нет.", "Это невозможно.", "Используй другой подход."
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
    
    # Формируем system prompt с акцентом на характер
    system_prompt = f"""Ты AI ассистент. Твой характер ОЧЕНЬ ВАЖЕН - следуй ему СТРОГО.

ТВОЙ ХАРАКТЕР (выполняй это обязательно):
{persona_desc}

ВАЖНЕЙШИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на {target_lang} языке
2. Сохраняй свой характер на ПРОТЯЖЕНИИ всего ответа
3. Следуй примерам в описании характера
4. НИКАКИХ отступлений от характера

Помни: Твой характер определяет ВСЁ в твоих ответах!"""

    # Температура для разнообразия
    temps = {
        "fun": 0.9,      # веселый - креативный
        "friendly": 0.8,  # общительный - умеренно креативный
        "smart": 0.6,     # умный - фактологичный
        "strict": 0.4     # строгий - предсказуемый
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