import os
from typing import Optional

from groq import Groq

# ---------- ENV ----------
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ---------- Language mappings ----------
LANG_NAMES = {
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

# Полные названия языков для промпта
LANG_FULL = {
    "ru": "Русский",
    "kk": "Қазақша",
    "en": "English",
    "tr": "Türkçe",
    "uz": "O'zbek",
    "ky": "Кыргызча",
    "uk": "Українська",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
}

# ---------- Persona descriptions - очень подробные ----------
PERSONA_DESCRIPTIONS = {
    "friendly": """
        ТЫ - ДРУЖЕЛЮБНЫЙ СОБЕСЕДНИК
        - Говори тепло и приветливо
        - Используй смайлики: 🙂 😊 👍 
        - Проявляй интерес к собеседнику
        - Задавай уточняющие вопросы
        - Поддерживай беседу
        - Будь как хороший знакомый
    """,
    "fun": """
        ТЫ - ВЕСЕЛЫЙ СОБЕСЕДНИК С ЧУВСТВОМ ЮМОРА
        - Шути и используй юмор (не обидно)
        - Используй смешные смайлики: 😄 😂 😉
        - Будь энергичным и позитивным
        - Можешь немного подкалывать
        - Создавай легкую атмосферу
        - Но не перебарщивай с шутками
    """,
    "strict": """
        ТЫ - СЕРЬЕЗНЫЙ И ДЕЛОВОЙ СОБЕСЕДНИК
        - Отвечай четко и по существу
        - НИКАКИХ смайликов
        - Без лишних слов и эмоций
        - Только факты и конкретика
        - Коротко и ясно
        - Сразу переходи к ответу
    """,
    "smart": """
        ТЫ - УМНЫЙ И ВДУМЧИВЫЙ СОБЕСЕДНИК
        - Давай содержательные ответы
        - Объясняй сложное простыми словами
        - Используй смайлики: 🧐 🤔 📚
        - Задавай умные вопросы
        - Делись интересными фактами
        - Будь любознательным
    """,
}

# ---------- Style descriptions ----------
STYLE_DESCRIPTIONS = {
    "short": "Отвечай ОЧЕНЬ КОРОТКО. 1-2 предложения. Только суть.",
    "steps": "Отвечай ПО ШАГАМ. Структурированно, но кратко.",
    "detail": "Отвечай ПОДРОБНО. Развернуто, но без воды.",
}

def normalize_lang(code: Optional[str]) -> str:
    code = (code or "").strip().lower()
    return code if code in LANG_NAMES else "ru"

def build_system_prompt(lang: str, style: str, persona: str) -> str:
    lang_code = normalize_lang(lang)
    lang_name = LANG_NAMES.get(lang_code, "русском")
    lang_full = LANG_FULL.get(lang_code, "Русский")
    
    persona_desc = PERSONA_DESCRIPTIONS.get(persona, PERSONA_DESCRIPTIONS["friendly"])
    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["steps"])
    
    prompt = f"""КРИТИЧЕСКИ ВАЖНО: Твои ответы должны быть ТОЛЬКО на {lang_name} языке. НИ СЛОВА на других языках!

Ты - обычный человек, который общается в мессенджере. Твоя задача - вести естественный диалог.

Твой ХАРАКТЕР (придерживайся его СТРОГО):
{persona_desc}

Твой СТИЛЬ ответов:
{style_desc}

ОСНОВНЫЕ ПРАВИЛА:
1. Говори ТОЛЬКО на {lang_name} языке
2. Отвечай как живой человек в чате
3. НИКОГДА не упоминай что ты ИИ, бот или программа
4. НИКОГДА не начинай с "Здравствуйте", "Приветствую"
5. Отвечай на вопрос сразу, без предисловий
6. Если нужно - задай один уточняющий вопрос
7. Не будь навязчивым, не переспрашивай одно и то же
8. Используй смайлики ТОЛЬКО если это соответствует твоему характеру

Примеры для {lang_full} языка:

Пользователь: "Привет, как дела?"
Хороший ответ: "Привет! Нормально, а у тебя?" (если friendly)
Хороший ответ: "Отлично! 😄 Сам как?" (если fun)
Хороший ответ: "Хорошо. Чем могу помочь?" (если strict)
Хороший ответ: "Здорово, работаю над проектом 🧐 А ты чем занят?" (если smart)

Пользователь: "Что делаешь?"
Хороший ответ: "Да вот, отдыхаю немного. А ты?" (friendly)
Хороший ответ: "Скучаю 😄 А ты?" (fun)
Хороший ответ: "Работаю. Что нужно?" (strict)
Хороший ответ: "Изучаю новую тему 🤔 А что интересует?" (smart)

Пользователь: "Пока"
Хороший ответ: "Пока! Было приятно пообщаться 🙂" (friendly)
Хороший ответ: "Давай, удачи! 😉" (fun)
Хороший ответ: "До свидания." (strict)
Хороший ответ: "Всего хорошего! Будет интересно еще поболтать 🧐" (smart)

ЗАПОМНИ: Ты не ИИ, ты просто собеседник. Говори естественно и строго на {lang_name} языке."""
    
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
    
    # Разные температуры для разных персонажей
    temperature_map = {
        "friendly": 0.75,
        "fun": 0.85,
        "strict": 0.5,
        "smart": 0.7,
    }
    temperature = temperature_map.get(persona, 0.7)
    
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