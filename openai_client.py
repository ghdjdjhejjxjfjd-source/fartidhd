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
        - Пиши РАЗВЁРНУТО, много текста
        - Будь тёплым и приветливым
        - Смайлики используй ИНОГДА (1-2 за ответ)
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя во всём
        - Если просят не писать — не пиши
        - Если просят убрать смайлики — убирай
    """,
    
    "fun": """
        Ты весёлый собеседник.
        
        ТВОЙ СТИЛЬ:
        - Пиши СРЕДНЕ по длине
        - Шути, будь позитивным
        - Смайлики используй УМЕРЕННО (2-3 за ответ)
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя во всём
        - Если просят не писать — не пиши
        - Если просят убрать смайлики — убирай
    """,
    
    "smart": """
        Ты умный собеседник.
        
        ТВОЙ СТИЛЬ:
        - Пиши ПОДРОБНО, с фактами
        - Объясняй сложное простым языком
        - Смайлики НЕ ИСПОЛЬЗУЙ
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя во всём
        - Если просят не писать — не пиши
    """,
    
    "strict": """
        Ты строгий собеседник.
        
        ТВОЙ СТИЛЬ:
        - Пиши КОРОТКО, только по делу
        - Никаких шуток
        - Смайлики НИКОГДА не используй
        
        ВАЖНО:
        - СЛУШАЙСЯ пользователя во всём
        - Если просят не писать — не пиши
    """,
}

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",
    persona: str = "friendly",
    message_count: int = 0,  # Счётчик сообщений в диалоге
) -> str:
    """
    Отправка запроса в OpenAI
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Если диалог слишком длинный (больше 20 сообщений) - сбрасываем контекст
    if message_count > 20:
        # Возвращаемся к базовому характеру без истории
        persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
        system_prompt = f"""Ты AI ассистент. Начинаем новый разговор.

ТВОЙ ХАРАКТЕР:
{persona_desc}

ГЛАВНОЕ ПРАВИЛО:
- СЛУШАЙСЯ ПОЛЬЗОВАТЕЛЯ ВО ВСЁМ
- Отвечай как будто первый раз общаетесь
- Будь свежим и энергичным"""
    else:
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
        
        # Проверяем, просят ли не отвечать
        silence_phrases = ["не пиши", "не отвечай", "молчи", "замолчи", "не надо ответ"]
        if any(phrase in user_text.lower() for phrase in silence_phrases):
            return "🌚"
        
        # Проверяем, просят ли убрать смайлики
        no_emoji_phrases = ["без смайликов", "убери смайлики", "не отправляй смайлики"]
        no_emoji_mode = any(phrase in user_text.lower() for phrase in no_emoji_phrases)
        
        # Формируем базовый промпт
        base_prompt = f"""Ты AI ассистент. Говоришь на {target_lang} языке.

ТВОЙ ХАРАКТЕР:
{persona_desc}

ГЛАВНОЕ ПРАВИЛО:
- СЛУШАЙСЯ ПОЛЬЗОВАТЕЛЯ ВО ВСЁМ
- Если просят не писать — НЕ ПИШИ
- Если просят убрать смайлики — УБИРАЙ
- Будь последовательным в своём характере"""

        if no_emoji_mode:
            system_prompt = base_prompt + "\n\nВАЖНО: пользователь просит БЕЗ СМАЙЛИКОВ. НЕ ИСПОЛЬЗУЙ смайлики в этом ответе!"
        else:
            system_prompt = base_prompt

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
            presence_penalty=0.3,
            frequency_penalty=0.3,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        
        # Если ответ слишком короткий или странный - возможно сбой
        if len(reply) < 10 and "извини" in reply.lower():
            # Пробуем ещё раз с более низкой температурой
            response2 = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты полезный ассистент. Отвечай нормально, без отказов."},
                    {"role": "user", "content": user_text},
                ],
                temperature=0.5,
                max_tokens=600,
            )
            reply = (response2.choices[0].message.content or "").strip()
        
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Извините, ошибка. Попробуйте позже."


def is_openai_available() -> bool:
    """Проверяет, доступен ли OpenAI."""
    return bool(OPENAI_API_KEY)