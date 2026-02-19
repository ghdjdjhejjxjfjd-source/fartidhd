import os
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

LANG_NAMES = {
    "ru": "РУССКОМ",
    "kk": "КАЗАХСКОМ",
    "en": "АНГЛИЙСКОМ",
    "tr": "ТУРЕЦКОМ",
    "uz": "УЗБЕКСКОМ",
    "ky": "КЫРГЫЗСКОМ",
    "uk": "УКРАИНСКОМ",
    "de": "НЕМЕЦКОМ",
    "es": "ИСПАНСКОМ",
    "fr": "ФРАНЦУЗСКОМ",
}

PERSONAS = {
    "friendly": "дружелюбный, теплый, используй смайлики 🙂",
    "fun": "веселый, шутливый, используй 😄 😂",
    "strict": "серьезный, без смайликов, коротко",
    "smart": "умный, вдумчивый, используй 🧐 🤔",
}

def ask_groq(
    user_text: str,
    *,
    lang: str = "ru",
    style: str = "steps",
    persona: str = "friendly",
) -> str:
    if not groq_client:
        raise RuntimeError("GROQ_API_KEY is not set")

    lang_name = LANG_NAMES.get(lang, "РУССКОМ")
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    # Очень строгий промпт с акцентом на язык
    system_prompt = f"""ТЫ ДОЛЖЕН ОТВЕЧАТЬ ТОЛЬКО НА {lang_name} ЯЗЫКЕ. ЭТО ОБЯЗАТЕЛЬНО!

Твой характер: {persona_desc}

ПРАВИЛА:
1. Отвечай ТОЛЬКО на {lang_name} языке
2. Ни слова на других языках
3. Отвечай как обычный человек
4. Не упоминай что ты ИИ

Пример:
User: Привет
Assistant: Привет! Как дела?"""

    temps = {"fun": 0.85, "friendly": 0.75, "smart": 0.7, "strict": 0.5}
    temperature = temps.get(persona, 0.7)

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=temperature,
            top_p=0.9,
            max_tokens=600,
        )
    except TypeError:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=temperature,
            top_p=0.9,
            max_tokens=600,
        )

    return (resp.choices[0].message.content or "").strip()