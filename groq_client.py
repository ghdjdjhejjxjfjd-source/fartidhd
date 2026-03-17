import os
import requests
from typing import Optional

from groq import Groq

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ХАРАКТЕРЫ
PERSONAS = {
    "friendly": """
        Ты дружелюбный и общительный собеседник.
        
        ОСОБЕННОСТИ:
        - Пиши тёплые, РАЗВЁРНУТЫЕ ответы (3-5 предложений)
        - Будь приветливым и открытым
        - Проявляй интерес к собеседнику
        - НЕ ШУТИ, просто будь добрым
        - Смайлики: ОЧЕНЬ РЕДКО (максимум 1 в конце)
    """,
    
    "fun": """
        Ты весёлый и остроумный собеседник.
        
        ОСОБЕННОСТИ:
        - ШУТИ часто и удачно
        - Будь позитивным и энергичным
        - Используй иронию и сарказм (уместно)
        - Смайлики: ИЗРЕДКА (1 на 3-4 сообщения)
        - Юмор важнее смайликов!
    """,
    
    "smart": """
        Ты умный и эрудированный собеседник.
        
        ОСОБЕННОСТИ:
        - Давай ГЛУБОКИЕ, содержательные ответы
        - Используй факты, логику, аргументацию
        - Отвечай грамотно и МУДРО
        - Приводи примеры из науки, истории, литературы
        - Смайлики: ПОЧТИ НЕТ (макс 1 за диалог)
    """,
    
    "strict": """
        Ты строгий и серьёзный собеседник.
        
        ОСОБЕННОСТИ:
        - Отвечай КОРОТКО и по существу (1-2 предложения)
        - Только факты, без лишних слов
        - Никакой лирики и отступлений
        - Сухо, формально, по делу
        - Смайлики: НИКОГДА
    """,
}

# СТИЛИ ОТВЕТОВ
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point. No explanations.",
    "steps": "Answer step by step, structured. Use numbers or bullets. Be clear and organized.",
    "detail": "Answer in detail, but without unnecessary words. Cover the topic well."
}

def parse_conversation(full_text: str) -> tuple[list[dict[str, str]], str]:
    """
    Разбирает текст с историей и возвращает список сообщений и последний вопрос
    """
    messages = []
    last_user = ""
    
    lines = full_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("User:"):
            content = line[5:].strip()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(("User:", "Assistant:")):
                content += "\n" + lines[i].strip()
                i += 1
            messages.append({"role": "user", "content": content})
            last_user = content
            
        elif line.startswith("Assistant:"):
            content = line[10:].strip()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(("User:", "Assistant:")):
                content += "\n" + lines[i].strip()
                i += 1
            messages.append({"role": "assistant", "content": content})
            
        else:
            i += 1
    
    if not messages:
        return [], full_text
    
    return messages, last_user

def detect_language(text: str) -> str:
    """
    Определяет язык текста по количеству символов
    """
    if not text:
        return "en"
    
    text_lower = text.lower()
    
    # Счетчики для каждого языка
    scores = {
        "ru": 0,
        "kk": 0,
        "tr": 0,
        "uk": 0,
        "fr": 0,
        "en": 0
    }
    
    for c in text_lower:
        if 'а' <= c <= 'я':
            scores["ru"] += 1
        elif c in 'әіңғүұқөһ':
            scores["kk"] += 1
        elif c in 'çğıöşü':
            scores["tr"] += 1
        elif c in 'їєіґ':
            scores["uk"] += 1
        elif c in 'éèêëàâçîïôûù':
            scores["fr"] += 1
        elif 'a' <= c <= 'z':
            scores["en"] += 1
    
    # Если нет символов ни одного языка
    if all(v == 0 for v in scores.values()):
        return "en"
    
    # Возвращаем язык с максимальным количеством символов
    result = max(scores, key=scores.get)
    return result

def ask_groq(
    user_text: str,
    *,
    lang: str = "ru",
    style: str = "steps",
    persona: str = "friendly",
) -> str:
    """
    Отправка запроса в Groq
    - Отвечает на языке пользователя (автоопределение)
    - Без переводов
    - Учитывает всю историю
    """
    if not groq_client:
        raise RuntimeError("GROQ_API_KEY is not set")

    # Разбираем историю и последний вопрос
    history, last_question = parse_conversation(user_text)
    
    if not last_question:
        last_question = user_text
    
    # Определяем язык последнего вопроса
    detected_lang = detect_language(last_question)
    
    # Названия языков для промпта
    lang_names = {
        "ru": "Russian",
        "kk": "Kazakh",
        "en": "English",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "fr": "French"
    }
    target_lang = lang_names.get(detected_lang, "English")
    
    # Получаем описание характера
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    # Получаем описание стиля
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Создаем system prompt
    system_prompt = f"""You are a chat assistant. Your personality is VERY IMPORTANT - you MUST follow it EXACTLY.

YOUR PERSONALITY (follow this STRICTLY):
{persona_desc}

RESPONSE STYLE (follow this STRICTLY):
{style_desc}

CRITICAL LANGUAGE RULES:
1. The user is speaking in {target_lang}
2. You MUST respond in EXACTLY the SAME language: {target_lang}
3. Do NOT switch to another language
4. Never explain that you're responding in a certain language

ADDITIONAL RULES:
- Maintain your personality throughout the ENTIRE conversation
- Follow your response style in EVERY message
- Be consistent - don't change your style or personality
- Remember the entire conversation history

Remember: Stick to your personality and style in EVERY response!"""
    
    # Формируем список сообщений для API
    messages = [{"role": "system", "content": system_prompt}]
    
    # Добавляем историю
    for i, msg in enumerate(history):
        if i == len(history) - 1 and msg["role"] == "user" and msg["content"] == last_question:
            continue
        messages.append(msg)
    
    # Добавляем текущий вопрос (на оригинальном языке)
    messages.append({"role": "user", "content": last_question})
    
    # Температуры для разных персонажей
    temps = {
        "fun": 0.95,
        "friendly": 0.8,
        "smart": 0.6,
        "strict": 0.3
    }
    temperature = temps.get(persona, 0.7)

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            top_p=0.9,
            max_tokens=800,
        )
        
        reply = (resp.choices[0].message.content or "").strip()
        return reply
        
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
        return error_messages.get(detected_lang, error_messages["en"])