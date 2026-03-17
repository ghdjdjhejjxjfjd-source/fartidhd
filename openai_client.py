import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ХАРАКТЕРЫ (как в groq_client.py)
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

# Стили ответов
STYLES = {
    "short": "Keep answers VERY short (1-2 sentences). Just the point. No explanations.",
    "steps": "Answer step by step, structured. Use numbers or bullets. Be clear and organized.",
    "detail": "Answer in detail, but without unnecessary words. Cover the topic well."
}

def extract_conversation(full_text: str) -> tuple[str, str]:
    """
    Извлекает историю разговора и последнее сообщение
    Возвращает (conversation_history, last_message)
    """
    if "Conversation:" in full_text:
        parts = full_text.split("User:", 1)
        if len(parts) > 1:
            # Вся история до последнего User:
            history = parts[0].replace("Conversation:", "").strip()
            last_part = parts[1].strip()
            
            # Обрезаем Assistant: если есть
            if "Assistant:" in last_part:
                last_msg = last_part.split("Assistant:")[0].strip()
            else:
                last_msg = last_part
                
            return history, last_msg
    
    # Если нет истории - возвращаем пустую историю и весь текст
    return "", full_text

def detect_conversation_language(history: str, last_msg: str) -> str:
    """
    Определяет язык по всей истории разговора
    """
    # Объединяем историю и последнее сообщение
    full_text = (history + " " + last_msg).lower()
    
    # Счетчики для каждого языка
    counts = {
        "ru": 0, "kk": 0, "en": 0, "tr": 0, "uk": 0, "fr": 0
    }
    
    # Русские буквы
    for c in full_text:
        if 'а' <= c <= 'я':
            counts["ru"] += 1
        elif c in 'әіңғүұқөһ':
            counts["kk"] += 1
        elif c in 'çğıöşü':
            counts["tr"] += 1
        elif c in 'їєіґ':
            counts["uk"] += 1
        elif c in 'éèêëàâçîïôûù':
            counts["fr"] += 1
    
    # Если есть английские слова (латиница не из других языков)
    eng_words = sum(1 for word in full_text.split() if word.isascii() and not any(c in word for c in 'çğıöşüéèêëàâîïôûù'))
    counts["en"] = eng_words
    
    # Выбираем язык с максимальным счетчиком
    detected = max(counts, key=counts.get)
    
    # Если ничего не нашли - английский
    if sum(counts.values()) == 0:
        return "en"
    
    return detected

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",  # Не используется, оставлен для совместимости
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI с полной историей
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Извлекаем историю и последнее сообщение
    history, last_message = extract_conversation(user_text)
    
    # Определяем язык по всей истории
    detected_lang = detect_conversation_language(history, last_message)
    
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
    
    # Формируем полный контекст разговора
    conversation_context = ""
    if history:
        conversation_context = f"Previous conversation:\n{history}\n\n"
    
    # Создаем system prompt
    system_prompt = f"""You are a helpful AI assistant.

YOUR PERSONALITY (follow this STRICTLY):
{persona_desc}

RESPONSE STYLE (follow this STRICTLY):
{style_desc}

CRITICAL LANGUAGE RULES:
1. The entire conversation is in {target_lang}
2. You MUST respond in EXACTLY the SAME language: {target_lang}
3. Do NOT switch to another language under any circumstances
4. If you're unsure about a word, use simple words in {target_lang}
5. Never explain or mention the language you're using

Remember: 
- Stay in character throughout the ENTIRE conversation
- Follow your response style in EVERY message
- Be consistent - don't change your personality"""
    
    # Формируем полный запрос с историей
    full_prompt = f"{conversation_context}User: {last_message}\n\nAssistant:"
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.8,  # Увеличил для более естественных ответов
            max_tokens=800,
            presence_penalty=0.3,
            frequency_penalty=0.3,
            top_p=0.9,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        
        # Если ответ слишком короткий - пробуем еще раз (но не меняем температуру)
        if len(reply) < 10 and "?" in last_message:
            # Это вопрос, а ответ слишком короткий - пробуем еще раз
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt + "\n\nPlease provide a more detailed answer."}
                ],
                temperature=0.8,
                max_tokens=800,
            )
            reply = (response.choices[0].message.content or "").strip()
        
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        # Сообщение об ошибке на определенном языке
        error_msgs = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_msgs.get(detected_lang, error_msgs["en"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)