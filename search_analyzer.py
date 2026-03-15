# search_analyzer.py
import os
import json
from groq import Groq
from openai import OpenAI

# Инициализация клиентов
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

# Промпт для анализа необходимости поиска
SEARCH_ANALYSIS_PROMPT = """
Ты - анализатор запросов. Твоя задача - определить, нужен ли поиск в интернете для ответа на вопрос пользователя.

Правила:
- Если вопрос требует СВЕЖИХ или АКТУАЛЬНЫХ данных → ответь "search"
- Если вопрос можно ответить из общих знаний → ответь "no_search"

Примеры когда НУЖЕН поиск (search):
- Вопросы про погоду, курс валют, цены
- Новости, события, что случилось сегодня/вчера
- Спортивные результаты, матчи, счета
- Расписание, время работы, билеты
- Актуальные данные, статистика

Примеры когда НЕ НУЖЕН поиск (no_search):
- Общие вопросы (что такое, кто такой, как работает)
- Творчество (напиши стих, придумай историю)
- Математика, логика, решение задач
- Советы, рекомендации, мнения
- Исторические факты (не меняются)

Отвечай ТОЛЬКО одним словом: "search" или "no_search"
"""

def analyze_with_groq(question):
    """Анализ вопроса через Groq"""
    if not groq_client:
        return None
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SEARCH_ANALYSIS_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0.1,  # Низкая температура для точности
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        return result if result in ["search", "no_search"] else None
        
    except Exception as e:
        print(f"❌ Groq analysis error: {e}")
        return None

def analyze_with_openai(question):
    """Анализ вопроса через OpenAI"""
    if not openai_client:
        return None
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SEARCH_ANALYSIS_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        return result if result in ["search", "no_search"] else None
        
    except Exception as e:
        print(f"❌ OpenAI analysis error: {e}")
        return None

def need_search(question, preferred_ai="fast"):
    """
    Главная функция - определяет нужен ли поиск
    
    Args:
        question: вопрос пользователя
        preferred_ai: "fast" (Groq) или "quality" (OpenAI)
    
    Returns:
        True - если нужен поиск
        False - если не нужен
        None - если не удалось определить
    """
    
    # Сначала пробуем через предпочтительный ИИ
    if preferred_ai == "fast":
        result = analyze_with_groq(question)
        if result:
            return result == "search"
    else:
        result = analyze_with_openai(question)
        if result:
            return result == "search"
    
    # Если не получилось, пробуем через другой ИИ
    if preferred_ai == "fast":
        result = analyze_with_openai(question)
    else:
        result = analyze_with_groq(question)
    
    if result:
        return result == "search"
    
    # Если оба не сработали - возвращаем None
    return None

# Простой запасной вариант на ключевых словах
def need_search_fallback(question):
    """Запасной вариант на ключевых словах"""
    question_lower = question.lower()
    
    search_keywords = [
        # Новости
        'новости', 'новость', 'события', 'произошло', 'случилось',
        # Время
        'сегодня', 'сейчас', 'вчера', 'завтра', 'этой неделе',
        # Цены
        'курс', 'цена', 'сколько стоит', 'стоимость',
        # Погода
        'погода', 'температура', 'прогноз',
        # Спорт
        'матч', 'счет', 'выиграл', 'проиграл', 'турнир',
        # Поисковые слова
        'найди', 'поищи', 'гугл', 'интернет'
    ]
    
    for word in search_keywords:
        if word in question_lower:
            return True
    
    return False