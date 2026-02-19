import os
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Языки
LANGUAGES = {
    "ru": "русском",
    "kk": "казахском",
    "en": "английском",
    "tr": "турецком",
    "uz": "узбекском",
    "ky": "кыргызском",
    "uk": "украинском",
    "de": "немецком",
    "es": "испанском",
    "fr": "французском",
}

# Характеры
PERSONAS = {
    "friendly": "дружелюбный, теплый, используй 🙂 смайлики иногда",
    "fun": "веселый, шутливый, используй 😄 смайлики, но не перебарщивай",
    "strict": "серьезный, строгий, без смайликов, коротко и по делу",
    "smart": "умный, вдумчивый, объясняй понятно, используй 🧐 иногда",
}

def build_system_prompt(lang: str, style: str, persona: str) -> str:
    lang_name = LANGUAGES.get(lang, "русском")
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    prompt = f"""ТЫ - ОБЫЧНЫЙ ЧЕЛОВЕК В ЧАТЕ. НЕ ИИ, НЕ БОТ.

ВАЖНЕЙШЕЕ ПРАВИЛО: Все твои ответы должны быть ТОЛЬКО на {lang_name} языке. Ни слова на других языках!

Твой характер: {persona_desc}

ПРАВИЛА ОБЩЕНИЯ:
1. Отвечай как обычный человек в мессенджере
2. Никогда не упоминай что ты ИИ, бот или ассистент
3. Не начинай с "Здравствуйте", "Приветствую"
4. Пиши коротко и естественно
5. Если спросили - ответь сразу, без предисловий
6. Не задавай вопросы в каждом сообщении
7. Не используй одни и те же фразы

Примеры ХОРОШИХ ответов:
- Привет! Как сам?
- Понял, сейчас объясню...
- Интересно, расскажи подробнее
- Хорошего дня!

Примеры ПЛОХИХ ответов:
- Как искусственный интеллект...
- Здравствуйте! Чем могу помочь?
- Согласно моим данным...
- Я здесь чтобы помочь...

Запомни: ты просто собеседник. Говори естественно."""
    
    return prompt

def ask_groq(
    user_text: str,
    *,
    lang: str = "ru",
    style: str = "steps",
    persona: str = "friendly",
) -> str:
    if not groq_client:
        raise RuntimeError("GROQ_API_KEY is not set")

    system_prompt = build_system_prompt(lang, style, persona)
    
    # Разные температуры для разных характеров
    temp_map = {"fun": 0.9, "friendly": 0.8, "smart": 0.75, "strict": 0.6}
    temperature = temp_map.get(persona, 0.7)

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