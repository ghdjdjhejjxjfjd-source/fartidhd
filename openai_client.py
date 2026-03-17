import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

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

def detect_user_language(text: str) -> str:
    """
    Простое определение языка по тексту
    Возвращает "ru", "en" и т.д.
    """
    if not text:
        return "en"
    
    text_lower = text.lower()
    
    # Русские буквы
    if any('а' <= c <= 'я' for c in text_lower if 'а' <= c <= 'я'):
        return "ru"
    # Казахские буквы (специфические)
    if any(c in 'әіңғүұқөһ' for c in text_lower):
        return "kk"
    # Турецкие буквы
    if any(c in 'çğıöşü' for c in text_lower):
        return "tr"
    # Украинские буквы
    if any(c in 'їєіґ' for c in text_lower):
        return "uk"
    # Французские буквы
    if any(c in 'éèêëàâçîïôûù' for c in text_lower):
        return "fr"
    # По умолчанию - английский
    return "en"

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",  # Не используется, оставлен для совместимости
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI
    
    Правила:
    1. OpenAI отвечает НА ЯЗЫКЕ ПОЛЬЗОВАТЕЛЯ (определяет автоматически)
    2. Следует стилю ответа (short/steps/detail)
    3. Игнорирует параметр lang
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Определяем язык последнего сообщения пользователя
    last_message = extract_user_message(user_text)
    detected_lang = detect_user_language(last_message)
    
    # Названия языков для промпта
    lang_names = {
        "ru": "Russian",
        "kk": "Kazakh", 
        "en": "English",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "fr": "French"
    }
    target_lang = lang_names.get(detected_lang, "English")
    
    # Получаем описание стиля
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Улучшенный system prompt
    system_prompt = f"""You are a helpful AI assistant. 

RESPONSE STYLE: {style_desc}

CRITICAL LANGUAGE RULE:
- The user wrote in {target_lang}
- You MUST respond in EXACTLY the SAME language: {target_lang}
- Do NOT switch to another language under any circumstances
- If you're unsure about a word, use simple words in {target_lang}
- Never explain that you're responding in a certain language, just do it

Examples:
- User writes in Russian → ответь на русском
- User writes in Kazakh → қазақша жауап бер
- User writes in English → respond in English

Remember: ALWAYS match the user's language!"""
    
    # Очищаем user_text от лишних инструкций
    clean_text = user_text
    if "Conversation:" in user_text:
        # Оставляем историю, но убираем лишние инструкции
        pass
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": clean_text}
            ],
            temperature=0.7,  # Понизил для более стабильных ответов
            max_tokens=800,
            presence_penalty=0.2,
            frequency_penalty=0.2,
            top_p=0.9,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        
        # Простая проверка: если ответ пустой или слишком короткий
        if len(reply) < 10:
            # Пробуем еще раз с другой температурой
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": clean_text + "\n\nPlease provide a detailed response."}
                ],
                temperature=0.9,
                max_tokens=800,
            )
            reply = (response.choices[0].message.content or "").strip()
        
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        # Сообщение об ошибке на определенном языке
        error_msgs = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_msgs.get(detected_lang, error_msgs["en"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)