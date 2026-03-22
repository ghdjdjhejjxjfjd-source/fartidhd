# bot/handlers/tabs/profile.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С ЛОКАЛИЗАЦИЕЙ
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from api import (
    get_access, get_user_persona, get_user_lang, 
    get_use_mini_app, get_ai_mode, get_ai_mode_changes
)
from payments import get_balance
from bot.menu import tab_kb
from bot.utils import set_last_menu, send_fresh_menu
from bot.helpers import format_balance
from bot.locales import get_text, get_lang_name, get_persona_name, get_mode_name, get_work_mode_name


async def show_profile(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Показать профиль пользователя"""
    
    # Получаем свежие данные из БД
    a = get_access(user_id)
    balance = get_balance(user_id)
    formatted_balance = format_balance(balance)
    persona = get_user_persona(user_id)
    lang = get_user_lang(user_id)
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    
    # Получаем username если есть
    username = "—"
    if query.from_user and query.from_user.username:
        username = f"@{query.from_user.username}"
    
    # Форматируем дату регистрации
    registered = "неизвестно"
    if a.get("registered_at"):
        try:
            reg_date = datetime.strptime(a["registered_at"], "%Y-%m-%d %H:%M:%S")
            registered = reg_date.strftime("%d.%m.%Y %H:%M")
        except:
            registered = a["registered_at"][:16]
    
    # Формируем текст профиля с локализацией
    text = get_text(user_id, "profile_template").format(
        username=username,
        registered=registered,
        messages=a.get('total_messages', 0),
        images=a.get('total_images', 0),
        spent=a.get('total_stars_spent', 0),
        balance=formatted_balance,
        lang=get_lang_name(user_id, lang),
        mode=get_work_mode_name(user_id, "miniapp" if use_mini_app else "inline"),
        ai_mode=get_mode_name(user_id, ai_mode)
    )
    
    try:
        await query.message.edit_text(
            text=text,
            reply_markup=tab_kb(user_id)
        )
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Профиль показан для {user_id}")
        
    except Exception as e:
        print(f"⚠️ Ошибка при показе профиля: {e}")
        await send_fresh_menu(context.bot, user_id)