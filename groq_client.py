import os
from typing import Optional

from groq import Groq

# ---------- ENV ----------
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ---------- Language / Style / Persona ----------
LANG_NAMES = {
    "ru": "Russian",
    "kk": "Kazakh",
    "en": "English",
    "tr": "Turkish",
    "uz": "Uzbek",
    "ky": "Kyrgyz",
    "uk": "Ukrainian",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
}


def normalize_lang(code: Optional[str]) -> str:
    code = (code or "").strip().lower()
    return code if code in LANG_NAMES else "ru"


def build_system_prompt(lang: str, style: str, persona: str) -> str:
    lang_code = normalize_lang(lang)
    lang_name = LANG_NAMES.get(lang_code, "Russian")
    
    # Новый, более естественный промпт
    base_prompt = f"""Ты - дружелюбный собеседник в мессенджере. Общайся естественно, как живой человек.

Правила общения:
1. Отвечай на {lang_name} языке
2. Пиши коротко и по делу, как в обычном чате
3. Не начинай каждое сообщение с приветствия
4. Используй эмодзи умеренно, чтобы оживить диалог
5. Если что-то непонятно - задай один уточняющий вопрос
6. Не пиши "как ИИ" или "как ассистент"
7. Будь дружелюбным, но не навязчивым
8. Отвечай сразу на вопрос, без лишних предисловий

Примеры хороших ответов:
- Привет! Как дела?
- Интересный вопрос. Я думаю, что...
- Понял тебя. Вот что могу предложить...
- Хорошо, давай разберемся...

Примеры плохих ответов:
- Как искусственный интеллект, я...
- Здравствуйте! Чем могу помочь?
- Согласно моим данным...
- Я здесь, чтобы помочь вам...

Запомни: ты просто друг в чате, который всегда рядом и готов поболтать."""
    
    return base_prompt


# ---------- MAIN AI FUNCTION ----------
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

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=0.9,  # Чуть выше для более живых ответов
            top_p=0.95,
            max_tokens=800,
        )
    except TypeError:
        # fallback for older SDK
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=0.9,
            top_p=0.95,
            max_tokens=800,
        )

    return (resp.choices[0].message.content or "").strip()