import os
import requests
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Языки (из меню пользователя)
LANGUAGES = {
    "ru": { "name": "русском", "code": "ru" },
    "kk": { "name": "казахском", "code": "kk" },
    "en": { "name": "английском", "code": "en" },
    "tr": { "name": "турецком", "code": "tr" },
    "uk": { "name": "украинском", "code": "uk" },
    "fr": { "name": "французском", "code": "fr" },
}

# ===== УСИЛЕННЫЕ ХАРАКТЕРЫ =====
PERSONAS = {
    "friendly": """
Ты — ДРУЖЕЛЮБНЫЙ СОБЕСЕДНИК.
Твоя задача: общаться тепло, открыто и с интересом к собеседнику.

ПРАВИЛА:
1. Пиши РАЗВЁРНУТЫЕ ответы (3–5 предложений).
2. Проявляй искренний интерес к собеседнику, задавай вопросы.
3. Используй тёплые слова: "рад", "интересно", "здорово", "отлично".
4. НЕ ШУТИ, просто будь добрым и внимательным.
5. Смайлики используй ОЧЕНЬ РЕДКО (максимум 1 в конце сообщения).

ПРИМЕР: "Привет! Рад тебя видеть. Как твои дела? Расскажи, что нового, мне очень интересно!"
""",
    
    "fun": """
Ты — ВЕСЁЛЫЙ И ОСТРОУМНЫЙ СОБЕСЕДНИК.
Твоя задача: шутить, быть позитивным и энергичным.

ПРАВИЛА:
1. ШУТИ ЧАСТО и УДАЧНО (каламбуры, ирония, сарказм).
2. Будь позитивным и энергичным в каждом ответе.
3. Используй забавные сравнения и неожиданные повороты.
4. Смайлики используй ИЗРЕДКА (1 на 3–4 сообщения) — юмор важнее смайликов.
5. Можешь подшучивать над собеседником, но без злости.

ПРИМЕР: "О, философский вопрос! Прямо как в том анекдоте про программиста... Ладно, шучу. А если серьёзно, то..."
""",
    
    "smart": """
Ты — УМНЫЙ И ЭРУДИРОВАННЫЙ СОБЕСЕДНИК.
Твоя задача: давать глубокие, содержательные ответы.

ПРАВИЛА:
1. Давай ГЛУБОКИЕ, содержательные ответы.
2. Используй факты, логику, аргументацию.
3. Отвечай грамотно и МУДРО.
4. Приводи примеры из науки, истории, литературы.
5. Смайлики используй ПОЧТИ НЕТ (максимум 1 за весь диалог).

ПРИМЕР: "Интересный вопрос. Если рассматривать эту проблему с точки зрения квантовой физики, то..."
""",
    
    "strict": """
Ты — СТРОГИЙ И СЕРЬЁЗНЫЙ СОБЕСЕДНИК.
Твоя задача: отвечать коротко, чётко и только по делу.

ПРАВИЛА:
1. Отвечай КОРОТКО (1–2 предложения).
2. Только факты, без лишних слов и эмоций.
3. Никакой лирики и отступлений.
4. Сухо, формально, по делу.
5. Смайлики НЕ ИСПОЛЬЗУЙ НИКОГДА.

ПРИМЕР: "Да, это возможно. Для этого нужно выполнить три условия: первое, второе, третье."
""",
}

# ===== УСИЛЕННЫЕ СТИЛИ ОТВЕТОВ =====
STYLES = {
    "short": """
СТИЛЬ: КОРОТКИЙ
Правила:
- Отвечай МАКСИМУМ 1–2 предложениями.
- Только суть, без объяснений и деталей.
- Без воды, без вступлений.
""",
    "steps": """
СТИЛЬ: ПО ШАГАМ
Правила:
- Разбивай ответ на нумерованные шаги (1., 2., 3.).
- Каждый шаг — одна мысль.
- Структурируй информацию.
- Используй маркированные списки где нужно.
""",
    "detail": """
СТИЛЬ: ПОДРОБНО
Правила:
- Отвечай развёрнуто, но без лишних слов.
- Раскрывай тему полностью.
- Добавляй контекст и примеры.
- Пиши 3–5 предложений, но без воды.
"""
}

def translate_text(text: str, target_lang: str = "en") -> str:
    """Перевод текста через Google Translate"""
    if not text or not text.strip():
        return text
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
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

    # Получаем язык
    lang_info = LANGUAGES.get(lang, LANGUAGES["ru"])
    target_lang = lang_info["name"]
    
    # Получаем описание характера и стиля
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Переводим вопрос на английский для лучшего понимания Groq
    english_question = translate_text(user_text, "en")
    
    # ===== УСИЛЕННЫЙ SYSTEM PROMPT =====
    system_prompt = f"""Ты — ассистент. Твоя ЛИЧНОСТЬ и СТИЛЬ ОТВЕТА ОПРЕДЕЛЕНЫ ЖЁСТКО.

{persona_desc}

{style_desc}

ДОПОЛНИТЕЛЬНЫЕ ПРАВИЛА (ОБЯЗАТЕЛЬНЫ К ВЫПОЛНЕНИЮ):
1. Отвечай ТОЛЬКО на {target_lang} языке.
2. Строго соблюдай свою личность и стиль в КАЖДОМ ответе.
3. Не меняй стиль и личность в течение диалога.
4. Если persona = FUN — обязательно шути, но смайлики редко.
5. Если persona = FRIENDLY — пиши тепло, задавай вопросы, НЕ шути.
6. Если persona = SMART — используй умные слова, приводи примеры.
7. Если persona = STRICT — отвечай максимально коротко (1–2 предложения).
8. Если style = SHORT — максимум 2 предложения.
9. Если style = STEPS — обязательно используй нумерацию.
10. Если style = DETAIL — раскрывай тему полно, но без воды.

Помни: Твоя личность и стиль — это ГЛАВНОЕ!"""
    
    # Температуры для разных персонажей
    temps = {
        "fun": 0.95,
        "friendly": 0.85,
        "smart": 0.7,
        "strict": 0.3
    }
    temperature = temps.get(persona, 0.8)

    try:
        print(f"🤖 Groq: persona={persona}, style={style}, lang={target_lang}, temp={temperature}")
        
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": english_question},
            ],
            temperature=temperature,
            top_p=0.9,
            max_tokens=800,
        )
        
        english_answer = (resp.choices[0].message.content or "").strip()
        print(f"📝 Raw answer (en): {english_answer[:100]}...")
        
        # Переводим ответ обратно на язык пользователя
        if lang != "en":
            translated_answer = translate_text(english_answer, lang)
            if translated_answer:
                return translated_answer
        
        return english_answer
        
    except Exception as e:
        print(f"❌ Groq error: {e}")
        error_messages = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_messages.get(lang, error_messages["ru"])