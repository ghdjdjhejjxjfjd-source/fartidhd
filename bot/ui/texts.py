# bot/ui/texts.py

# Тексты на разных языках
TEXTS = {
    "ru": {
        "chat_start": "💬 Напиши сообщение для ИИ.\nОтправь текст, и я отвечу.\n\nДля отмены напиши /cancel",
        "image_start": "🖼 Отправь описание картинки.\nНапример: 'красивый закат в горах'\n\nДля отмены напиши /cancel",
        "tools_menu": "🔧 **Инструменты**\n\nВыбери что хочешь сделать:",
        "no_stars": "❌ Недостаточно звезд.\nКупи звезды в меню: ⭐ Купить звезды",
        "blocked": "⛔ Доступ заблокирован.",
        "thinking": "🤔 Думаю...",
        "generating": "🎨 Генерирую картинку... (до 30 секунд)",
    },
    "en": {
        "chat_start": "💬 Write a message for AI.\nI'll reply.\n\nTo cancel type /cancel",
        "image_start": "🖼 Describe the image.\nExample: 'beautiful sunset in mountains'\n\nTo cancel type /cancel",
        "tools_menu": "🔧 **Tools**\n\nChoose what you want:",
        "no_stars": "❌ Not enough stars.\nBuy stars in menu: ⭐ Buy stars",
        "blocked": "⛔ Access blocked.",
        "thinking": "🤔 Thinking...",
        "generating": "🎨 Generating image... (up to 30 seconds)",
    }
}

def get_text(key: str, lang: str = "ru") -> str:
    """Получить текст по ключу и языку"""
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)