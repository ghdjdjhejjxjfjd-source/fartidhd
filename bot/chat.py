from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from api import get_access, get_user_persona, get_user_lang, get_user_ai_lang, get_user_style, get_ai_mode, increment_messages, add_stars_spent
from payments import get_balance, spend_stars
from groq_client import ask_groq
from openai_client import ask_openai
from .config import send_log_http
from .menu import main_menu_for_user

async def inline_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    ai_mode = get_ai_mode(uid)
    cost = 0.3 if ai_mode == "fast" else 1.0
    
    if a.get("is_blocked"):
        await query.message.reply_text("⛔ Доступ заблокирован.")
        return
    
    if not a.get("is_free") and balance < cost:
        await query.message.reply_text(
            f"❌ Недостаточно звезд (нужно {cost}⭐).\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        return
    
    mode_names = {"fast": "🚀 Быстрый (Groq)", "quality": "💎 Качественный (OpenAI)"}
    style_names = {"short": "📏 Коротко", "steps": "📋 По шагам", "detail": "📚 Подробно"}
    lang_names = {
        "ru": "🇷🇺 Русский", "en": "🇬🇧 English", "kk": "🇰🇿 Қазақша",
        "tr": "🇹🇷 Türkçe", "uk": "🇺🇦 Українська", "fr": "🇫🇷 Français"
    }
    
    current_style = get_user_style(uid)
    current_ai_lang = get_user_ai_lang(uid)
    
    await query.message.reply_text(
        f"💬 Напиши сообщение для ИИ.\n"
        f"Режим: {mode_names.get(ai_mode, 'Быстрый')}\n"
        f"Язык ответов: {lang_names.get(current_ai_lang, 'Русский')}\n"
        f"Стиль: {style_names.get(current_style, 'По шагам')}\n"
        f"Стоимость: {cost}⭐ за сообщение\n\n"
        f"Отправляй сообщения, я буду отвечать.\n"
        f"Для выхода из чата напиши /cancel"
    )
    
    context.user_data["in_chat_mode"] = True

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE, uid: int, text: str):
    
    # ===== ВЫХОД ИЗ ЧАТА =====
    if text.lower() == "/cancel":
        context.user_data["in_chat_mode"] = False
        
        try:
            await update.message.delete()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=uid,
            text="🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
            reply_markup=main_menu_for_user(uid)
        )
        return
    
    # ===== ОБЫЧНОЕ СООБЩЕНИЕ =====
    a = get_access(uid)
    ai_lang = get_user_ai_lang(uid)
    persona = get_user_persona(uid)
    style = get_user_style(uid)
    ai_mode = get_ai_mode(uid)
    cost = 0.3 if ai_mode == "fast" else 1.0
    
    if a.get("is_blocked"):
        await update.message.reply_text("⛔ Доступ заблокирован.")
        context.user_data["in_chat_mode"] = False
        return
    
    balance = get_balance(uid)
    if not a.get("is_free") and balance < cost:
        await update.message.reply_text(
            f"❌ Недостаточно звезд (нужно {cost}⭐).\n"
            "Купи звезды в меню: ⭐ Купить звезды"
        )
        context.user_data["in_chat_mode"] = False
        return
    
    typing_msg = await update.message.reply_text("⏳ Печатает...")
    
    try:
        if ai_mode == "fast":
            reply = ask_groq(
                user_text=text,
                lang=ai_lang,
                persona=persona,
                style=style
            )
        else:
            reply = ask_openai(
                user_text=text,
                lang=ai_lang,
                style=style
            )
        
        if reply:
            await typing_msg.delete()
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Выйти из чата", callback_data="exit_chat")]
            ])
            
            await context.bot.send_message(
                chat_id=uid,
                text=reply,
                reply_markup=keyboard
            )
            
            if not a.get("is_free"):
                spend_stars(uid, cost)
                add_stars_spent(uid, cost)
            
            increment_messages(uid)
            send_log_http(f"💬 Чат в боте ({ai_mode}): {uid} -> {text[:50]}...")
            
        else:
            await typing_msg.edit_text("❌ Ошибка получения ответа")
            
    except Exception as e:
        error_msg = str(e)
        if "insufficient_stars" in error_msg:
            await typing_msg.edit_text("❌ Недостаточно звезд. Купите в меню.")
        elif "network" in error_msg.lower():
            await typing_msg.edit_text("📡 Проблема с интернетом. Попробуйте позже.")
        else:
            await typing_msg.edit_text(f"❌ Ошибка: {error_msg[:100]}")
        
        context.user_data["in_chat_mode"] = False