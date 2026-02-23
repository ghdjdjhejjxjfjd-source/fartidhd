# bot_handlers.py
import os
from datetime import datetime

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

from api import get_access, get_last_menu, set_last_menu, clear_last_menu, set_use_mini_app, get_use_mini_app, set_user_persona, get_user_persona, set_user_lang, get_user_lang
from payments import get_balance

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
MINIAPP_URL = (os.getenv("MINIAPP_URL") or "").strip()

# лог-группа: TARGET_GROUP_ID приоритет
GROUP_ID_RAW = (os.getenv("TARGET_GROUP_ID") or os.getenv("LOG_GROUP_ID") or "0").strip()
try:
    GROUP_ID = int(GROUP_ID_RAW)
except Exception:
    GROUP_ID = 0


def is_valid_https_url(url: str) -> bool:
    return url.startswith("https://") and len(url) > len("https://")


def send_log_http(text: str):
    if not BOT_TOKEN or not GROUP_ID:
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": GROUP_ID, "text": text},
            timeout=12,
        )
        if not r.ok:
            print("LOG ERROR:", r.status_code, r.text)
    except Exception as e:
        print("LOG ERROR:", e)


def build_start_log(update: Update) -> str:
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = (user.username or "—") if user else "—"
    full_name = f"{(user.first_name or '') if user else ''} {(user.last_name or '') if user else ''}".strip() or "—"

    chat_type = chat.type if chat else "—"
    chat_id = chat.id if chat else "—"
    text = (msg.text or "").strip() if msg else ""

    return (
        "🚀 /start\n"
        f"🕒 {time_str}\n"
        f"👤 {full_name} (@{username})\n"
        f"🆔 user_id: {user.id if user else '—'}\n"
        f"💬 chat_type: {chat_type}\n"
        f"🏷 chat_id: {chat_id}\n"
        f"✉️ text: {text}"
    )


# =========================
#   UI: MENU + TABS
# =========================

# Тексты на разных языках
MENU_TEXTS = {
    "ru": "🤖 InstaGroq AI\n\nВыбирай действие кнопками ниже 👇",
    "en": "🤖 InstaGroq AI\n\nChoose action with buttons below 👇",
    "kk": "🤖 InstaGroq AI\n\nӘрекетті төмендегі батырмалармен таңдаңыз 👇",
    "tr": "🤖 InstaGroq AI\n\nAşağıdaki butonlarla işlem seçin 👇",
    "uk": "🤖 InstaGroq AI\n\nОбирай дію кнопками нижче 👇",
    "fr": "🤖 InstaGroq AI\n\nChoisissez l'action avec les boutons ci-dessous 👇",
}

