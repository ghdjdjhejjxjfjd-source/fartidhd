import os
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def ask_groq(
    user_text: str,
    *,
    lang: str = "ru",
    style: str = "steps",
    persona: str = "friendly",
) -> str:
    """
    Отправка запроса в Groq
    - Groq сам определяет язык по контексту
    - Никаких принудительных инструкций
    - Учитывает всю историю
    """
    if not groq_client:
        raise RuntimeError("GROQ_API_KEY is not set")

    # Просто передаем весь текст как есть
    # user_text уже содержит всю историю (User:/Assistant:)
    messages = [
        {"role": "user", "content": user_text}
    ]

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=800,
        )
        
        reply = (resp.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"Groq error: {e}")
        
        # Сообщения об ошибке на разных языках
        error_msgs = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_msgs.get(lang, error_msgs["ru"])