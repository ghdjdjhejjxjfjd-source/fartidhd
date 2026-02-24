# api/payments.py
# Этот файл перенаправляет всё в payments_db

from .payments_db import (
    get_balance, add_stars, spend_stars, get_packages, get_package,
    get_top_users, reset_balance
)

# Пакеты звезд (оставляем здесь, если нужны)
STAR_PACKAGES = [
    {
        "id": "starter",
        "name": "Starter",
        "stars": 100,
        "price_usd": 1.99,
        "price_per_star": 0.0199,
        "discount": 0,
        "popular": False,
    },
    {
        "id": "basic",
        "name": "Basic",
        "stars": 500,
        "price_usd": 8.99,
        "price_per_star": 0.0179,
        "discount": 10,
        "popular": False,
    },
    {
        "id": "popular",
        "name": "Popular",
        "stars": 1000,
        "price_usd": 16.99,
        "price_per_star": 0.0169,
        "discount": 15,
        "popular": True,
    },
    {
        "id": "pro",
        "name": "Pro",
        "stars": 2500,
        "price_usd": 39.99,
        "price_per_star": 0.0159,
        "discount": 20,
        "popular": False,
    },
    {
        "id": "premium",
        "name": "Premium",
        "stars": 5000,
        "price_usd": 74.99,
        "price_per_star": 0.0149,
        "discount": 25,
        "popular": False,
    },
    {
        "id": "ultimate",
        "name": "Ultimate",
        "stars": 10000,
        "price_usd": 139.99,
        "price_per_star": 0.0139,
        "discount": 30,
        "popular": False,
    },
]

__all__ = [
    'get_balance', 'add_stars', 'spend_stars', 'get_packages', 'get_package',
    'get_top_users', 'reset_balance', 'STAR_PACKAGES'
]