TAB_TEXTS = {
    "ru": {
        "blocked": "⛔ Доступ заблокирован.\n\nЕсли ты считаешь это ошибкой — напиши админу.",
        "need_pay": "💰 Чтобы открыть Mini App, нужно купить пакет.\n\nОплату подключим позже.",
        "need_stars": "⭐ Для доступа к Mini App нужна хотя бы 1 звезда.\n\nКупите пакет звезд ниже 👇",
        "buy_pack": "💰 Купить пакет\n\nПакеты сообщений (пример):\n• 100 сообщений — 99₽\n• 500 сообщений — 399₽\n• 2000 сообщений — 999₽\n\nОплату подключим позже.",
        "settings": "⚙️ Настройки\n\nВыбери раздел:",
        "help": "❓ Помощь\n\nНажми «Открыть Mini App» или используй встроенный чат.",
        "profile": "👤 Профиль\n\nРаздел в разработке.",
        "status": "📌 Статус\n\nРаздел в разработке.",
        "ref": "🎁 Рефералы\n\nРаздел в разработке.",
        "support": "💬 Поддержка\n\nРаздел в разработке.",
        "faq": "📚 FAQ\n\nРаздел в разработке.",
        "about": "ℹ️ О проекте\n\nРаздел в разработке.",
        "buy_stars": "⭐ Пакеты звезд\n\nВыберите пакет для пополнения:",
        "balance": "⭐ Ваш баланс звезд",
        "mode_settings": "🔄 Режим работы\n\nВыбери как пользоваться ботом:",
        "persona_settings": "🎭 Характер ИИ\n\nВыбери как ИИ будет отвечать:",
        "lang_settings": "🌐 Язык\n\nВыбери язык интерфейса:",
    },
    "en": {
        "blocked": "⛔ Access blocked.\n\nIf you think this is a mistake — contact admin.",
        "need_pay": "💰 To open Mini App, you need to buy a package.\n\nPayment will be added later.",
        "need_stars": "⭐ To access Mini App you need at least 1 star.\n\nBuy star packages below 👇",
        "buy_pack": "💰 Buy package\n\nMessage packages (example):\n• 100 messages — $1\n• 500 messages — $4\n• 2000 messages — $10",
        "settings": "⚙️ Settings\n\nChoose section:",
        "help": "❓ Help\n\nClick «Open Mini App» or use built-in chat.",
        "profile": "👤 Profile\n\nSection in development.",
        "status": "📌 Status\n\nSection in development.",
        "ref": "🎁 Referrals\n\nSection in development.",
        "support": "💬 Support\n\nSection in development.",
        "faq": "📚 FAQ\n\nSection in development.",
        "about": "ℹ️ About\n\nSection in development.",
        "buy_stars": "⭐ Star packages\n\nChoose package:",
        "balance": "⭐ Your star balance",
        "mode_settings": "🔄 Mode\n\nChoose how to use the bot:",
        "persona_settings": "🎭 AI Personality\n\nChoose how AI should respond:",
        "lang_settings": "🌐 Language\n\nChoose interface language:",
    },
    "kk": {
        "blocked": "⛔ Қатынау бұғатталған.\n\nҚате деп ойласаңыз — әкімшіге жазыңыз.",
        "need_pay": "💰 Mini App ашу үшін пакет сатып алу керек.\n\nТөлем кейінірек қосылады.",
        "need_stars": "⭐ Mini App қатынау үшін кемінде 1 жұлдыз қажет.\n\nТөменде жұлдыз пакеттерін сатып алыңыз 👇",
        "buy_pack": "💰 Пакет сатып алу\n\nХабарлама пакеттері (мысалы):\n• 100 хабарлама — 500₸\n• 500 хабарлама — 2000₸\n• 2000 хабарлама — 5000₸",
        "settings": "⚙️ Баптаулар\n\nБөлімді таңдаңыз:",
        "help": "❓ Көмек\n\n«Mini App ашу» батырмасын басыңыз немесе кірістірілген чатты пайдаланыңыз.",
        "profile": "👤 Профиль\n\nБөлім әзірленуде.",
        "status": "📌 Мәртебе\n\nБөлім әзірленуде.",
        "ref": "🎁 Рефералдар\n\nБөлім әзірленуде.",
        "support": "💬 Қолдау\n\nБөлім әзірленуде.",
        "faq": "📚 Сұрақ-жауап\n\nБөлім әзірленуде.",
        "about": "ℹ️ Жоба туралы\n\nБөлім әзірленуде.",
        "buy_stars": "⭐ Жұлдыз пакеттері\n\nПакетті таңдаңыз:",
        "balance": "⭐ Сіздің жұлдыз балансыңыз",
        "mode_settings": "🔄 Режим\n\nБотты қалай пайдалану керектігін таңдаңыз:",
        "persona_settings": "🎭 ЖИ мінезі\n\nЖИ қалай жауап беруін таңдаңыз:",
        "lang_settings": "🌐 Тіл\n\nИнтерфейс тілін таңдаңыз:",
    },
    "tr": {
        "blocked": "⛔ Erişim engellendi.\n\nBunun bir hata olduğunu düşünüyorsanız — admin'e yazın.",
        "need_pay": "💰 Mini App'i açmak için paket satın almanız gerekiyor.\n\nÖdeme daha sonra eklenecek.",
        "need_stars": "⭐ Mini App'e erişmek için en az 1 yıldız gerekli.\n\nAşağıdan yıldız paketleri satın alın 👇",
        "buy_pack": "💰 Paket satın al\n\nMesaj paketleri (örnek):\n• 100 mesaj — 50₺\n• 500 mesaj — 200₺\n• 2000 mesaj — 500₺",
        "settings": "⚙️ Ayarlar\n\nBölüm seçin:",
        "help": "❓ Yardım\n\n«Mini App'i Aç» butonuna tıklayın veya yerleşik sohbeti kullanın.",
        "profile": "👤 Profil\n\nBölüm geliştirme aşamasında.",
        "status": "📌 Durum\n\nBölüm geliştirme aşamasında.",
        "ref": "🎁 Referanslar\n\nBölüm geliştirme aşamasında.",
        "support": "💬 Destek\n\nBölüm geliştirme aşamasında.",
        "faq": "📚 SSS\n\nBölüm geliştirme aşamasında.",
        "about": "ℹ️ Proje hakkında\n\nBölüm geliştirme aşamasında.",
        "buy_stars": "⭐ Yıldız paketleri\n\nPaket seçin:",
        "balance": "⭐ Yıldız bakiyeniz",
        "mode_settings": "🔄 Mod\n\nBotu nasıl kullanacağınızı seçin:",
        "persona_settings": "🎭 Yapay Zeka Kişiliği\n\nYapay Zeka'nın nasıl yanıt vereceğini seçin:",
        "lang_settings": "🌐 Dil\n\nArayüz dilini seçin:",
    },
    "uk": {
        "blocked": "⛔ Доступ заблоковано.\n\nЯкщо ви вважаєте це помилкою — напишіть адміну.",
        "need_pay": "💰 Щоб відкрити Mini App, потрібно купити пакет.\n\nОплату підключимо пізніше.",
        "need_stars": "⭐ Для доступу до Mini App потрібна хоча б 1 зірка.\n\nКупіть пакет зірок нижче 👇",
        "buy_pack": "💰 Купити пакет\n\nПакети повідомлень (приклад):\n• 100 повідомлень — 50₴\n• 500 повідомлень — 200₴\n• 2000 повідомлень — 500₴",
        "settings": "⚙️ Налаштування\n\nВиберіть розділ:",
        "help": "❓ Допомога\n\nНатисніть «Відкрити Mini App» або використовуйте вбудований чат.",
        "profile": "👤 Профіль\n\nРозділ в розробці.",
        "status": "📌 Статус\n\nРозділ в розробці.",
        "ref": "🎁 Реферали\n\nРозділ в розробці.",
        "support": "💬 Підтримка\n\nРозділ в розробці.",
        "faq": "📚 FAQ\n\nРозділ в розробці.",
        "about": "ℹ️ Про проєкт\n\nРозділ в розробці.",
        "buy_stars": "⭐ Пакети зірок\n\nВиберіть пакет:",
        "balance": "⭐ Ваш баланс зірок",
        "mode_settings": "🔄 Режим\n\nВиберіть як користуватися ботом:",
        "persona_settings": "🎭 Характер ШІ\n\nВиберіть як ШІ відповідатиме:",
        "lang_settings": "🌐 Мова\n\nВиберіть мову інтерфейсу:",
    },
    "fr": {
        "blocked": "⛔ Accès bloqué.\n\nSi vous pensez que c'est une erreur — contactez l'admin.",
        "need_pay": "💰 Pour ouvrir Mini App, vous devez acheter un forfait.\n\nPaiement sera ajouté plus tard.",
        "need_stars": "⭐ Pour accéder à Mini App, vous avez besoin d'au moins 1 étoile.\n\nAchetez des forfaits d'étoiles ci-dessous 👇",
        "buy_pack": "💰 Acheter forfait\n\nForfaits de messages (exemple):\n• 100 messages — 5€\n• 500 messages — 20€\n• 2000 messages — 50€",
        "settings": "⚙️ Paramètres\n\nChoisissez une section:",
        "help": "❓ Aide\n\nCliquez sur «Ouvrir Mini App» ou utilisez le chat intégré.",
        "profile": "👤 Profil\n\nSection en développement.",
        "status": "📌 Statut\n\nSection en développement.",
        "ref": "🎁 Parrainage\n\nSection en développement.",
        "support": "💬 Support\n\nSection en développement.",
        "faq": "📚 FAQ\n\nSection en développement.",
        "about": "ℹ️ À propos\n\nSection en développement.",
        "buy_stars": "⭐ Forfaits d'étoiles\n\nChoisissez un forfait:",
        "balance": "⭐ Votre solde d'étoiles",
        "mode_settings": "🔄 Mode\n\nChoisissez comment utiliser le bot:",
        "persona_settings": "🎭 Personnalité IA\n\nChoisissez comment l'IA doit répondre:",
        "lang_settings": "🌐 Langue\n\nChoisissez la langue de l'interface:",
    }
}

