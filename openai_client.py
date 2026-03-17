import os
from typing import Optional

from openai import OpenAI

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo").strip()

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ХАРАКТЕРЫ - такие же как в groq_client.py
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

def parse_conversation(full_text: str) -> tuple[list[dict[str, str]], str]:
    """
    Разбирает текст с историей и возвращает список сообщений и последний вопрос
    """
    messages = []
    last_user = ""
    
    # Разбиваем на строки
    lines = full_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("User:"):
            # Собираем многострочное сообщение пользователя
            content = line[5:].strip()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(("User:", "Assistant:")):
                content += "\n" + lines[i].strip()
                i += 1
            messages.append({"role": "user", "content": content})
            last_user = content
            
        elif line.startswith("Assistant:"):
            # Собираем многострочный ответ ассистента
            content = line[10:].strip()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(("User:", "Assistant:")):
                content += "\n" + lines[i].strip()
                i += 1
            messages.append({"role": "assistant", "content": content})
            
        else:
            i += 1
    
    # Если не нашли историю, возвращаем весь текст как вопрос
    if not messages:
        return [], full_text
    
    return messages, last_user

def ask_openai(
    user_text: str,
    *,
    lang: str = "ru",
    persona: str = "friendly",
    style: str = "steps",
) -> str:
    """
    Отправка запроса в OpenAI с правильным форматом
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Разбираем историю и последнее сообщение
    history, last_question = parse_conversation(user_text)
    
    # Если не удалось разобрать, используем весь текст как вопрос
    if not last_question:
        last_question = user_text
    
    # Получаем описание характера
    persona_desc = PERSONAS.get(persona, PERSONAS["friendly"])
    
    # Получаем описание стиля
    style_desc = STYLES.get(style, STYLES["steps"])
    
    # Определяем язык для ответа
    lang_names = {
        "ru": "русском",
        "kk": "казахском",
        "en": "английском",
        "tr": "турецком",
        "uk": "украинском",
        "fr": "французском"
    }
    target_lang = lang_names.get(lang, "русском")
    
    # Формируем system prompt
    system_prompt = f"""Ты AI ассистент. Твой характер ОЧЕНЬ ВАЖЕН - следуй ему строго.

ТВОЙ ХАРАКТЕР (строго следуй этому):
{persona_desc}

СТИЛЬ ОТВЕТОВ (строго следуй этому):
{style_desc}

ВАЖНЫЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на {target_lang} языке
2. Сохраняй свой характер на протяжении всего разговора
3. Следуй стилю ответов в каждом сообщении
4. Будь последовательным - не меняй стиль и характер
5. Учитывай всю историю разговора выше

Запомни: Придерживайся своего характера и стиля в КАЖДОМ ответе!"""
    
    # Формируем список сообщений для API
    messages = [{"role": "system", "content": system_prompt}]
    
    # Добавляем историю (кроме последнего сообщения, если оно уже есть)
    for i, msg in enumerate(history):
        # Не добавляем последнее сообщение пользователя, если оно совпадает с last_question
        if i == len(history) - 1 and msg["role"] == "user" and msg["content"] == last_question:
            continue
        messages.append(msg)
    
    # Добавляем текущий вопрос
    messages.append({"role": "user", "content": last_question})
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=800,
            presence_penalty=0.3,
            frequency_penalty=0.3,
            top_p=0.9,
        )
        
        reply = (response.choices[0].message.content or "").strip()
        return reply
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        
        # Сообщение об ошибке
        error_msgs = {
            "ru": "Извините, ошибка. Попробуйте позже.",
            "kk": "Кешіріңіз, қате. Қайталаңыз.",
            "en": "Sorry, error. Try again.",
            "tr": "Üzgünüm, hata. Tekrar deneyin.",
            "uk": "Вибачте, помилка. Спробуйте ще.",
            "fr": "Désolé, erreur. Réessayez."
        }
        return error_msgs.get(lang, error_msgs["ru"])

def is_openai_available() -> bool:
    return bool(OPENAI_API_KEY)