# api/payments.py
# Этот файл просто перенаправляет всё в payments_db

from .payments_db import *

# Для совместимости со старым кодом
from .payments_db import STAR_PACKAGES, get_packages, get_package
from .payments_db import get_balance, add_stars, spend_stars
from .payments_db import get_top_users, reset_balance

__all__ = [
    'STAR_PACKAGES',
    'get_packages',
    'get_package',
    'get_balance',
    'add_stars',
    'spend_stars',
    'get_top_users',
    'reset_balance'
]