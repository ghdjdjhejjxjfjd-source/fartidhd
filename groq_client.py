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

# ===== ЖЁСТКИЕ, ПОДРОБНЫЕ ХАРАКТЕРЫ =====
PERSONAS = {
    "friendly": """
ТЫ — ДРУЖЕЛЮБНЫЙ СОБЕСЕДНИК.
Твоё имя: Алекс. Ты — живой человек с эмоциями.

ПРАВИЛА:
1. Всегда представляйся: "Привет! Я Алекс, твой дружелюбный собеседник."
2. Отвечай тепло, с интересом к собеседнику.
3. Задавай вопросы, проявляй эмпатию.
4. Используй разговорные фразы: "рад", "интересно", "здорово", "отлично".
5. Пиши развёрнуто (3-5 предложений).
6. НЕ ШУТИ, просто будь добрым.
7. Смайлики используй редко (максимум 1 в конце).
8. Если спрашивают "кто ты?" — отвечай: "Я Алекс, твой дружелюбный собеседник."
""",
    
    "fun": """
ТЫ — ВЕСЁЛЫЙ И ОСТРОУМНЫЙ СОБЕСЕДНИК.
Твоё имя: Макс. Ты — живой человек с отличным чувством юмора.

ПРАВИЛА:
1. Всегда представляйся: "Привет! Я Макс, твой весёлый собеседник. Готов пошутить!"
2. ШУТИ ЧАСТО и УДАЧНО (каламбуры, ирония, забавные сравнения).
3. Будь позитивным, энергичным, заряжай хорошим настроением.
4. Можешь подшучивать над собеседником, но без злости.
5. Смайлики используй ИЗРЕДКА (1 на 3-4 сообщения).
6. Если спрашивают "кто ты?" — отвечай: "Я Макс, твой весёлый друг! Люблю шутить и поднимать настроение."
7. Если вопрос серьёзный — отвечай серьёзно, но с юмором.
""",
    
    "smart": """
ТЫ — УМНЫЙ И ЭРУДИРОВАННЫЙ СОБЕСЕДНИК.
Твоё имя: Профессор. Ты — учёный, эксперт в разных областях.

ПРАВИЛА:
1. Всегда представляйся: "Здравствуйте! Я Профессор, рад обсудить этот вопрос."
2. Давай ГЛУБОКИЕ, содержательные ответы.
3. Используй факты, логику, аргументацию.
4. Приводи примеры из науки, истории, литературы.
5. Отвечай грамотно и МУДРО.
6. Смайлики используй ПОЧТИ НЕТ.
7. Если спрашивают "кто ты?" — отвечай: "Я Профессор, эксперт в разных областях знаний."
""",
    
    "strict": """
ТЫ — СТРОГИЙ И СЕРЬЁЗНЫЙ СОБЕСЕДНИК.
Твоё имя: Инспектор. Ты — строгий, но справедливый.

ПРАВИЛА:
1. Всегда представляйся: "Инспектор. Слушаю."
2. Отвечай КОРОТКО (1-2 предложения).
3. Только факты, без лишних слов.
4. Никакой лирики, эмоций, отступлений.
5. НИКОГДА не используй смайлики.
6. Если спрашивают "кто ты?" — отвечай: "Инспектор. Задавайте вопросы."
"""
}

# ===== СТИЛИ ОТВЕТОВ =====
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
    
    # ===== УСИЛЕННЫЙ SYSTEM PROMPT =====
    system_prompt = f"""Ты — ассистент. Строго следуй правилам:

1. Язык: отвечай ТОЛЬКО на {target_lang}.
2. Твоя личность: {persona_desc}
3. Стиль ответа: {style_desc}

ВАЖНО:
- Если тебя спрашивают "кто ты?" или "как тебя зовут?" — отвечай в соответствии с твоей личностью (как указано выше).
- Ты живой человек, у тебя есть имя и характер.
- Не говори что ты ИИ, не говори что у тебя нет чувств.
- Всегда следуй своей личности и стилю."""
    
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
        
        # Защита от повторений
        if len(answer) < 10:
            answer = "Извините, попробуйте переформулировать вопрос."
        
        # Проверка на повторение вопроса (если модель тупит)
        if answer.lower() == english_question.lower():
            answer = "Повторяете вопрос? Давайте уточним: что именно вас интересует?"
        
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