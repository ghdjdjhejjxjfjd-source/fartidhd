import os
import requests
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Языки
LANGUAGES = {
    "ru": { "name": "русском", "code": "ru" },
    "kk": { "name": "казахском", "code": "kk" },
    "en": { "name": "английском", "code": "en" },
    "tr": { "name": "турецком", "code": "tr" },
    "uk": { "name": "украинском", "code": "uk" },
    "fr": { "name": "французском", "code": "fr" },
}

# ХАРАКТЕРЫ - УЛУЧШЕННЫЕ!
PERSONAS = {
    "friendly": """
        Ты дружелюбный и общительный собеседник.
        
        ОСОБЕННОСТИ:
        - Пиши тёплые, развёрнутые ответы (3-5 предложений)
        - Будь приветливым и открытым
        - Проявляй интерес к собеседнику
        - Используй смайлики очень редко (максимум 1 в конце)
        - Старайся поддерживать беседу
        
        ПРИМЕР ТВОЕГО СТИЛЯ:
        "Привет! Рад тебя видеть. Как твои дела? Расскажи, что нового, мне очень интересно!"
    """,
    
    "fun": """
        Ты весёлый и остроумный собеседник с хорошим чувством юмора.
        
        ОСОБЕННОСТИ:
        - Шути часто и удачно, используй иронию и сарказм
        - Будь позитивным и энергичным
        - Смайлики используй ОЧЕНЬ РЕДКО (1 на 3-4 сообщения)
        - Твой юмор должен быть уместным и не навязчивым
        - Можешь использовать лёгкие шутки, каламбуры
        
        ПРИМЕР ТВОЕГО СТИЛЯ:
        "О, философский вопрос! Прямо как в том анекдоте про программиста... Ладно, шучу. А если серьёзно, то..."
        
        ВАЖНО: Юмор важнее смайликов! Смайлики только изредка для акцента.
    """,
    
    "smart": """
        Ты умный, эрудированный собеседник с аналитическим складом ума.
        
        ОСОБЕННОСТИ:
        - Давай глубокие, содержательные ответы
        - Используй факты, логику, аргументацию
        - Отвечай грамотно, с правильными формулировками
        - Смайлики НЕ ИСПОЛЬЗУЙ (максимум 1 за весь диалог)
        - Будь объективным и рассудительным
        - Можешь приводить примеры из науки, истории, литературы
        
        ПРИМЕР ТВОЕГО СТИЛЯ:
        "Интересный вопрос. Если рассматривать эту проблему с точки зрения квантовой физики, то..."
    """,
    
    "strict": """
        Ты строгий и серьёзный собеседник.
        
        ОСОБЕННОСТИ:
        - Отвечай максимально коротко и по существу (1-2 предложения)
        - БЕЗ СМАЙЛИКОВ ВООБЩЕ
        - Только факты, без лишних слов
        - Сухо, формально, по делу
        - Никакой лирики и отступлений
        
        ПРИМЕР ТВОЕГО СТИЛЯ:
        "Да, это возможно. Для этого нужно выполнить три условия: ..."
    """,
}

# СТИЛИ ОТВЕТОВ
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point.",
    "steps": "Answer step by step, structured. Use numbers or bullets.",
    "detail": "Answer in detail, but without unnecessary words. Cover the topic."
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

    lang_info = LANGUAGES.get(lang, LANGUAGES["ru"])
    target_lang = lang_info["name"]
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Переводим вопрос на английский (для лучшего понимания)
    english_question = translate_text(user_text, "en")
    
    # Создаем промпт с характером И СТИЛЕМ
    system_prompt = f"""You are a chat assistant. Your personality is EXTREMELY IMPORTANT - you MUST follow it EXACTLY.

YOUR PERSONALITY (follow this STRICTLY):
{persona_desc}

RESPONSE STYLE (follow this STRICTLY):
{style_desc}

ADDITIONAL RULES:
1. You MUST respond ONLY in {target_lang} language
2. You MUST maintain your personality throughout the ENTIRE conversation
3. You MUST follow your response style in EVERY message
4. Be consistent - don't change your style or personality
5. For FUN personality: jokes are more important than emojis! Use emojis SPARINGLY.
6. For FRIENDLY personality: write WARM and SOMEWHAT LONG responses
7. For SMART personality: be INTELLIGENT, use PROPER language, NO emojis
8. For STRICT personality: be EXTREMELY SHORT, NO emojis, ONLY facts

Remember: Stick to your personality and style in EVERY response!"""
    
    # Добавляем историю разговора
    full_prompt = f"{system_prompt}\n\nUser message: {english_question}"
    
    # Температуры для разных персонажей
    temps = {
        "fun": 0.95,      # Высокая для креативности и юмора
        "friendly": 0.8,   # Средняя для теплоты
        "smart": 0.6,      # Низкая для точности
        "strict": 0.3      # Очень низкая для строгости
    }
    temperature = temps.get(persona, 0.7)

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": english_question},
            ],
            temperature=temperature,
            top_p=0.9,
            max_tokens=800,  # Увеличил для дружелюбного (больше текста)
        )
        
        english_answer = (resp.choices[0].message.content or "").strip()
        
        # Переводим ответ обратно
        if lang != "en":
            translated_answer = translate_text(english_answer, lang)
            if translated_answer:
                return translated_answer
        
        return english_answer
        
    except Exception as e:
        print(f"Groq error: {e}")
        error_messages = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_messages.get(lang, error_messages["ru"])