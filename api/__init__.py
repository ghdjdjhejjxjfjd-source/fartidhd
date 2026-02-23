from .config import api

# Импортируем функции из db.py (ДОБАВЛЯЕМ set_free и set_blocked)
from .db import (
    get_access, get_last_menu, set_last_menu, clear_last_menu,
    set_user_lang, get_user_lang,
    set_user_persona, get_user_persona,
    set_use_mini_app, get_use_mini_app,
    set_free, set_blocked  # ← вот эти две строчки добавить
)

# Импортируем все маршруты
from . import routes
from . import stars
from . import image

# Функция для отправки логов
from .config import send_log_to_group

# Экспортируем всё для импорта из api (ДОБАВЛЯЕМ В __all__)
__all__ = [
    'api', 
    'get_access', 'get_last_menu', 'set_last_menu', 'clear_last_menu',
    'set_user_lang', 'get_user_lang',
    'set_user_persona', 'get_user_persona',
    'set_use_mini_app', 'get_use_mini_app',
    'set_free', 'set_blocked',  # ← и сюда добавить
    'send_log_to_group'
]