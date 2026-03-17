import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = "gpt-4o-mini"  # ← новая модель

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
    Отправка запроса в OpenAI GPT-4o-mini
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    history, last_question = parse_conversation(user_text)
    
    if not last_question:
        last_question = user_text
    
    detected_lang = detect_language(last_question)
    
    lang_names = {
        "ru": "русском",
        "kk": "казахском",
        "en": "английском",
        "tr": "турецком",
        "uk": "украинском",
        "fr": "французском"
    }
    target_lang = lang_names.get(detected_lang, "русском")
    
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # System prompt для GPT-4o-mini
    system_prompt = f"""Ты полезный помощник. Отвечай на {target_lang} языке.

СТИЛЬ ОТВЕТА:
{style_desc}

ПРАВИЛА:
- Отвечай строго по теме
- Учитывай всю историю разговора
- Будь полезным"""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for i, msg in enumerate(history):
        if i == len(history) - 1 and msg["role"] == "user" and msg["content"] == last_question:
            continue
        messages.append(msg)
    
    messages.append({"role": "user", "content": last_question})
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=1000,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        error_msgs = {
            "ru": "Ошибка. Попробуйте позже.",
            "kk": "Қате. Қайталаңыз.",
            "en": "Error. Try again.",
            "tr": "Hata. Tekrar deneyin.",
            "uk": "Помилка. Спробуйте ще.",
            "fr": "Erreur. Réessayez."
        }
        return error_msgs.get(detected_lang, error_msgs["ru"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)