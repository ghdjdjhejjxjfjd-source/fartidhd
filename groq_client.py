import os
import requests
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Языки с их названиями
LANGUAGES = {
    "ru": { "name": "русский", "code": "ru", "flag": "🇷🇺" },
    "kk": { "name": "казахский", "code": "kk", "flag": "🇰🇿" },
    "en": { "name": "английский", "code": "en", "flag": "🇬🇧" },
    "tr": { "name": "турецкий", "code": "tr", "flag": "🇹🇷" },
    "uz": { "name": "узбекский", "code": "uz", "flag": "🇺🇿" },
    "ky": { "name": "кыргызский", "code": "ky", "flag": "🇰🇬" },
    "uk": { "name": "украинский", "code": "uk", "flag": "🇺🇦" },
    "de": { "name": "немецкий", "code": "de", "flag": "🇩🇪" },
    "es": { "name": "испанский", "code": "es", "flag": "🇪🇸" },
    "fr": { "name": "французский", "code": "fr", "flag": "🇫🇷" },
}

# Характеры
PERSONAS = {
    "friendly": "дружелюбный, теплый, используй смайлики 🙂",
    "fun": "веселый, шутливый, используй 😄 😂",
    "strict": "серьезный, без смайликов, коротко и по делу",
    "smart": "умный, вдумчивый, используй 🤔 🧐",
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
    
    # Переводим вопрос пользователя на английский (для лучшего понимания моделью)
    english_question = translate_text(user_text, "en")
    
    # Создаем промпт на английском (модель лучше понимает)
    system_prompt = f"""You are a helpful chat assistant. Respond naturally like a human.

Personality: {persona_desc}

IMPORTANT: You MUST respond in {target_lang} language only!

Rules:
1. Answer in {target_lang} language
2. Be natural and conversational
3. Don't start every message with greetings
4. Don't repeat yourself
5. Never mention you're an AI

User question: {english_question}

Remember: Your response must be in {target_lang}."""
    
    # Разные температуры для разных характеров
    temps = {
        "fun": 0.85,
        "friendly": 0.75,
        "smart": 0.7,
        "strict": 0.5
    }
    temperature = temps.get(persona, 0.7)

    try:
        # Получаем ответ от модели на английском
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
        
        # Переводим ответ обратно на нужный язык
        if lang != "en":
            translated_answer = translate_text(english_answer, lang)
            if translated_answer:
                return translated_answer
        
        return english_answer
        
    except Exception as e:
        print(f"Groq error: {e}")
        
        # Сообщения об ошибках на разных языках
        error_messages = {
            "ru": "Извините, произошла ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате пайда болды. Кейінірек қайталаңыз.",
            "en": "Sorry, an error occurred. Try again later.",
            "tr": "Üzgünüm, bir hata oluştu. Daha sonra tekrar deneyin.",
            "uz": "Kechirasiz, xatolik yuz berdi. Keyinroq qayta urinib ko'ring.",
            "ky": "Кечиресиз, ката кетти. Кийинчерээк кайталаңыз.",
            "uk": "Вибачте, сталася помилка. Спробуйте пізніше.",
            "de": "Entschuldigung, ein Fehler ist aufgetreten. Versuchen Sie es später noch einmal.",
            "es": "Lo siento, ocurrió un error. Inténtalo de nuevo más tarde.",
            "fr": "Désolé, une erreur s'est produite. Réessayez plus tard."
        }
        return error_messages.get(lang, error_messages["ru"])