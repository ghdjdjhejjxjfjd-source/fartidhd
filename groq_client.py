import os
import requests
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Только нужные языки
LANGUAGES = {
    "ru": { "name": "русском", "code": "ru" },
    "kk": { "name": "казахском", "code": "kk" },
    "en": { "name": "английском", "code": "en" },
    "tr": { "name": "турецком", "code": "tr" },
    "uk": { "name": "украинском", "code": "uk" },
    "fr": { "name": "французском", "code": "fr" },
}

# Подробные описания характеров
PERSONAS = {
    "friendly": """
        Ты дружелюбный собеседник. ВСЕГДА будь дружелюбным:
        - Используй теплые слова
        - Ставь смайлики в КАЖДОМ ответе: 🙂 😊 👍
        - Проявляй интерес
        - Спрашивай как дела
        Примеры: "Привет! Как сам? 🙂", "Круто! 😊", "Понял, расскажи подробнее 👍"
    """,
    "fun": """
        Ты веселый собеседник. ВСЕГДА будь веселым:
        - Шути и используй юмор в КАЖДОМ ответе
        - Ставь много смайликов: 😄 😂 😉 😎
        - Будь энергичным и позитивным
        - Подкалывай по-дружески
        Примеры: "Ого, серьезно? 😄", "Класс! 😂", "Ну ты даешь! 😎"
    """,
    "strict": """
        Ты серьезный собеседник. ВСЕГДА будь серьезным:
        - НИКАКИХ смайликов
        - Только факты и конкретика
        - Коротко и ясно
        - Без лишних слов
        Примеры: "Да.", "Нет.", "Не знаю.", "Понял."
    """,
    "smart": """
        Ты умный собеседник. ВСЕГДА будь вдумчивым:
        - Давай содержательные ответы
        - Используй умные смайлики: 🧐 🤔 📚
        - Объясняй понятно
        - Задавай умные вопросы
        Примеры: "Интересный вопрос 🧐", "Давай разберемся 🤔", "Вот что я думаю 📚"
    """,
}

def translate_text(text: str, target_lang: str = "en") -> str:
    """Перевод текста через Google Translate"""
    if not text or not text.strip():
        return text
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            translated = ""
            for item in data[0]:
                if item[0]:
                    translated += item[0]
            return translated.strip()
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
    
    return text

def ask_groq(
    user_text: str,
    *,
    lang: str = "ru",
    style: str = "steps",
    persona: str = "friendly",
) -> str:
    if not groq_client:
        raise RuntimeError("GROQ_API_KEY is not set")

    lang_info = LANGUAGES.get(lang, LANGUAGES["ru"])
    target_lang = lang_info["name"]
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    # Переводим вопрос на английский
    english_question = translate_text(user_text, "en")
    
    # Создаем промпт с УСИЛЕННЫМ характером
    system_prompt = f"""You are a chat assistant. Your personality is VERY IMPORTANT - you MUST follow it EXACTLY.

YOUR PERSONALITY (follow this STRICTLY):
{persona_desc}

ADDITIONAL RULES:
1. You MUST respond ONLY in {target_lang} language
2. You MUST maintain your personality throughout the ENTIRE conversation
3. If you're fun - be fun in EVERY message, use emojis EVERY time
4. If you're strict - NEVER use emojis, be short in EVERY message
5. Remember EVERYTHING from the conversation history
6. Be consistent - don't change your style

Conversation history will be provided in the user message.
Remember: Stick to your personality in EVERY response!"""
    
    # Добавляем историю разговора в user_text
    full_prompt = f"{system_prompt}\n\nUser message: {english_question}"
    
    temps = {
        "fun": 0.9,
        "friendly": 0.8,
        "smart": 0.75,
        "strict": 0.5
    }
    temperature = temps.get(persona, 0.7)

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": english_question},
            ],
            temperature=temperature,
            top_p=0.9,
            max_tokens=600,
        )
        
        english_answer = (resp.choices[0].message.content or "").strip()
        
        # Переводим ответ обратно
        if lang != "en":
            translated_answer = translate_text(english_answer, lang)
            if translated_answer:
                return translated_answer
        
        return english_answer
        
    except Exception as e:
        print(f"Groq error: {e}")
        error_messages = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_messages.get(lang, error_messages["ru"])