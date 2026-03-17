# bot/helpers.py
def format_balance(balance: float) -> str:
    """Форматирует баланс: 10.0, 10.5, 0.3"""
    if balance == int(balance):
        return f"{int(balance)}"
    return f"{balance:.1f}"