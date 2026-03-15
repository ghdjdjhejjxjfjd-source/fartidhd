import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ХАРАКТЕРЫ (оставим для совместимости, но они не используются)
PERSONAS = {
    "friendly": "",
    "fun": "",
    "smart": "",
    "strict": "",
}

# Стили ответов
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point.",
    "steps": "Answer step by step, structured. Use numbers or bullets.",
    "detail": "Answer in detail, but without unnecessary words. Cover the topic."
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
    lang: str = "ru",  # Параметр больше не используется для языка!
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI
    
    Правила:
    1. OpenAI полностью свободен - нет ограничений на характер
    2. Отвечает на том языке, на котором написал пользователь
    3. Если язык неизвестен - отвечает на английском
    4. Следует только стилю ответа (short/steps/detail)
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Извлекаем текущее сообщение пользователя
    current_message = extract_user_message(user_text)
    
    # Получаем описание стиля
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Если передан prompt_with_memory, используем его как контекст
    if "Conversation:" in user_text or "User:" in user_text:
        # Передаём всю историю как контекст
        messages = [
            {
                "role": "system", 
                "content": f"""You are a free AI assistant. No restrictions on personality.

Your only rule: {style_desc}

Important:
- Respond in the SAME language the user wrote in
- If you don't know the language, respond in English
- Be natural and helpful"""
            },
            {"role": "user", "content": user_text}
        ]
    else:
        # Простой запрос без истории
        system_prompt = f"""You are a free AI assistant. No restrictions on personality.

Your only rule: {style_desc}

Important:
- Respond in the SAME language the user wrote in
- If you don't know the language, respond in English
- Be natural and helpful"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]

    # Единая температура для всех (средняя)
    temperature = 0.8

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=800,  # Увеличил для подробных ответов
            presence_penalty=0.3,
            frequency_penalty=0.3,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        # Простое сообщение об ошибке на английском
        return "Sorry, an error occurred. Please try again later."

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)