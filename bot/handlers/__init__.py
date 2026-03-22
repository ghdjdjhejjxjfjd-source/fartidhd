# bot/handlers/__init__.py - УБИРАЕМ old_handlers
from .start import start
from .router import on_button, open_tab
from .navigation import back_to_previous, back_to_menu, ignore
from .state import navigation_stack
from .tabs.profile import show_profile
from .tabs.help import show_help
from .tabs.status import show_status
from .tabs.ref import show_ref
from .tabs.support import show_support
from .tabs.buy_stars import show_buy_stars, buy_stars_package
from .tabs.style import show_style_settings, set_style
from .tabs.ai_lang import show_ai_lang_settings, set_ai_lang
from bot.utils import handle_message  # ← импортируем handle_message из utils

__all__ = [
    'start',
    'on_button',
    'open_tab',
    'navigation_stack',
    'back_to_previous',
    'back_to_menu',
    'ignore',
    'show_profile',
    'show_help',
    'show_status',
    'show_ref',
    'show_support',
    'show_buy_stars',
    'buy_stars_package',
    'show_style_settings',
    'set_style',
    'show_ai_lang_settings',
    'set_ai_lang',
    'handle_message',
]