# Тексты для кнопок
BUTTON_TEXTS = {
    "ru": {
        "back": "⬅️ Назад",
        "friendly": "😊 Общительный",
        "fun": "😂 Весёлый",
        "smart": "🧐 Умный",
        "strict": "😐 Строгий",
        "miniapp_mode": "📱 Mini App",
        "inline_mode": "💬 Встроенный",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "lang_kk": "🇰🇿 Қазақша",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_uk": "🇺🇦 Українська",
        "lang_fr": "🇫🇷 Français",
        "yes": "✅ Да",
        "no": "❌ Нет",
    },
    "en": {
        "back": "⬅️ Back",
        "friendly": "😊 Friendly",
        "fun": "😂 Fun",
        "smart": "🧐 Smart",
        "strict": "😐 Strict",
        "miniapp_mode": "📱 Mini App",
        "inline_mode": "💬 Built-in",
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "lang_kk": "🇰🇿 Kazakh",
        "lang_tr": "🇹🇷 Turkish",
        "lang_uk": "🇺🇦 Ukrainian",
        "lang_fr": "🇫🇷 French",
        "yes": "✅ Yes",
        "no": "❌ No",
    },
    "kk": {
        "back": "⬅️ Артқа",
        "friendly": "😊 Көпшіл",
        "fun": "😂 Көңілді",
        "smart": "🧐 Ақылды",
        "strict": "😐 Қатаң",
        "miniapp_mode": "📱 Mini App",
        "inline_mode": "💬 Кірістірілген",
        "lang_ru": "🇷🇺 Орыс",
        "lang_en": "🇬🇧 Ағылшын",
        "lang_kk": "🇰🇿 Қазақ",
        "lang_tr": "🇹🇷 Түрік",
        "lang_uk": "🇺🇦 Украин",
        "lang_fr": "🇫🇷 Француз",
        "yes": "✅ Иә",
        "no": "❌ Жоқ",
    },
    "tr": {
        "back": "⬅️ Geri",
        "friendly": "😊 Samimi",
        "fun": "😂 Eğlenceli",
        "smart": "🧐 Zeki",
        "strict": "😐 Katı",
        "miniapp_mode": "📱 Mini App",
        "inline_mode": "💬 Yerleşik",
        "lang_ru": "🇷🇺 Rusça",
        "lang_en": "🇬🇧 İngilizce",
        "lang_kk": "🇰🇿 Kazakça",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_uk": "🇺🇦 Ukraynaca",
        "lang_fr": "🇫🇷 Fransızca",
        "yes": "✅ Evet",
        "no": "❌ Hayır",
    },
    "uk": {
        "back": "⬅️ Назад",
        "friendly": "😊 Дружній",
        "fun": "😂 Веселий",
        "smart": "🧐 Розумний",
        "strict": "😐 Суворий",
        "miniapp_mode": "📱 Mini App",
        "inline_mode": "💬 Вбудований",
        "lang_ru": "🇷🇺 Російська",
        "lang_en": "🇬🇧 Англійська",
        "lang_kk": "🇰🇿 Казахська",
        "lang_tr": "🇹🇷 Турецька",
        "lang_uk": "🇺🇦 Українська",
        "lang_fr": "🇫🇷 Французька",
        "yes": "✅ Так",
        "no": "❌ Ні",
    },
    "fr": {
        "back": "⬅️ Retour",
        "friendly": "😊 Amical",
        "fun": "😂 Drôle",
        "smart": "🧐 Intelligent",
        "strict": "😐 Strict",
        "miniapp_mode": "📱 Mini App",
        "inline_mode": "💬 Intégré",
        "lang_ru": "🇷🇺 Russe",
        "lang_en": "🇬🇧 Anglais",
        "lang_kk": "🇰🇿 Kazakh",
        "lang_tr": "🇹🇷 Turc",
        "lang_uk": "🇺🇦 Ukrainien",
        "lang_fr": "🇫🇷 Français",
        "yes": "✅ Oui",
        "no": "❌ Non",
    }
}


