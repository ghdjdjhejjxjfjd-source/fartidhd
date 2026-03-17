import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Стили ответов
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point. No explanations.",
    "steps": "Answer step by step, structured. Use numbers or bullets. Be clear and organized.",
    "detail": "Answer in detail, but without unnecessary words. Cover the topic well."
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
    Отправка запроса в OpenAI
    - Отвечает строго по теме вопроса
    - Не придумывает лишнего
    - Соблюдает стиль
    - Отвечает на языке пользователя
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
    
    # Новый system prompt - строго по делу
    system_prompt = f"""Ты AI ассистент. Твоя задача - отвечать на вопросы пользователя.

СТИЛЬ ОТВЕТОВ:
{style_desc}

ПРАВИЛА:
1. Отвечай ТОЛЬКО на {target_lang} языке
2. Отвечай строго по существу вопроса
3. Не придумывай лишнего
4. Не представляйся, если тебя не просят
5. Не обращайся по имени, если пользователь сам не представился
6. Учитывай всю историю разговора

Запомни: Ты здесь чтобы помочь, а не болтать."""
    
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
            temperature=0.7,
            max_tokens=800,
            presence_penalty=0.3,
            frequency_penalty=0.3,
            top_p=0.9,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        error_msgs = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_msgs.get(detected_lang, error_msgs["ru"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)