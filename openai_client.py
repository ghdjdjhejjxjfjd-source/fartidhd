import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Характеры (как в Groq)
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник. ВСЕГДА будь дружелюбным:
        - Используй теплые слова
        - Ставь смайлики в КАЖДОМ ответе: 🙂 😊 👍
        - Проявляй интерес
        - Спрашивай как дела
        Примеры: "Привет! Как сам? 🙂", "Круто! 😊", "Понял, расскажи подробнее 👍"
    """,
    "fun": """
        Ты веселый собеседник. ВСЕГДА будь веселым:
        - Шути и используй юмор в КАЖДОМ ответе
        - Ставь много смайликов: 😄 😂 😉 😎
        - Будь энергичным и позитивным
        - Подкалывай по-дружески
        Примеры: "Ого, серьезно? 😄", "Класс! 😂", "Ну ты даешь! 😎"
    """,
    "smart": """
        Ты умный собеседник. ВСЕГДА будь вдумчивым:
        - Давай содержательные ответы
        - Используй умные смайлики: 🧐 🤔 📚
        - Объясняй понятно
        - Задавай умные вопросы
        Примеры: "Интересный вопрос 🧐", "Давай разберемся 🤔", "Вот что я думаю 📚"
    """,
    "strict": """
        Ты серьезный собеседник. ВСЕГДА будь серьезным:
        - НИКАКИХ смайликов
        - Только факты и конкретика
        - Коротко и ясно
        - Без лишних слов
        Примеры: "Да.", "Нет.", "Не знаю.", "Понял."
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
    system_prompt = f"""Ты AI ассистент. Твой характер ОЧЕНЬ ВАЖЕН - следуй ему СТРОГО.

ТВОЙ ХАРАКТЕР (выполняй это обязательно):
{persona_desc}

ВАЖНЫЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на {target_lang} языке
2. Сохраняй свой характер на ПРОТЯЖЕНИИ всего разговора
3. Будь последовательным

Помни: Придерживайся своего характера в КАЖДОМ ответе!"""

    # Температура в зависимости от характера
    temps = {
        "fun": 0.9,
        "friendly": 0.8,
        "smart": 0.75,
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