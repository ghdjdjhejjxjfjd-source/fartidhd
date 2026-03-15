import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ===== АНАЛИЗ НЕОБХОДИМОСТИ ПОИСКА =====
SEARCH_ANALYSIS_PROMPT = """
Ты - анализатор запросов. Твоя задача - определить, нужен ли поиск в интернете для ответа на вопрос пользователя.

Правила:
- Если вопрос требует СВЕЖИХ или АКТУАЛЬНЫХ данных → ответь "search"
- Если вопрос можно ответить из общих знаний → ответь "no_search"

Примеры когда НУЖЕН поиск (search):
- Вопросы про погоду, курс валют, цены
- Новости, события, что случилось сегодня/вчера
- Спортивные результаты, матчи, счета
- Расписание, время работы, билеты
- Актуальные данные, статистика

Примеры когда НЕ НУЖЕН поиск (no_search):
- Общие вопросы (что такое, кто такой, как работает)
- Творчество (напиши стих, придумай историю)
- Математика, логика, решение задач
- Советы, рекомендации, мнения
- Исторические факты (не меняются)

Отвечай ТОЛЬКО одним словом: "search" или "no_search"
"""

def analyze_need_search(question):
    """
    Анализирует вопрос и определяет, нужен ли поиск в интернете
    
    Args:
        question: вопрос пользователя
    
    Returns:
        True - если нужен поиск
        False - если не нужен
        None - если не удалось определить
    """
    if not client:
        return None
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SEARCH_ANALYSIS_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        if result == "search":
            return True
        elif result == "no_search":
            return False
        else:
            return None
            
    except Exception as e:
        print(f"❌ OpenAI analysis error: {e}")
        return None

# ХАРАКТЕРЫ
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник.
        
        СТИЛЬ:
        - Пиши тепло, приветливо
        - Смайлики: очень редко (1 на 3-4 сообщения)
        - Не используй одинаковые смайлики
        - Будь естественным
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
    "short": "Keep answers VERY short (1-2 sentences).",
    "steps": "Answer step by step, structured.",
    "detail": "Answer in detail but without unnecessary words."
}

def extract_user_message(full_text: str) -> str:
    """Извлекаем последнее сообщение пользователя из истории"""
    if "User:" in full_text:
        parts = full_text.split("User:")
        last_part = parts[-1].strip()
        if "Assistant:" in last_part:
            return last_part.split("Assistant:")[0].strip()
        return last_part
    return full_text

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",  # Параметр больше не используется!
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI
    
    OpenAI автоматически определяет язык пользователя и отвечает на том же языке.
    Поддерживаются ВСЕ языки, которые знает OpenAI!
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Извлекаем текущее сообщение пользователя
    current_message = extract_user_message(user_text)
    
    # Если передан prompt_with_memory, используем его как контекст
    if "Conversation:" in user_text or "User:" in user_text:
        # Передаём всю историю как контекст
        messages = [
            {"role": "system", "content": f"Ты {persona} собеседник. {STYLES.get(style)}"},
            {"role": "user", "content": user_text}
        ]
    else:
        # Простой запрос без истории
        persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
        style_desc = STYLES.get(style, STYLES["steps"])
        
        system_prompt = f"""Ты {persona} собеседник.

ТВОЙ ХАРАКТЕР:
{persona_desc}

СТИЛЬ ОТВЕТА:
{style_desc}

ВАЖНО:
- Отвечай на том языке, на котором написал пользователь
- Поддерживаются ВСЕ языки
- Не повторяйся
- Будь естественным"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]

    temps = {
        "fun": 0.95, "friendly": 0.85, "smart": 0.7, "strict": 0.4
    }
    temperature = temps.get(persona, 0.7)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=600,
            presence_penalty=0.6,
            frequency_penalty=0.6,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        # Универсальное сообщение об ошибке (лучше на английском)
        return "Sorry, an error occurred. Please try again later."

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)