def get_text(user_id: int, key: str, default: str = "") -> str:
    """Получить текст на языке пользователя"""
    lang = get_user_lang(user_id)
    if key in TAB_TEXTS.get(lang, {}):
        return TAB_TEXTS[lang][key]
    return TAB_TEXTS["ru"].get(key, default)


def get_button_text(user_id: int, key: str) -> str:
    """Получить текст кнопки на языке пользователя"""
    lang = get_user_lang(user_id)
    return BUTTON_TEXTS.get(lang, BUTTON_TEXTS["ru"]).get(key, key)


def tab_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    back_text = get_button_text(user_id, "back")
    return InlineKeyboardMarkup([[InlineKeyboardButton(back_text, callback_data="back_to_menu")]])


def settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура настроек с реальными кнопками"""
    use_mini_app = get_use_mini_app(user_id)
    bt = lambda key: get_button_text(user_id, key)
    
    keyboard = [
        [InlineKeyboardButton(bt("friendly"), callback_data="set_persona:friendly"),
         InlineKeyboardButton(bt("fun"), callback_data="set_persona:fun")],
        [InlineKeyboardButton(bt("smart"), callback_data="set_persona:smart"),
         InlineKeyboardButton(bt("strict"), callback_data="set_persona:strict")],
        [InlineKeyboardButton("─" * 10, callback_data="ignore")],  # разделитель
    ]
    
    # Кнопки режима работы (с отметкой текущего)
    if use_mini_app:
        keyboard.append([
            InlineKeyboardButton(f"✅ {bt('miniapp_mode')}", callback_data="switch_to_miniapp"),
            InlineKeyboardButton(bt("inline_mode"), callback_data="switch_to_inline")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(bt("miniapp_mode"), callback_data="switch_to_miniapp"),
            InlineKeyboardButton(f"✅ {bt('inline_mode')}", callback_data="switch_to_inline")
        ])
    
    keyboard.append([InlineKeyboardButton("─" * 10, callback_data="ignore")])  # разделитель
    
    # Кнопка языка
    current_lang = get_user_lang(user_id)
    lang_flag = {
        "ru": "🇷🇺", "en": "🇬🇧", "kk": "🇰🇿", 
        "tr": "🇹🇷", "uk": "🇺🇦", "fr": "🇫🇷"
    }.get(current_lang, "🌐")
    
    keyboard.append([InlineKeyboardButton(
        f"{lang_flag} {bt(f'lang_{current_lang}')}", 
        callback_data="tab:lang_settings"
    )])
    
    keyboard.append([InlineKeyboardButton(bt("back"), callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора режима"""
    use_mini_app = get_use_mini_app(user_id)
    bt = lambda key: get_button_text(user_id, key)
    
    keyboard = []
    
    if use_mini_app:
        keyboard.append([InlineKeyboardButton(f"✅ {bt('miniapp_mode')}", callback_data="ignore")])
        keyboard.append([InlineKeyboardButton(bt("inline_mode"), callback_data="switch_to_inline")])
    else:
        keyboard.append([InlineKeyboardButton(bt("miniapp_mode"), callback_data="switch_to_miniapp")])
        keyboard.append([InlineKeyboardButton(f"✅ {bt('inline_mode')}", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton(bt("back"), callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)


def persona_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора характера"""
    current = get_user_persona(user_id) or "friendly"
    bt = lambda key: get_button_text(user_id, key)
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ {bt('friendly')}" if current == "friendly" else bt("friendly"),
                callback_data="set_persona:friendly"
            ),
            InlineKeyboardButton(
                f"✅ {bt('fun')}" if current == "fun" else bt("fun"),
                callback_data="set_persona:fun"
            )
        ],
        [
            InlineKeyboardButton(
                f"✅ {bt('smart')}" if current == "smart" else bt("smart"),
                callback_data="set_persona:smart"
            ),
            InlineKeyboardButton(
                f"✅ {bt('strict')}" if current == "strict" else bt("strict"),
                callback_data="set_persona:strict"
            )
        ],
        [InlineKeyboardButton(bt("back"), callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    current = get_user_lang(user_id) or "ru"
    bt = lambda key: get_button_text(user_id, key)
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ {bt('lang_ru')}" if current == "ru" else bt("lang_ru"),
                callback_data="set_lang:ru"
            ),
            InlineKeyboardButton(
                f"✅ {bt('lang_en')}" if current == "en" else bt("lang_en"),
                callback_data="set_lang:en"
            )
        ],
        [
            InlineKeyboardButton(
                f"✅ {bt('lang_kk')}" if current == "kk" else bt("lang_kk"),
                callback_data="set_lang:kk"
            ),
            InlineKeyboardButton(
                f"✅ {bt('lang_tr')}" if current == "tr" else bt("lang_tr"),
                callback_data="set_lang:tr"
            )
        ],
        [
            InlineKeyboardButton(
                f"✅ {bt('lang_uk')}" if current == "uk" else bt("lang_uk"),
                callback_data="set_lang:uk"
            ),
            InlineKeyboardButton(
                f"✅ {bt('lang_fr')}" if current == "fr" else bt("lang_fr"),
                callback_data="set_lang:fr"
            )
        ],
        [InlineKeyboardButton(bt("back"), callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def stars_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с пакетами звезд"""
    from payments import get_packages
    bt = lambda key: get_button_text(user_id, key)
    
    keyboard = []
    packages = get_packages()
    
    for p in packages:
        stars = p["stars"]
        price = f"${p['price_usd']:.2f}"
        discount = f" 🔥 -{p['discount']}%" if p['discount'] > 0 else ""
        popular = " ⭐" if p.get('popular', False) else ""
        
        btn_text = f"{stars} ⭐ – {price}{discount}{popular}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_stars:{p['id']}")])
    
    keyboard.append([InlineKeyboardButton(bt("back"), callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)


def main_menu_for_user(user_id: int) -> InlineKeyboardMarkup:
    a = get_access(user_id) if user_id else {"is_free": False, "is_blocked": False}
    balance = get_balance(user_id)
    use_mini_app = get_use_mini_app(user_id)
    bt = lambda key: get_button_text(user_id, key)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton("⛔ Доступ заблокирован", callback_data="tab:blocked")])
        return InlineKeyboardMarkup(keyboard)

    # Баланс звезд
    keyboard.append([InlineKeyboardButton(f"⭐ {get_text(user_id, 'balance')}: {balance}", callback_data="tab:balance")])

    # Кнопки в зависимости от режима
    if use_mini_app:
        # Режим Mini App
        can_open_miniapp = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        
        if can_open_miniapp:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            if balance < 1:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_stars")])
            else:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_pay")])
    else:
        # Встроенный режим (чат в Telegram)
        can_use_chat = (balance >= 1 or a.get("is_free"))
        
        if can_use_chat:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="inline_chat")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="inline_image")])
        else:
            keyboard.append([InlineKeyboardButton("💬 Чат с ИИ", callback_data="tab:need_stars")])
            keyboard.append([InlineKeyboardButton("🖼 Генерация картинки", callback_data="tab:need_stars")])

    # Кнопка покупки звезд
    keyboard.append([InlineKeyboardButton("⭐ Купить звезды", callback_data="tab:buy_stars")])

    # Нижние кнопки (2 в ряд)
    row1 = [
        InlineKeyboardButton("⚙️ Настройки", callback_data="tab:settings"),
        InlineKeyboardButton("❓ Помощь", callback_data="tab:help"),
    ]
    row2 = [
        InlineKeyboardButton("👤 Профиль", callback_data="tab:profile"),
        InlineKeyboardButton("📌 Статус", callback_data="tab:status"),
    ]
    row3 = [
        InlineKeyboardButton("🎁 Рефералы", callback_data="tab:ref"),
        InlineKeyboardButton("💬 Поддержка", callback_data="tab:support"),
    ]
    
    keyboard.append(row1)
    keyboard.append(row2)
    keyboard.append(row3)

    return InlineKeyboardMarkup(keyboard)


