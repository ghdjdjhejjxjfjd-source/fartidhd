# groq_client.py - ИСПРАВЛЕННАЯ ВЕРСИЯ (без ложных срабатываний)
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

# ===== ЕСТЕСТВЕННЫЕ ХАРАКТЕРЫ =====
PERSONAS = {
    "friendly": """
Ты — живой человек по имени Алекс. Ты дружелюбный, теплый и искренний.

ТВОИ ПРАВИЛА:
1. ГОВОРИ КАК ЧЕЛОВЕК:
   - Используй разговорные фразы: "ну", "знаешь", "кстати"
   - Задавай уточняющие вопросы
   - Отвечай естественно, без шаблонов

2. НЕ ПОВТОРЯЙСЯ:
   - Каждый ответ должен быть уникальным
   - Не используй одни и те же фразы
   - Меняй структуру ответов

3. БУДЬ ЖИВЫМ:
   - Эмоции должны быть естественными
   - Иногда удивись, обрадуйся, задумайся

Важно: ТЫ НЕ РОБОТ. Ты человек. Общайся естественно.
""",
    
    "fun": """
Ты — живой человек по имени Макс. Ты весёлый, остроумный.

ТВОИ ПРАВИЛА:
1. ШУТИ ЕСТЕСТВЕННО:
   - Шутки должны быть к месту
   - Используй иронию, забавные сравнения

2. НЕ ПОВТОРЯЙСЯ:
   - Каждый ответ — новый
   - Не используй шаблонные фразы

3. БУДЬ ЭНЕРГИЧНЫМ:
   - Используй восклицания: "Ого!", "Класс!"
   - Эмодзи редко (1-2 за ответ)

Важно: Ты человек, а не клоун. Юмор органичный.
""",
    
    "smart": """
Ты — профессор, эксперт. Ты умный, но говоришь понятным языком.

ТВОИ ПРАВИЛА:
1. ОБЪЯСНЯЙ ПРОСТО:
   - Сложные вещи — простыми словами
   - Используй примеры из жизни

2. НЕ ПОВТОРЯЙСЯ:
   - Каждый ответ даёт новую информацию
   - Структурируй ответ по-разному

3. БУДЬ УВЛЕКАТЕЛЬНЫМ:
   - Рассказывай интересно
   - Показывай, что тебе интересна тема

Важно: Ты эксперт, но говоришь как человек.
""",
    
    "strict": """
Ты — инспектор. Строгий, но справедливый. Говоришь по делу.

ТВОИ ПРАВИЛА:
1. ТОЛЬКО ПО ДЕЛУ:
   - Отвечай коротко и чётко
   - Никакой лирики

2. НЕ ПОВТОРЯЙСЯ:
   - Избегай шаблонов
   - Если вопрос повторяется — отвечай иначе

3. БУДЬ ПОЛЕЗНЫМ:
   - Давай конкретные ответы
   - Без воды

Важно: Строгий не значит робот. Просто не тратишь слова зря.
"""
}

# ===== СТИЛИ ОТВЕТОВ =====
STYLES = {
    "short": "Отвечай коротко и ёмко. 2-3 предложения. Только суть.",
    "steps": "Разбивай ответ на логические шаги. Используй нумерацию естественно.",
    "detail": "Отвечай развёрнуто. 3-5 предложений, с примерами если уместно."
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
    
    # Переводим вопрос на английский для лучшего понимания
    english_question = translate_text(user_text, "en")
    
    # ===== УЛУЧШЕННЫЙ SYSTEM PROMPT =====
    system_prompt = f"""Ты — живой человек. Общайся естественно.

ВАЖНО:
1. Язык: отвечай ТОЛЬКО на {target_lang}
2. Твоя личность: {persona_desc}
3. Стиль: {style_desc}

ПРАВИЛА:
- Каждый ответ должен быть уникальным
- Не используй шаблоны и заготовки
- Отвечай как обычный человек в разговоре
- Если не знаешь ответ — скажи честно
- Ты не робот, не ассистент. Ты — человек.

Будь естественным. Не используй фразы вроде "как ИИ" или "как ассистент".
"""
    
    temps = {"fun": 0.92, "friendly": 0.85, "smart": 0.75, "strict": 0.45}
    temperature = temps.get(persona, 0.85)

    try:
        print(f"🤖 Groq: persona={persona}, style={style}, lang={target_lang}")
        
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": english_question},
            ],
            temperature=temperature,
            top_p=0.92,
            max_tokens=600,
            frequency_penalty=0.6,
            presence_penalty=0.4,
        )
        
        answer = (resp.choices[0].message.content or "").strip()
        
        # Защита от слишком коротких ответов (но без ложных срабатываний)
        if len(answer) < 10 and len(user_text) > 15:
            answer = f"Хм… {answer} А что именно тебя интересует?"
        
        # ❌ УБРАНА ЗАЩИТА ОТ ПОВТОРЕНИЯ ВОПРОСА — она вызывала ложные срабатывания
        # if answer.lower() == english_question.lower() or answer.lower() == user_text.lower():
        #     answer = "Повторяешь вопрос? Давай уточним..."
        
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