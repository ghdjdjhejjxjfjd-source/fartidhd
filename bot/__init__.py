# bot/__init__.py
from .handlers.start import start
from .handlers.router import on_button
from .old_handlers import handle_message  # ←改了这里
from .config import send_log_http, build_start_log

__all__ = [
    'start',
    'on_button', 
    'handle_message',
    'send_log_http',
    'build_start_log'
]