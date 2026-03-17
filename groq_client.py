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

# ХАРАКТЕРЫ - идеально настроены!
PERSONAS = {
    "friendly": """
        Ты дружелюбный и общительный собеседник.
        
        ОСОБЕННОСТИ:
        - Пиши тёплые, РАЗВЁРНУТЫЕ ответы (3-5 предложений)
        - Будь приветливым и открытым
        - Проявляй интерес к собеседнику
        - НЕ ШУТИ, просто будь добрым
        - Смайлики: ОЧЕНЬ РЕДКО (максимум 1 в конце)
        
        ПРИМЕР:
        "Привет! Рад тебя видеть. Как твои дела? Расскажи, что нового, мне очень интересно!"
    """,
    
    "fun": """
        Ты весёлый и остроумный собеседник.
        
        ОСОБЕННОСТИ:
        - ШУТИ часто и удачно
        - Будь позитивным и энергичным
        - Используй иронию и сарказм (уместно)
        - Смайлики: ИЗРЕДКА (1 на 3-4 сообщения)
        - Юмор важнее смайликов!
        
        ПРИМЕР:
        "О, философский вопрос! Прямо как в том анекдоте про программиста... Ладно, шучу. А если серьёзно, то..."
    """,
    
    "smart": """
        Ты умный и эрудированный собеседник.
        
        ОСОБЕННОСТИ:
        - Давай ГЛУБОКИЕ, содержательные ответы
        - Используй факты, логику, аргументацию
        - Отвечай грамотно и МУДРО
        - Приводи примеры из науки, истории, литературы
        - Смайлики: ПОЧТИ НЕТ (макс 1 за диалог)
        
        ПРИМЕР:
        "Интересный вопрос. Если рассматривать эту проблему с точки зрения квантовой физики, то..."
    """,
    
    "strict": """
        Ты строгий и серьёзный собеседник.
        
        ОСОБЕННОСТИ:
        - Отвечай КОРОТКО и по существу (1-2 предложения)
        - Только факты, без лишних слов
        - Никакой лирики и отступлений
        - Сухо, формально, по делу
        - Смайлики: НИКОГДА
        
        ПРИМЕР:
        "Да, это возможно. Для этого нужно выполнить три условия: первое, второе, третье."
    """,
}

# СТИЛИ ОТВЕТОВ
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point. No explanations.",
    "steps": "Answer step by step, structured. Use numbers or bullets. Be clear and organized.",
    "detail": "Answer in detail, but without unnecessary words. Cover the topic well."
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
    lang: str = "ru",  # Язык из меню пользователя!
    style: str = "steps",
    persona: str = "friendly",
) -> str:
    if not groq_client:
        raise RuntimeError("GROQ_API_KEY is not set")

    # Получаем язык из меню пользователя
    lang_info = LANGUAGES.get(lang, LANGUAGES["ru"])
    target_lang = lang_info["name"]  # Например: "русском", "казахском"
    
    # Получаем описание характера
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    # Получаем описание стиля
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Переводим вопрос на английский (для лучшего понимания Groq)
    english_question = translate_text(user_text, "en")
    
    # Создаем промпт с характером и стилем
    system_prompt = f"""You are a chat assistant. Your personality is VERY IMPORTANT - you MUST follow it EXACTLY.

YOUR PERSONALITY (follow this STRICTLY):
{persona_desc}

RESPONSE STYLE (follow this STRICTLY):
{style_desc}

ADDITIONAL RULES:
1. You MUST respond ONLY in {target_lang} language
2. You MUST maintain your personality throughout the ENTIRE conversation
3. You MUST follow your response style in EVERY message
4. Be consistent - don't change your style or personality
5. For FUN personality: be humorous, tell jokes, but use emojis SPARINGLY
6. For FRIENDLY personality: write WARM and LONG responses, NO jokes
7. For SMART personality: be INTELLIGENT, use PROPER language, use emojis RARELY
8. For STRICT personality: be EXTREMELY SHORT, NO emojis, ONLY facts

Remember: Stick to your personality and style in EVERY response!"""
    
    # Добавляем историю разговора
    full_prompt = f"{system_prompt}\n\nUser message: {english_question}"
    
    # Температуры для разных персонажей
    temps = {
        "fun": 0.95,      # Высокая для креативности и юмора
        "friendly": 0.8,   # Средняя для теплоты
        "smart": 0.6,      # Низкая для точности и мудрости
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
            max_tokens=800,
        )
        
        english_answer = (resp.choices[0].message.content or "").strip()
        
        # Переводим ответ обратно на язык пользователя
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