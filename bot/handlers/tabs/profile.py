from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from api import (
    get_access, get_user_persona, get_user_lang, 
    get_use_mini_app, get_ai_mode, get_ai_mode_changes
)
from payments import get_balance
from bot.menu import tab_kb, TAB_TEXT
from bot.utils import set_last_menu, send_fresh_menu


async def show_profile(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Показать профиль пользователя с реальными данными"""
    
    # Получаем свежие данные из БД
    a = get_access(user_id)
    balance = get_balance(user_id)
    persona = get_user_persona(user_id)
    lang = get_user_lang(user_id)
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    
    # Получаем username если есть
    username = "—"
    if query.from_user and query.from_user.username:
        username = f"@{query.from_user.username}"
    
    # Названия для характера
    persona_names = {
        "friendly": "😊 Общительный",
        "fun": "😂 Весёлый",
        "smart": "🧐 Умный",
        "strict": "😐 Строгий"
    }
    
    # Названия для языка
    lang_names = {
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
        "kk": "🇰🇿 Қазақша",
        "tr": "🇹🇷 Türkçe",
        "uk": "🇺🇦 Українська",
        "fr": "🇫🇷 Français"
    }
    
    # Названия для режима ИИ (без звезд в тексте)
    ai_mode_names = {
        "fast": "🚀 Быстрый",
        "quality": "💎 Качественный"
    }
    
    # Форматируем дату регистрации
    registered = "неизвестно"
    if a.get("registered_at"):
        try:
            reg_date = datetime.strptime(a["registered_at"], "%Y-%m-%d %H:%M:%S")
            registered = reg_date.strftime("%d.%m.%Y %H:%M")
        except:
            registered = a["registered_at"][:16]
    
    # Формируем текст профиля (БЕЗ Markdown, просто текст)
    text = (
        f"👤 ПРОФИЛЬ\n\n"
        f"🆔 ID: {user_id}\n"
        f"📱 Юзернейм: {username}\n"
        f"📅 Регистрация: {registered}\n\n"
        
        f"📊 СТАТИСТИКА\n"
        f"💬 Сообщений всего: {a.get('total_messages', 0)}\n"
        f"🖼 Картинок всего: {a.get('total_images', 0)}\n"
        f"⭐ Потрачено звезд: {a.get('total_stars_spent', 0)}\n"
        f"💎 Баланс: {balance} ⭐\n\n"
        
        f"⚙️ ТЕКУЩЕЕ\n"
        f"🎭 Характер: {persona_names.get(persona, persona)}\n"
        f"🌐 Язык: {lang_names.get(lang, lang)}\n"
        f"🔄 Режим: {'📱 Mini App' if use_mini_app else '💬 Встроенный'}\n"
        f"⚡ Режим ИИ: {ai_mode_names.get(ai_mode, ai_mode)}\n"
        f"💳 FREE: {'✅ Да' if a.get('is_free') else '❌ Нет'}\n"
        f"⛔ Блокировка: {'❌ Да' if a.get('is_blocked') else '✅ Нет'}"
    )
    
    try:
        # Отправляем/обновляем сообщение с профилем (БЕЗ parse_mode)
        await query.message.edit_text(
            text=text,
            reply_markup=tab_kb(user_id)
        )
        # Сохраняем ID сообщения для последующего удаления
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Профиль показан для {user_id}")
        
    except Exception as e:
        print(f"⚠️ Ошибка при показе профиля: {e}")
        # Если не получилось отредактировать - отправляем новое меню
        await send_fresh_menu(context.bot, user_id)