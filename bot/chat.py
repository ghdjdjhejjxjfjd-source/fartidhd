from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from api import get_access, get_user_persona, get_user_lang, get_user_ai_lang, get_user_style, get_ai_mode, increment_messages, add_stars_spent
from payments import get_balance, spend_stars
from groq_client import ask_groq
from openai_client import ask_openai
from .config import send_log_http

# Храним ID последнего сообщения бота для каждого пользователя
last_bot_message = {}

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
    global last_bot_message
    
    # Проверка на выход из чата
    if text.lower() == "/cancel":
        await update.message.reply_text(
            "✅ Чат завершен. Возвращаю в меню...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")]
            ])
        )
        context.user_data["in_chat_mode"] = False
        return
    
    a = get_access(uid)
    interface_lang = get_user_lang(uid)  # язык интерфейса
    ai_lang = get_user_ai_lang(uid)      # язык ответов ИИ
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
    
    # Отправляем ОДНО сообщение с анимацией
    sent_msg = await update.message.reply_text("⏳ Печатает...")
    
    try:
        # Выбираем AI в зависимости от режима
        if ai_mode == "fast":
            # Groq - используем язык ИИ, характер и стиль
            reply = ask_groq(
                user_text=text,
                lang=ai_lang,  # язык ответов ИИ
                persona=persona,
                style=style
            )
        else:
            # OpenAI - используем язык ИИ и стиль (характер не используется)
            reply = ask_openai(
                user_text=text,
                lang=ai_lang,  # язык ответов ИИ
                style=style
            )
        
        if reply:
            # Удаляем кнопку под предыдущим сообщением бота
            if uid in last_bot_message:
                try:
                    await context.bot.edit_message_reply_markup(
                        chat_id=uid,
                        message_id=last_bot_message[uid],
                        reply_markup=None
                    )
                except:
                    pass
            
            # Отправляем ответ ТОЛЬКО с кнопкой выхода
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Выйти из чата", callback_data="exit_chat")]
            ])
            
            await sent_msg.edit_text(reply, reply_markup=keyboard)
            
            # Сохраняем ID этого сообщения
            last_bot_message[uid] = sent_msg.message_id
            
            # Списываем звезды
            if not a.get("is_free"):
                spend_stars(uid, cost)
                add_stars_spent(uid, cost)
            
            increment_messages(uid)
            send_log_http(f"💬 Чат в боте ({ai_mode}): {uid} -> {text[:50]}...")
            
        else:
            await sent_msg.edit_text("❌ Ошибка получения ответа")
            
    except Exception as e:
        error_msg = str(e)
        if "insufficient_stars" in error_msg:
            await sent_msg.edit_text("❌ Недостаточно звезд. Купите в меню.")
            context.user_data["in_chat_mode"] = False
        elif "network" in error_msg.lower():
            await sent_msg.edit_text("📡 Проблема с интернетом. Попробуйте позже.")
            context.user_data["in_chat_mode"] = False
        else:
            await sent_msg.edit_text(f"❌ Ошибка: {error_msg[:100]}")
            context.user_data["in_chat_mode"] = False