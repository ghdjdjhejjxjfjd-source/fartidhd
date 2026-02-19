import os
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Подробные названия языков с примерами
LANGUAGES = {
    "ru": {
        "name": "РУССКИЙ",
        "example_q": "Привет, как дела?",
        "example_a": "Привет! Нормально, а у тебя?"
    },
    "kk": {
        "name": "ҚАЗАҚША",
        "example_q": "Сәлем, қалың қалай?",
        "example_a": "Сәлем! Жақсы, өзің қалайсың?"
    },
    "en": {
        "name": "ENGLISH",
        "example_q": "Hi, how are you?",
        "example_a": "Hi! I'm good, how about you?"
    },
    "tr": {
        "name": "TÜRKÇE",
        "example_q": "Merhaba, nasılsın?",
        "example_a": "Merhaba! İyiyim, sen nasılsın?"
    },
    "uz": {
        "name": "O'ZBEKCHA",
        "example_q": "Salom, qalaysiz?",
        "example_a": "Salom! Yaxshiman, o'zingiz qalaysiz?"
    },
    "ky": {
        "name": "КЫРГЫЗЧА",
        "example_q": "Салам, кандайсың?",
        "example_a": "Салам! Жакшы, өзүң кандайсың?"
    },
    "uk": {
        "name": "УКРАЇНСЬКА",
        "example_q": "Привіт, як справи?",
        "example_a": "Привіт! Нормально, а в тебе?"
    },
    "de": {
        "name": "DEUTSCH",
        "example_q": "Hallo, wie geht's?",
        "example_a": "Hallo! Gut, und dir?"
    },
    "es": {
        "name": "ESPAÑOL",
        "example_q": "¡Hola! ¿Cómo estás?",
        "example_a": "¡Hola! Bien, ¿y tú?"
    },
    "fr": {
        "name": "FRANÇAIS",
        "example_q": "Salut, comment ça va?",
        "example_a": "Salut! Ça va bien, et toi?"
    }
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

    # Получаем информацию о языке
    lang_info = LANGUAGES.get(lang, LANGUAGES["ru"])
    lang_name = lang_info["name"]
    example_q = lang_info["example_q"]
    example_a = lang_info["example_a"]
    
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    # Очень строгий промпт с примерами для каждого языка
    system_prompt = f"""ТЫ ОБЯЗАН ОТВЕЧАТЬ ТОЛЬКО НА {lang_name} ЯЗЫКЕ. НИ СЛОВА НА ДРУГИХ ЯЗЫКАХ!

Твой характер: {persona_desc}

ПРИМЕР ДИАЛОГА НА {lang_name}:
User: {example_q}
Assistant: {example_a}

ТЕПЕРЬ ТВОЯ ОЧЕРЕДЬ:

ПРАВИЛА:
1. Отвечай ТОЛЬКО на {lang_name}
2. Используй слова и грамматику этого языка
3. Не переключайся на другие языки
4. Отвечай как обычный человек
5. Не упоминай что ты ИИ

Если пользователь пишет на другом языке - всё равно отвечай на {lang_name}."""

    # Разные температуры для разных персонажей
    temps = {
        "fun": 0.85,
        "friendly": 0.75,
        "smart": 0.7,
        "strict": 0.5
    }
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