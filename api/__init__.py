from .config import api

# Импортируем все маршруты
from . import routes
from . import stars
from . import image

# Функция для отправки логов (должна быть доступна везде)
from .config import send_log_to_group

# Экспортируем api для использования в main.py
__all__ = ['api']