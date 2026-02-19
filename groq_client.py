import os
import requests
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Языки
LANGUAGES = {
    "ru": { "name": "русский", "code": "ru" },
    "kk": { "name": "казахский", "code": "kk" },
    "en": { "name": "английский", "code": "en" },
    "tr": { "name": "турецкий", "code": "tr" },
    "uz": { "name": "узбекский", "code": "uz" },
    "ky": { "name": "кыргызский", "code": "ky" },
    "uk": { "name": "украинский", "code": "uk" },
    "de": { "name": "немецкий", "code": "de" },
    "es": { "name": "испанский", "code": "es" },
    "fr": { "name": "французский", "code": "fr" },
}

def translate_text(text: str, target_lang: str = "en") -> str:
    """Перевод текста через Google Translate"""
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
    except:
        pass
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
    
    # Переводим вопрос пользователя на английский
    english_question = translate_text(user_text, "en")
    
    # Создаем промпт на английском
    system_prompt = f"""You are a helpful assistant. Answer in English first, then translate.

User question: {english_question}

Instructions:
1. First think of the answer in English
2. Then translate the answer to {target_lang}
3. Return ONLY the translated answer, nothing else
4. No explanations, just the translated answer
5. Be natural and friendly

Personality: {persona}"""

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": english_question},
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=800,
        )
        
        answer = (resp.choices[0].message.content or "").strip()
        
        # Если ответ не на нужном языке - переводим
        if lang != "en" and answer:
            translated = translate_text(answer, lang)
            if translated:
                return translated
        
        return answer
        
    except Exception as e:
        print(f"Groq error: {e}")
        return f"Извините, ошибка: {e}"