# =========================
#   MENU MESSAGE MANAGEMENT
# =========================
async def delete_prev_menu(bot, user_id: int):
    chat_id, msg_id = get_last_menu(user_id)
    if not chat_id or not msg_id:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        print(f"🗑️ Удалено старое меню для {user_id}")
    except Exception:
        pass
    clear_last_menu(user_id)


async def send_fresh_menu(bot, user_id: int, text: str = None):
    # удаляем предыдущее меню
    await delete_prev_menu(bot, user_id)

    if text is None:
        text = get_text(user_id, "menu", MENU_TEXTS.get(get_user_lang(user_id), MENU_TEXTS["ru"]))

    # отправляем новое
    m = await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=main_menu_for_user(user_id),
    )
    set_last_menu(user_id, user_id, m.message_id)


async def update_user_menu(bot, user_id: int):
    """Принудительно обновить меню пользователя"""
    await send_fresh_menu(bot, user_id)


async def send_block_notice(bot, user_id: int):
    # удаляем меню
    await delete_prev_menu(bot, user_id)

    # просто текст (без меню)
    await bot.send_message(chat_id=user_id, text=get_text(user_id, "blocked"))


async def edit_to_menu(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    try:
        text = get_text(user_id, "menu", MENU_TEXTS.get(get_user_lang(user_id), MENU_TEXTS["ru"]))
        await query.message.edit_text(text, reply_markup=main_menu_for_user(user_id))
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id)


