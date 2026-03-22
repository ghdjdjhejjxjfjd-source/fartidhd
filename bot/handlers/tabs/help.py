# bot/handlers/tabs/help.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.utils import set_last_menu, send_fresh_menu
from bot.locales import get_text, get_button_text
from .state import navigation_stack

# Список разделов помощи
HELP_SECTIONS = [
    "chat",
    "image", 
    "fast_mode",
    "quality_mode",
    "personas",
    "styles",
    "stars",
    "referrals",
    "modes"
]

def help_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура со списком разделов помощи"""
    keyboard = []
    
    # Кнопки разделов (2 в ряд)
    sections = [
        ("chat", "help_chat_btn"),
        ("image", "help_image_btn"),
        ("fast_mode", "help_fast_mode_btn"),
        ("quality_mode", "help_quality_mode_btn"),
        ("personas", "help_personas_btn"),
        ("styles", "help_styles_btn"),
        ("stars", "help_stars_btn"),
        ("referrals", "help_referrals_btn"),
        ("modes", "help_modes_btn")
    ]
    
    row = []
    for i, (section_id, btn_key) in enumerate(sections):
        row.append(InlineKeyboardButton(
            get_button_text(user_id, btn_key),
            callback_data=f"help_section:{section_id}"
        ))
        if len(row) == 2 or i == len(sections) - 1:
            keyboard.append(row)
            row = []
    
    # Кнопка назад в главное меню
    keyboard.append([InlineKeyboardButton(
        get_button_text(user_id, "back"),
        callback_data="back_to_menu"
    )])
    
    return InlineKeyboardMarkup(keyboard)


async def show_help_menu(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    """Показать главное меню помощи (список разделов)"""
    text = get_text(user_id, "help_title")
    
    try:
        await query.message.edit_text(
            text=text,
            reply_markup=help_menu_kb(user_id)
        )
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Меню помощи показано для {user_id}")
    except Exception as e:
        print(f"⚠️ Ошибка при показе меню помощи: {e}")
        await send_fresh_menu(context.bot, user_id)


async def show_help_section(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, section: str):
    """Показать подробное описание раздела помощи"""
    text = get_text(user_id, f"help_{section}_text")
    
    # Клавиатура: только кнопка назад (в меню помощи)
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            get_button_text(user_id, "back"),
            callback_data="back_to_help_menu"
        )
    ]])
    
    try:
        await query.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
        set_last_menu(user_id, user_id, query.message.message_id)
        print(f"✅ Раздел помощи '{section}' показан для {user_id}")
    except Exception as e:
        print(f"⚠️ Ошибка при показе раздела помощи: {e}")
        await send_fresh_menu(context.bot, user_id)