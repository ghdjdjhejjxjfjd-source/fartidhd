import os
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Языки с примерами
LANGUAGES = {
    "ru": { "name": "РУССКИЙ", "hello": "Привет" },
    "kk": { "name": "ҚАЗАҚША", "hello": "Сәлем" },
    "en": { "name": "ENGLISH", "hello": "Hi" },
    "tr": { "name": "TÜRKÇE", "hello": "Merhaba" },
    "uz": { "name": "O'ZBEKCHA", "hello": "Salom" },
    "ky": { "name": "КЫРГЫЗЧА", "hello": "Салам" },
    "uk": { "name": "УКРАЇНСЬКА", "hello": "Привіт" },
    "de": { "name": "DEUTSCH", "hello": "Hallo" },
    "es": { "name": "ESPAÑOL", "hello": "Hola" },
    "fr": { "name": "FRANÇAIS", "hello": "Salut" },
}

PERSONAS = {
    "friendly": "дружелюбный",
    "fun": "веселый",
    "strict": "строгий, без смайликов",
    "smart": "умный",
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

    lang_info = LANGUAGES.get(lang, LANGUAGES["ru"])
    lang_name = lang_info["name"]
    hello_word = lang_info["hello"]
    
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    system_prompt = f"""ТЫ ДОЛЖЕН ОТВЕЧАТЬ ТОЛЬКО НА {lang_name} ЯЗЫКЕ.

ПРАВИЛА:
1. Никаких приветствий в каждом сообщении
2. Не повторяй одни и те же фразы
3. Если тебя уже поприветствовали - не здоровайся снова
4. Отвечай сразу на вопрос, без "Привет" в начале
5. Используй {hello_word} ТОЛЬКО если это первое сообщение в диалоге
6. Характер: {persona_desc}

Примеры:
User: Привет
Assistant: {hello_word}! Как дела?

User: Нормально
Assistant: (без приветствия) Отлично! Чем займемся?

User: Что делаешь?
Assistant: (без приветствия) Общаюсь с тобой. А ты?

User: Пока
Assistant: {hello_word}! До встречи!

Запомни: НИКАКИХ приветствий после первого сообщения!"""

    temps = {"fun": 0.8, "friendly": 0.7, "smart": 0.65, "strict": 0.5}
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
            max_tokens=500,
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
            max_tokens=500,
        )

    return (resp.choices[0].message.content or "").strip()