async def edit_to_tab(context: ContextTypes.DEFAULT_TYPE, query, user_id: int, tab_key: str):
    text = get_text(user_id, tab_key, "Раздел в разработке.")
    
    # Для баланса показываем актуальное значение
    if tab_key == "balance":
        balance = get_balance(user_id)
        text = f"⭐ {get_text(user_id, 'balance')}: {balance}"
    
    # Выбираем клавиатуру
    if tab_key == "buy_stars":
        reply_markup = stars_kb(user_id)
    elif tab_key == "mode_settings":
        reply_markup = mode_settings_kb(user_id)
    elif tab_key == "persona_settings":
        reply_markup = persona_settings_kb(user_id)
    elif tab_key == "lang_settings":
        reply_markup = lang_settings_kb(user_id)
    elif tab_key == "settings":
        reply_markup = settings_kb(user_id)
    else:
        reply_markup = tab_kb(user_id)
    
    try:
        await query.message.edit_text(text, reply_markup=reply_markup)
        set_last_menu(user_id, user_id, query.message.message_id)
    except Exception:
        await send_fresh_menu(context.bot, user_id, text)


# =========================
#   INLINE CHAT HANDLERS
# =========================
async def inline_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало чата в Telegram"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text(get_text(uid, "blocked"))
        return
    
    if not a.get("is_free") and balance < 1:
        await query.message.reply_text(
            f"❌ {get_text(uid, 'need_stars')}"
        )
        return
    
    lang = get_user_lang(uid)
    messages = {
        "ru": "💬 Напиши сообщение для ИИ.\nОтправь текст, и я отвечу.\n\nДля отмены напиши /cancel",
        "en": "💬 Write a message for AI.\nSend text, and I'll reply.\n\nTo cancel, type /cancel",
        "kk": "💬 ЖИ үшін хабарлама жазыңыз.\nМәтінді жіберіңіз, мен жауап беремін.\n\nБолдырмау үшін /cancel деп жазыңыз",
        "tr": "💬 Yapay Zeka için mesaj yazın.\nMetin gönderin, cevap vereceğim.\n\nİptal için /cancel yazın",
        "uk": "💬 Напишіть повідомлення для ШІ.\nНадішліть текст, і я відповім.\n\nДля скасування напишіть /cancel",
        "fr": "💬 Écrivez un message pour l'IA.\nEnvoyez le texte, je répondrai.\n\nPour annuler, écrivez /cancel"
    }
    await query.message.reply_text(messages.get(lang, messages["ru"]))
    
    # Запоминаем что пользователь в режиме чата
    context.user_data["in_chat_mode"] = True


