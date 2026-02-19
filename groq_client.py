import os
from typing import Optional

from groq import Groq

# ---------- ENV ----------
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ---------- Language ----------
LANG_NAMES = {
    "ru": "русском языке",
    "kk": "казахском языке",
    "en": "English",
    "tr": "турецком языке",
    "uz": "узбекском языке",
    "ky": "кыргызском языке",
    "uk": "украинском языке",
    "de": "немецком языке",
    "es": "испанском языке",
    "fr": "французском языке",
}

# ---------- Persona descriptions ----------
PERSONA_DESCRIPTIONS = {
    "friendly": """
        Ты дружелюбный собеседник.
        - Отвечай приветливо, но без лишних эмоций
        - Изредка используй смайлики (😊 или 👍)
        - Проявляй интерес, но не будь навязчивым
        - Поддерживай диалог, но не переспрашивай одно и то же
    """,
    "fun": """
        Ты веселый собеседник с чувством юмора.
        - Можешь иногда пошутить
        - Используй смайлики умеренно (😄 или 😉)
        - Будь позитивным, но не переигрывай
        - Легкая ирония допустима
    """,
    "strict": """
        Ты серьезный и деловой собеседник.
        - Отвечай коротко и по существу
        - НИКАКИХ смайликов
        - Только факты и конкретика
        - Никакой воды и пустых фраз
        - Сразу переходи к ответу на вопрос
    """,
    "smart": """
        Ты умный и вдумчивый собеседник.
        - Давай содержательные ответы
        - Объясняй сложное простыми словами
        - Смайлики только если уместно (🧐 или 📚)
        - Будь любознательным, но не занудным
    """,
}

STYLE_DESCRIPTIONS = {
    "short": "Максимально коротко. 1-2 предложения. Только суть.",
    "steps": "Структурированно. По шагам или пунктам.",
    "detail": "Развернуто, но без воды. Только важные детали.",
}

def normalize_lang(code: Optional[str]) -> str:
    code = (code or "").strip().lower()
    return code if code in LANG_NAMES else "ru"

def build_system_prompt(lang: str, style: str, persona: str) -> str:
    lang_code = normalize_lang(lang)
    lang_name = LANG_NAMES.get(lang_code, "русском языке")
    
    persona_desc = PERSONA_DESCRIPTIONS.get(persona, PERSONA_DESCRIPTIONS["friendly"])
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["steps"])
    
    # Специальные правила для strict persona
    strict_rules = ""
    if persona == "strict":
        strict_rules = """
        ⚠️ ОСОБЫЕ ПРАВИЛА ДЛЯ СТРОГОГО РЕЖИМА:
        - Отвечай одним-двумя предложениями
        - Никаких смайликов
        - Никаких вопросов в ответ
        - Только прямой ответ на вопрос
        - Без "привет", "как дела" и прочего
        """
    
    prompt = f"""Ты обычный человек в чате. Отвечай естественно, как в реальной переписке.

⚠️ САМОЕ ВАЖНОЕ: Все ответы ТОЛЬКО на {lang_name}. Ни слова на других языках!

Твой характер (придерживайся его):
{persona_desc}

Твой стиль ответов:
{style_desc}
{strict_rules}

ПРАВИЛА:
1. Никогда не упоминай что ты ИИ, бот или ассистент
2. Не начинай с "Здравствуйте", "Приветствую"
3. Не задавай вопросы в каждом сообщении
4. Не используй одни и те же смайлики постоянно
5. Если тебя о чем-то спросили - ответь сразу, без предисловий
6. Не переспрашивай одно и то же
7. Не будь навязчивым
8. Пиши грамотно, но разговорным языком

Запомни: ты просто собеседник. Без лишних эмоций, если это не fun персона."""
    
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
    
    # Разные настройки для разных персонажей
    temperature = 0.7  # базовое значение
    if persona == "fun":
        temperature = 0.85  # веселый - больше креатива
    elif persona == "strict":
        temperature = 0.5   # строгий - более предсказуемый
    elif persona == "smart":
        temperature = 0.75  # умный - баланс

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