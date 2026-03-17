import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = "o1-mini"

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Стили ответов
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point.",
    "steps": "Answer step by step, structured. Use numbers or bullets.",
    "detail": "Answer in detail, but without unnecessary words."
}

def parse_conversation(full_text: str) -> tuple[list[dict[str, str]], str]:
    """
    Разбирает текст с историей и возвращает список сообщений и последний вопрос
    """
    messages = []
    last_user = ""
    
    lines = full_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("User:"):
            content = line[5:].strip()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(("User:", "Assistant:")):
                content += "\n" + lines[i].strip()
                i += 1
            messages.append({"role": "user", "content": content})
            last_user = content
            
        elif line.startswith("Assistant:"):
            content = line[10:].strip()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(("User:", "Assistant:")):
                content += "\n" + lines[i].strip()
                i += 1
            messages.append({"role": "assistant", "content": content})
            
        else:
            i += 1
    
    if not messages:
        return [], full_text
    
    return messages, last_user

def detect_language(text: str) -> str:
    """
    Определяет язык текста
    """
    if not text:
        return "ru"
    
    text_lower = text.lower()
    
    if any('а' <= c <= 'я' for c in text_lower if 'а' <= c <= 'я'):
        return "ru"
    if any(c in 'әіңғүұқөһ' for c in text_lower):
        return "kk"
    if any(c in 'çğıöşü' for c in text_lower):
        return "tr"
    if any(c in 'їєіґ' for c in text_lower):
        return "uk"
    if any(c in 'éèêëàâçîïôûù' for c in text_lower):
        return "fr"
    return "en"

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI o1-mini
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    history, last_question = parse_conversation(user_text)
    
    if not last_question:
        last_question = user_text
    
    detected_lang = detect_language(last_question)
    
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Формируем инструкцию в первом сообщении пользователя (o1-mini не поддерживает system)
    first_message = f"""Ты полезный помощник. Отвечай на том языке, на котором написан вопрос.

СТИЛЬ ОТВЕТА:
{style_desc}

ПРАВИЛА:
- Отвечай строго по теме
- Учитывай всю историю разговора ниже
- Будь полезным

История разговора:"""
    
    # Формируем список сообщений для API (только user и assistant)
    messages = []
    
    # Добавляем инструкцию как первое сообщение пользователя
    if history:
        messages.append({"role": "user", "content": first_message})
    else:
        # Если истории нет, добавляем инструкцию перед вопросом
        messages.append({"role": "user", "content": f"{first_message}\n\nВопрос: {last_question}"})
        return _send_request(messages)
    
    # Добавляем историю
    for msg in history:
        messages.append(msg)
    
    # Добавляем текущий вопрос
    messages.append({"role": "user", "content": last_question})
    
    return _send_request(messages)

def _send_request(messages):
    """Отправка запроса в OpenAI"""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_completion_tokens=1000,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Ошибка. Попробуйте позже."

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)