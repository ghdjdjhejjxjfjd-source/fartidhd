from .config import api

# Импортируем функции из db.py
from .db import (
    get_access, get_last_menu, set_last_menu, clear_last_menu,
    set_user_lang, get_user_lang,
    set_user_persona, get_user_persona,
    set_user_style, get_user_style,
    set_use_mini_app, get_use_mini_app,
    set_free, set_blocked,
    increment_messages, increment_images, add_stars_spent,
    get_ai_mode, set_ai_mode,
    get_ai_mode_changes,
    get_user_limits,
    increment_groq_persona, increment_groq_style, increment_openai_style
)

# Импортируем функции из memory.py
from .memory import mem_get, mem_add, mem_clear, build_memory_prompt

# Импортируем функции из payments_db.py
from .payments_db import (
    get_balance, add_stars, spend_stars, get_packages, get_package,
    get_top_users, reset_balance
)

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
    'set_user_style', 'get_user_style',
    'set_use_mini_app', 'get_use_mini_app',
    'set_free', 'set_blocked',
    'increment_messages', 'increment_images', 'add_stars_spent',
    'get_ai_mode', 'set_ai_mode',
    'get_ai_mode_changes',
    'get_user_limits',
    'increment_groq_persona', 'increment_groq_style', 'increment_openai_style',
    'mem_get', 'mem_add', 'mem_clear', 'build_memory_prompt',
    'get_balance', 'add_stars', 'spend_stars', 'get_packages', 'get_package',
    'get_top_users', 'reset_balance',
    'send_log_to_group'
]