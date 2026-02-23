from .config import api

# Импортируем функции из db.py
from .db import (
    get_access, get_last_menu, set_last_menu, clear_last_menu,
    set_user_lang, get_user_lang,
    set_user_persona, get_user_persona,
    set_use_mini_app, get_use_mini_app,
    set_free, set_blocked,
    increment_messages, increment_images, add_stars_spent,
    get_ai_mode, set_ai_mode
)

# Импортируем функции из memory.py
from .memory import mem_get, mem_add, mem_clear, build_memory_prompt  # ✅ ДОБАВЛЕНО

# Импортируем все маршруты
from . import routes
from . import stars
from . import image

# Функция для отправки логов
from .config import send_log_to_group

# Экспортируем всё для импорта из api
__all__ = [
    'api', 
    'get_access', 'get_last_menu', 'set_last_menu', 'clear_last_menu',
    'set_user_lang', 'get_user_lang',
    'set_user_persona', 'get_user_persona',
    'set_use_mini_app', 'get_use_mini_app',
    'set_free', 'set_blocked',
    'increment_messages', 'increment_images', 'add_stars_spent',
    'get_ai_mode', 'set_ai_mode',
    'mem_get', 'mem_add', 'mem_clear', 'build_memory_prompt',  # ✅ ДОБАВЛЕНО
    'send_log_to_group'
]