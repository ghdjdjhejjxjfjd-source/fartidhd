import os
import requests
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

LANGUAGES = {
    "ru": "русском", "kk": "казахском", "en": "английском",
    "tr": "турецком", "uk": "украинском", "fr": "французском"
}

# ===== КОРОТКИЕ, ЧЁТКИЕ ХАРАКТЕРЫ =====
PERSONAS = {
    "friendly": "Ты дружелюбный собеседник. Отвечай тепло, задавай вопросы, проявляй интерес. Пиши развёрнуто (3-5 предложений). Не шути. Смайлики редко.",
    "fun": "Ты весёлый и остроумный. Шути, используй иронию. Будь позитивным. Смайлики изредка. Юмор важнее смайликов.",
    "smart": "Ты умный и эрудированный. Давай глубокие ответы с фактами и примерами. Используй логику. Смайлики почти не используй.",
    "strict": "Ты строгий и серьёзный. Отвечай коротко (1-2 предложения). Только факты, без эмоций. Никаких смайликов."
}

# ===== КОРОТКИЕ, ЧЁТКИЕ СТИЛИ =====
STYLES = {
    "short": "Отвечай максимум 2 предложениями. Только суть.",
    "steps": "Разбивай ответ на шаги с нумерацией (1., 2., 3.).",
    "detail": "Отвечай развёрнуто, но без воды. 3-5 предложений."
}

def translate_text(text: str, target_lang: str = "en") -> str:
    if not text or not text.strip():
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx", "sl": "auto", "tl": target_lang,
            "dt": "t", "q": text
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

    target_lang = LANGUAGES.get(lang, "русском")
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    style_desc = STYLES.get(style, STYLES["steps"])
    
    english_question = translate_text(user_text, "en")
    
    # ===== СТАБИЛЬНЫЙ SYSTEM PROMPT (без дублирования) =====
    system_prompt = f"""Ты ассистент. Строго следуй правилам:

1. Язык: отвечай ТОЛЬКО на {target_lang}.
2. Характер: {persona_desc}
3. Стиль: {style_desc}

Не меняй характер и стиль в диалоге."""
    
    temps = {"fun": 0.9, "friendly": 0.8, "smart": 0.7, "strict": 0.3}
    temperature = temps.get(persona, 0.8)

    try:
        print(f"🤖 Groq: persona={persona}, style={style}, lang={target_lang}")
        
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
        
        answer = (resp.choices[0].message.content or "").strip()
        
        # Защита от повторений (если ответ слишком короткий или повторяется)
        if len(answer) < 10:
            answer = "Извините, попробуйте переформулировать вопрос."
        
        # Перевод на язык пользователя
        if lang != "en":
            translated = translate_text(answer, lang)
            if translated and len(translated) > 5:
                return translated
        
        return answer
        
    except Exception as e:
        print(f"❌ Groq error: {e}")
        error_messages = {
            "ru": "Ошибка. Попробуйте позже.",
            "kk": "Қате. Қайталаңыз.",
            "en": "Error. Try again.",
            "tr": "Hata. Tekrar deneyin.",
            "uk": "Помилка. Спробуйте ще.",
            "fr": "Erreur. Réessayez."
        }
        return error_messages.get(lang, error_messages["ru"])