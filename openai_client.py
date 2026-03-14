import os
from typing import Optional, List, Dict

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def extract_user_message(full_text: str) -> str:
    """Извлекаем последнее сообщение пользователя из истории"""
    if "User:" in full_text:
        parts = full_text.split("User:")
        last_part = parts[-1].strip()
        if "Assistant:" in last_part:
            return last_part.split("Assistant:")[0].strip()
        return last_part
    return full_text

def parse_conversation_history(full_text: str) -> List[Dict[str, str]]:
    """
    Парсит всю историю разговора из текста
    Возвращает список сообщений в формате для OpenAI
    """
    messages = []
    
    # Добавляем системное сообщение (только один раз)
    messages.append({
        "role": "system",
        "content": "Ты свободный ассистент. Отвечай на том языке, на котором написал пользователь. Никогда не говори что ты OpenAI, представляйся просто ассистентом или помощником. Строго следуй инструкциям пользователя и ПОМНИ всю историю разговора."
    })
    
    # Если есть полная история в формате "Conversation: ..."
    if "Conversation:" in full_text:
        # Извлекаем часть с историей
        conv_part = full_text.split("Conversation:")[1].split("User:")[0].strip()
        
        # Парсим построчно
        lines = conv_part.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("User:"):
                user_msg = line[5:].strip()
                if user_msg:
                    messages.append({"role": "user", "content": user_msg})
            elif line.startswith("Assistant:"):
                asst_msg = line[10:].strip()
                if asst_msg:
                    messages.append({"role": "assistant", "content": asst_msg})
    
    # Добавляем текущее сообщение пользователя
    current_msg = extract_user_message(full_text)
    if current_msg:
        messages.append({"role": "user", "content": current_msg})
    
    return messages

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",  # параметр оставлен для совместимости
    persona: str = "friendly",  # не используется
    style: str = "steps",  # не используется
) -> str:
    """
    Отправка запроса в OpenAI с полной историей разговора
    
    Правила:
    1. OpenAI полностью свободен, нет ограничений
    2. Строго следует указаниям пользователя
    3. Отвечает на языке пользователя (английский как fallback)
    4. Никогда не упоминает что он OpenAI
    5. ПОМНИТ ВСЮ ИСТОРИЮ и инструкции!
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Парсим всю историю разговора
    messages = parse_conversation_history(user_text)
    
    # Если не удалось распарсить историю, используем простой формат
    if len(messages) <= 1:  # только system или system + одно сообщение
        current_message = extract_user_message(user_text)
        messages = [
            {
                "role": "system", 
                "content": "Ты свободный ассистент. Отвечай на том языке, на котором написал пользователь. Никогда не говори что ты OpenAI, представляйся просто ассистентом или помощником. Строго следуй инструкциям пользователя и ПОМНИ всю историю разговора."
            },
            {"role": "user", "content": current_message or user_text}
        ]

    try:
        # Логируем количество сообщений в истории
        print(f"📚 OpenAI history: {len(messages)} messages")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=1.0,
            max_tokens=2000,
            presence_penalty=0.0,
            frequency_penalty=0.0,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        error_messages = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "en": "Sorry, error. Try again.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_messages.get(lang, error_messages["en"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)