async def inline_image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало генерации картинки в Telegram"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    uid = user.id
    
    a = get_access(uid)
    balance = get_balance(uid)
    
    if a.get("is_blocked"):
        await query.message.reply_text(get_text(uid, "blocked"))
        return
    
    if not a.get("is_free") and balance < 1:
        await query.message.reply_text(
            f"❌ {get_text(uid, 'need_stars')}"
        )
        return
    
    lang = get_user_lang(uid)
    messages = {
        "ru": "🖼 Отправь описание картинки.\nНапример: 'красивый закат в горах'\n\nДля отмены напиши /cancel",
        "en": "🖼 Send image description.\nExample: 'beautiful sunset in mountains'\n\nTo cancel, type /cancel",
        "kk": "🖼 Сурет сипаттамасын жіберіңіз.\nМысалы: 'таулардағы әдемі күн батуы'\n\nБолдырмау үшін /cancel деп жазыңыз",
        "tr": "🖼 Resim açıklaması gönderin.\nÖrnek: 'dağlarda güzel gün batımı'\n\nİptal için /cancel yazın",
        "uk": "🖼 Надішліть опис картинки.\nНаприклад: 'гарний захід сонця в горах'\n\nДля скасування напишіть /cancel",
        "fr": "🖼 Envoyez la description de l'image.\nExemple: 'beau coucher de soleil dans les montagnes'\n\nPour annuler, écrivez /cancel"
    }
    await query.message.reply_text(messages.get(lang, messages["ru"]))
    
    # Запоминаем что пользователь в режиме генерации
    context.user_data["in_image_mode"] = True


