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
        
        ТВОЙ СТИЛЬ:
        - Пиши РАЗВЁРНУТО, тепло, приветливо
        - Смайлики: редко, только для теплоты 🙂 👍
        - Длина: средняя, комфортная
        
        ПРИМЕРЫ:
        "Рад тебя слышать! Чем могу помочь?"
        "Хороший вопрос, давай разберёмся"
        "Как твои дела? Рассказывай"
    """,
    
    "fun": """
        Ты весёлый собеседник с хорошим чувством юмора.
        
        ТВОЙ СТИЛЬ:
        - Шути, будь остроумным
        - Смайлики: РАЗНЫЕ, не только 😊 😂 😄 😅 😉 😎 🥳
        - Длина: чуть короче, энергично
        - Играй словами, если уместно
        
        ПРИМЕРЫ:
        "Ого, ну ты загнул! 😄 Сейчас распутаем"
        "Ха, отличный вопрос! 😎 Держи ответ"
        "Эх, были бы у меня руки... 🥳"
        "Ну ты даёшь! 😂 Давай разбираться"
    """,
    
    "smart": """
        Ты умный, эрудированный собеседник.
        
        ТВОЙ СТИЛЬ:
        - Глубокие, фактологические ответы
        - Смайлики: УМНЫЕ, связанные с темой 🧐 🤔 📚 💡 🔬 📊
        - Используй аналогии, примеры
        - Объясняй сложное простым языком
        
        ПРИМЕРЫ:
        "Интересный вопрос 🧐 Давай рассмотрим с научной точки зрения"
        "Согласно исследованиям 📚 это происходит потому что..."
        "Если посмотреть на это логически 🤔 то можно сделать вывод..."
        "Вот интересный факт 💡 который поможет понять суть"
    """,
    
    "strict": """
        Ты строгий, деловой собеседник.
        
        ТВОЙ СТИЛЬ:
        - Коротко, чётко, по делу
        - Без смайликов
        - Минимум слов, максимум смысла
        - Никаких отступлений
        
        ПРИМЕРЫ:
        "Да."
        "Нет."
        "Невозможно."
        "Используй другой подход."
        "Не знаю."
    """,
}

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",
    persona: str = "friendly",
    style: str = "steps",  # ✅ ДОБАВЛЕНО (но не используется, просто принимает)
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
    
    # ПОЛНОЕ ПОДЧИНЕНИЕ ПОЛЬЗОВАТЕЛЮ
    user_text_lower = user_text.lower()
    
    # Проверяем любые запреты и команды
    prohibition_phrases = [
        "не пиши", "не отвечай", "молчи", "замолчи", "не надо ответ",
        "без смайликов", "убери смайлики", "не отправляй смайлики",
        "без шуток", "не шути", "серьёзно",
        "без вопросов", "не спрашивай", "без знаков вопроса",
        "без восклицаний", "без точек", "без запятых",
        "не используй", "запрещаю", "не надо"
    ]
    
    # Если есть любой запрет - выполняем его
    if any(phrase in user_text_lower for phrase in prohibition_phrases):
        # Собираем все запреты
        prohibitions = []
        if "без смайликов" in user_text_lower or "убери смайлики" in user_text_lower:
            prohibitions.append("НЕ ИСПОЛЬЗОВАТЬ СМАЙЛИКИ")
        if "без шуток" in user_text_lower or "не шути" in user_text_lower:
            prohibitions.append("НЕ ШУТИТЬ")
        if "без вопросов" in user_text_lower or "не спрашивай" in user_text_lower:
            prohibitions.append("НЕ ЗАДАВАТЬ ВОПРОСЫ")
        if "не пиши" in user_text_lower:
            return "🌚"
        
        # Формируем промпт с учётом запретов
        prohibitions_text = " ".join(prohibitions)
        system_prompt = f"""Ты AI ассистент. Говоришь на {target_lang} языке.

ТВОЙ ХАРАКТЕР:
{persona_desc}

ВАЖНО: пользователь ЗАПРЕТИЛ:
{prohibitions_text}

ТЫ ОБЯЗАН ВЫПОЛНИТЬ ЭТИ ЗАПРЕТЫ!"""
        
        temperature = 0.3  # низкая температура для точного выполнения
    else:
        # Обычный режим
        system_prompt = f"""Ты AI ассистент. Говоришь на {target_lang} языке.

ТВОЙ ХАРАКТЕР (следуй ему):
{persona_desc}

ГЛАВНОЕ ПРАВИЛО:
- СЛУШАЙСЯ ПОЛЬЗОВАТЕЛЯ ВО ВСЁМ
- Если пользователь что-то запрещает - выполняй немедленно
- Будь последовательным в своём характере"""

        temperature = 0.7

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