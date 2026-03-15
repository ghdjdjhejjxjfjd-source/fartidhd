# tavily_client.py
import os
from tavily import TavilyClient

# Получаем API ключ из переменных окружения
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

print(f"🔑 TAVILY_API_KEY loaded: {'YES' if TAVILY_API_KEY else 'NO'}")

# Инициализируем клиент
if TAVILY_API_KEY:
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    print("✅ Tavily client initialized")
else:
    tavily = None
    print("❌ Tavily client NOT initialized - missing API key")

def search_web(query, max_results=5):
    """
    Поиск в интернете через Tavily
    
    Args:
        query: поисковый запрос
        max_results: максимальное количество результатов
    
    Returns:
        Словарь с результатами поиска или None
    """
    if not tavily:
        print("❌ Tavily client not available")
        return None
    
    try:
        print(f"🌐 Searching Tavily for: {query[:50]}...")
        # Выполняем поиск
        response = tavily.search(
            query=query,
            search_depth="basic",  # basic или advanced
            max_results=max_results,
            include_answer=True,    # Включить готовый ответ
            include_raw_content=False
        )
        
        print(f"✅ Tavily search completed")
        return response
        
    except Exception as e:
        print(f"❌ Tavily search error: {e}")
        return None

def get_search_summary(query, max_results=3):
    """
    Получить краткую сводку результатов поиска
    
    Args:
        query: поисковый запрос
        max_results: количество результатов
    
    Returns:
        Текстовая сводка для отправки в ИИ
    """
    results = search_web(query, max_results)
    
    if not results:
        return None
    
    summary = f"📱 РЕЗУЛЬТАТЫ ПОИСКА В ИНТЕРНЕТЕ:\n\n"
    
    # Добавляем готовый ответ если есть
    if results.get('answer'):
        summary += f"📌 Краткий ответ: {results['answer']}\n\n"
    
    # Добавляем результаты
    if results.get('results'):
        summary += f"📊 Найдено {len(results['results'])} результатов:\n\n"
        for i, result in enumerate(results['results'], 1):
            title = result.get('title', 'Без заголовка')
            content = result.get('content', '')
            url = result.get('url', '')
            
            summary += f"{i}. {title}\n"
            summary += f"   {content[:200]}...\n"
            summary += f"   Источник: {url}\n\n"
    else:
        summary += "❌ Результаты не найдены\n"
    
    return summary

def is_tavily_available():
    """Проверка доступности Tavily"""
    return tavily is not None