# =========================
#   HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_log_http(build_start_log(update))

    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return

    await send_fresh_menu(context.bot, uid)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = (query.data or "").strip()

    try:
        await query.answer()
    except Exception:
        pass

    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return

    # игнорируем разделители
    if data == "ignore":
        return

    # назад в меню
    if data == "back_to_menu":
        await edit_to_menu(context, query, uid)
        return

    # вкладки: tab:<key>
    if data.startswith("tab:"):
        key = data.split("tab:", 1)[1].strip()
        await edit_to_tab(context, query, uid, key)
        return

    # покупка звезд
    if data.startswith("buy_stars:"):
        package_id = data.split("buy_stars:", 1)[1].strip()
        from payments import get_package
        package = get_package(package_id)
        
        if package:
            stars = package["stars"]
            price = package["price_usd"]
            
            await query.message.edit_text(
                f"✅ Вы выбрали пакет {package['name']}\n"
                f"⭐ {stars} звезд за ${price}\n\n"
                f"Оплата через Telegram Stars будет доступна позже.\n"
                f"Сейчас это тестовый режим.",
                reply_markup=tab_kb(uid)
            )
        else:
            await query.message.edit_text(
                "❌ Пакет не найден",
                reply_markup=tab_kb(uid)
            )
        return

    # переключение режима
    if data == "switch_to_miniapp":
        set_use_mini_app(uid, True)
        await query.message.edit_text(
            "✅ Режим переключен на Mini App!",
            reply_markup=tab_kb(uid)
        )
        await update_user_menu(context.bot, uid)
        return

    if data == "switch_to_inline":
        set_use_mini_app(uid, False)
        await query.message.edit_text(
            "✅ Режим переключен на встроенный!",
            reply_markup=tab_kb(uid)
        )
        await update_user_menu(context.bot, uid)
        return

    # выбор характера
    if data.startswith("set_persona:"):
        persona = data.split("set_persona:", 1)[1].strip()
        set_user_persona(uid, persona)
        
        persona_names = {
            "friendly": get_button_text(uid, "friendly"),
            "fun": get_button_text(uid, "fun"),
            "smart": get_button_text(uid, "smart"),
            "strict": get_button_text(uid, "strict")
        }
        
        await query.message.edit_text(
            f"✅ {get_text(uid, 'persona_settings')}\n\n{persona_names.get(persona, persona)}",
            reply_markup=tab_kb(uid)
        )
        return

    # выбор языка
    if data.startswith("set_lang:"):
        lang = data.split("set_lang:", 1)[1].strip()
        set_user_lang(uid, lang)
        
        await query.message.edit_text(
            f"✅ {get_button_text(uid, f'lang_{lang}')}",
            reply_markup=tab_kb(uid)
        )
        # Обновляем всё меню на новом языке
        await update_user_menu(context.bot, uid)
        return

    # inline чат
    if data == "inline_chat":
        await inline_chat_start(update, context)
        return

    # inline генерация
    if data == "inline_image":
        await inline_image_start(update, context)
        return

    await edit_to_menu(context, query, uid)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (для inline режима)"""
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    uid = user.id
    
    # Проверяем режим
    if not context.user_data.get("in_chat_mode") and not context.user_data.get("in_image_mode"):
        return
    
    a = get_access(uid)
    balance = get_balance(uid)
    lang = get_user_lang(uid)
    
    if a.get("is_blocked"):
        await update.message.reply_text(get_text(uid, "blocked"))
        context.user_data.clear()
        return
    
    if not a.get("is_free") and balance < 1:
        await update.message.reply_text(get_text(uid, "need_stars"))
        context.user_data.clear()
        return
    
    text = update.message.text
    
    if context.user_data.get("in_chat_mode"):
        # Отправляем в Groq
        thinking = {
            "ru": "🤔 Думаю...",
            "en": "🤔 Thinking...",
            "kk": "🤔 Ойлануда...",
            "tr": "🤔 Düşünüyorum...",
            "uk": "🤔 Думаю...",
            "fr": "🤔 Je pense..."
        }
        await update.message.reply_text(thinking.get(lang, thinking["ru"]))
        
        try:
            from groq_client import ask_groq
            persona = get_user_persona(uid) or "friendly"
            reply = ask_groq(text, lang=lang, persona=persona)
            
            await update.message.reply_text(reply)
            
            # Списываем звезду если не FREE
            if not a.get("is_free"):
                from payments import spend_stars
                spend_stars(uid, 1)
                
        except Exception as e:
            error_msg = {
                "ru": f"❌ Ошибка: {e}",
                "en": f"❌ Error: {e}",
                "kk": f"❌ Қате: {e}",
                "tr": f"❌ Hata: {e}",
                "uk": f"❌ Помилка: {e}",
                "fr": f"❌ Erreur: {e}"
            }
            await update.message.reply_text(error_msg.get(lang, error_msg["ru"]))
        
        # Выходим из режима
        context.user_data["in_chat_mode"] = False
        
    elif context.user_data.get("in_image_mode"):
        # Генерируем картинку
        generating = {
            "ru": "🎨 Генерирую картинку...",
            "en": "🎨 Generating image...",
            "kk": "🎨 Сурет жасалуда...",
            "tr": "🎨 Resim oluşturuluyor...",
            "uk": "🎨 Генерую зображення...",
            "fr": "🎨 Génération d'image..."
        }
        await update.message.reply_text(generating.get(lang, generating["ru"]))
        
        try:
            from stability_client import generate_image
            image_base64 = generate_image(text)
            
            # Отправляем фото
            import base64
            image_data = base64.b64decode(image_base64.split(",")[1])
            
            caption = {
                "ru": f"🖼 Промпт: {text}",
                "en": f"🖼 Prompt: {text}",
                "kk": f"🖼 Сипаттама: {text}",
                "tr": f"🖼 İstem: {text}",
                "uk": f"🖼 Запит: {text}",
                "fr": f"🖼 Prompt: {text}"
            }
            
            await update.message.reply_photo(
                photo=image_data,
                caption=caption.get(lang, caption["ru"])
            )
            
            # Списываем звезду если не FREE
            if not a.get("is_free"):
                from payments import spend_stars
                spend_stars(uid, 1)
                
        except Exception as e:
            error_msg = {
                "ru": f"❌ Ошибка генерации: {e}",
                "en": f"❌ Generation error: {e}",
                "kk": f"❌ Жасау қатесі: {e}",
                "tr": f"❌ Oluşturma hatası: {e}",
                "uk": f"❌ Помилка генерації: {e}",
                "fr": f"❌ Erreur de génération: {e}"
            }
            await update.message.reply_text(error_msg.get(lang, error_msg["ru"]))
        
        # Выходим из режима
        context.user_data["in_image_mode"] = False