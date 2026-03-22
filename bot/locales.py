# bot/locales.py - ПОЛНЫЙ ФАЙЛ ЛОКАЛИЗАЦИИ
from api import get_user_lang

# =========================
# ПЕРЕВОДЫ НА 6 ЯЗЫКОВ
# =========================

LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "kk": "🇰🇿 Қазақша",
    "tr": "🇹🇷 Türkçe",
    "uk": "🇺🇦 Українська",
    "fr": "🇫🇷 Français"
}

# =========================
# ОСНОВНЫЕ ТЕКСТЫ
# =========================
TEXTS = {
    # Главное меню
    "menu_title": {
        "ru": "💫 NextAI\n\nВыбирай действие кнопками ниже 👇",
        "en": "💫 NextAI\n\nChoose action with buttons below 👇",
        "kk": "💫 NextAI\n\nӘрекетті төмендегі батырмалармен таңдаңыз 👇",
        "tr": "💫 NextAI\n\nAşağıdaki butonlarla işlem seçin 👇",
        "uk": "💫 NextAI\n\nОбери дію кнопками нижче 👇",
        "fr": "💫 NextAI\n\nChoisis une action avec les boutons ci-dessous 👇"
    },
    
    # Кнопки главного меню
    "balance_button": {
        "ru": "⭐ Баланс: {balance} звезд",
        "en": "⭐ Balance: {balance} stars",
        "kk": "⭐ Баланс: {balance} жұлдыз",
        "tr": "⭐ Bakiye: {balance} yıldız",
        "uk": "⭐ Баланс: {balance} зірок",
        "fr": "⭐ Solde: {balance} étoiles"
    },
    "open_miniapp": {
        "ru": "🚀 Открыть Mini App",
        "en": "🚀 Open Mini App",
        "kk": "🚀 Mini App ашу",
        "tr": "🚀 Mini App Aç",
        "uk": "🚀 Відкрити Mini App",
        "fr": "🚀 Ouvrir Mini App"
    },
    "buy_stars_button": {
        "ru": "⭐ Купить звезды",
        "en": "⭐ Buy stars",
        "kk": "⭐ Жұлдыздар сатып алу",
        "tr": "⭐ Yıldız satın al",
        "uk": "⭐ Купити зірки",
        "fr": "⭐ Acheter des étoiles"
    },
    "settings": {
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
        "kk": "⚙️ Баптаулар",
        "tr": "⚙️ Ayarlar",
        "uk": "⚙️ Налаштування",
        "fr": "⚙️ Paramètres"
    },
    "help": {
        "ru": "❓ Помощь",
        "en": "❓ Help",
        "kk": "❓ Көмек",
        "tr": "❓ Yardım",
        "uk": "❓ Допомога",
        "fr": "❓ Aide"
    },
    "profile": {
        "ru": "👤 Профиль",
        "en": "👤 Profile",
        "kk": "👤 Профиль",
        "tr": "👤 Profil",
        "uk": "👤 Профіль",
        "fr": "👤 Profil"
    },
    "status": {
        "ru": "📌 Статус",
        "en": "📌 Status",
        "kk": "📌 Күй",
        "tr": "📌 Durum",
        "uk": "📌 Статус",
        "fr": "📌 Statut"
    },
    "ref": {
        "ru": "🎁 Рефералы",
        "en": "🎁 Referrals",
        "kk": "🎁 Рефералдар",
        "tr": "🎁 Referanslar",
        "uk": "🎁 Реферали",
        "fr": "🎁 Parrainages"
    },
    "support": {
        "ru": "💬 Поддержка",
        "en": "💬 Support",
        "kk": "💬 Қолдау",
        "tr": "💬 Destek",
        "uk": "💬 Підтримка",
        "fr": "💬 Support"
    },
    "support_blocked_button": {
        "ru": "⛔ Поддержка",
        "en": "⛔ Support",
        "kk": "⛔ Қолдау",
        "tr": "⛔ Destek",
        "uk": "⛔ Підтримка",
        "fr": "⛔ Support"
    },
    "inline_chat": {
        "ru": "💬 Чат с ИИ",
        "en": "💬 AI Chat",
        "kk": "💬 AI чат",
        "tr": "💬 Yapay Zeka Sohbet",
        "uk": "💬 Чат з ШІ",
        "fr": "💬 Chat IA"
    },
    "inline_image": {
        "ru": "🖼 Генерация картинки",
        "en": "🖼 Image generation",
        "kk": "🖼 Сурет генерациялау",
        "tr": "🖼 Görsel oluşturma",
        "uk": "🖼 Генерація зображення",
        "fr": "🖼 Génération d'image"
    },
    
    # Кнопки настроек
    "ai_lang": {
        "ru": "🌐 Язык ответов ИИ",
        "en": "🌐 AI response language",
        "kk": "🌐 AI жауап тілі",
        "tr": "🌐 YZ yanıt dili",
        "uk": "🌐 Мова відповідей ШІ",
        "fr": "🌐 Langue de réponse IA"
    },
    "persona": {
        "ru": "🎭 Характер ({remaining}/{max_limit})",
        "en": "🎭 Personality ({remaining}/{max_limit})",
        "kk": "🎭 Мінез ({remaining}/{max_limit})",
        "tr": "🎭 Karakter ({remaining}/{max_limit})",
        "uk": "🎭 Характер ({remaining}/{max_limit})",
        "fr": "🎭 Personnalité ({remaining}/{max_limit})"
    },
    "style": {
        "ru": "📝 Стиль ответа ({remaining}/{max_limit})",
        "en": "📝 Response style ({remaining}/{max_limit})",
        "kk": "📝 Жауап стилі ({remaining}/{max_limit})",
        "tr": "📝 Yanıt stili ({remaining}/{max_limit})",
        "uk": "📝 Стиль відповіді ({remaining}/{max_limit})",
        "fr": "📝 Style de réponse ({remaining}/{max_limit})"
    },
    "ai_mode": {
        "ru": "⚡ Режим ИИ ({remaining}/{max_limit})",
        "en": "⚡ AI mode ({remaining}/{max_limit})",
        "kk": "⚡ AI режимі ({remaining}/{max_limit})",
        "tr": "⚡ YZ modu ({remaining}/{max_limit})",
        "uk": "⚡ Режим ШІ ({remaining}/{max_limit})",
        "fr": "⚡ Mode IA ({remaining}/{max_limit})"
    },
    "mode": {
        "ru": "🔄 Режим работы",
        "en": "🔄 Work mode",
        "kk": "🔄 Жұмыс режимі",
        "tr": "🔄 Çalışma modu",
        "uk": "🔄 Режим роботи",
        "fr": "🔄 Mode de travail"
    },
    "lang": {
        "ru": "🌐 Язык интерфейса",
        "en": "🌐 Interface language",
        "kk": "🌐 Интерфейс тілі",
        "tr": "🌐 Arayüz dili",
        "uk": "🌐 Мова інтерфейсу",
        "fr": "🌐 Langue de l'interface"
    },
    
    # Режимы работы
    "miniapp": {
        "ru": "📱 Mini App",
        "en": "📱 Mini App",
        "kk": "📱 Mini App",
        "tr": "📱 Mini App",
        "uk": "📱 Mini App",
        "fr": "📱 Mini App"
    },
    "inline": {
        "ru": "💬 Встроенный",
        "en": "💬 Inline",
        "kk": "💬 Кіріктірілген",
        "tr": "💬 Yerleşik",
        "uk": "💬 Вбудований",
        "fr": "💬 Intégré"
    },
    
    # Режимы ИИ
    "fast": {
        "ru": "🚀 Быстрый",
        "en": "🚀 Fast",
        "kk": "🚀 Жылдам",
        "tr": "🚀 Hızlı",
        "uk": "🚀 Швидкий",
        "fr": "🚀 Rapide"
    },
    "quality": {
        "ru": "💎 Качественный",
        "en": "💎 Quality",
        "kk": "💎 Сапалы",
        "tr": "💎 Kaliteli",
        "uk": "💎 Якісний",
        "fr": "💎 Qualité"
    },
    "fast_limit": {
        "ru": "🚀 Быстрый (лимит)",
        "en": "🚀 Fast (limit)",
        "kk": "🚀 Жылдам (лимит)",
        "tr": "🚀 Hızlı (limit)",
        "uk": "🚀 Швидкий (ліміт)",
        "fr": "🚀 Rapide (limite)"
    },
    "quality_limit": {
        "ru": "💎 Качественный (лимит)",
        "en": "💎 Quality (limit)",
        "kk": "💎 Сапалы (лимит)",
        "tr": "💎 Kaliteli (limit)",
        "uk": "💎 Якісний (ліміт)",
        "fr": "💎 Qualité (limite)"
    },
    
    # Кнопки подтверждения
    "confirm_yes": {
        "ru": "✅ Да, сменить",
        "en": "✅ Yes, change",
        "kk": "✅ Иә, өзгерту",
        "tr": "✅ Evet, değiştir",
        "uk": "✅ Так, змінити",
        "fr": "✅ Oui, changer"
    },
    "confirm_no": {
        "ru": "❌ Нет, отмена",
        "en": "❌ No, cancel",
        "kk": "❌ Жоқ, болдырмау",
        "tr": "❌ Hayır, iptal",
        "uk": "❌ Ні, скасувати",
        "fr": "❌ Non, annuler"
    },
    "back": {
        "ru": "⬅️ Назад",
        "en": "⬅️ Back",
        "kk": "⬅️ Артқа",
        "tr": "⬅️ Geri",
        "uk": "⬅️ Назад",
        "fr": "⬅️ Retour"
    },
    "limit": {
        "ru": "{name} (лимит)",
        "en": "{name} (limit)",
        "kk": "{name} (лимит)",
        "tr": "{name} (limit)",
        "uk": "{name} (ліміт)",
        "fr": "{name} (limite)"
    },
    "share": {
        "ru": "📤 Поделиться",
        "en": "📤 Share",
        "kk": "📤 Бөлісу",
        "tr": "📤 Paylaş",
        "uk": "📤 Поділитися",
        "fr": "📤 Partager"
    },
    "exit_hint": {
        "ru": "⬅️ Нажмите для выхода",
        "en": "⬅️ Click to exit",
        "kk": "⬅️ Шығу үшін басыңыз",
        "tr": "⬅️ Çıkmak için tıklayın",
        "uk": "⬅️ Натисніть для виходу",
        "fr": "⬅️ Cliquez pour sortir"
    },
    
    # Тексты вкладок
    "blocked": {
        "ru": "⛔ Доступ заблокирован.\n\nЕсли ты считаешь это ошибкой — напиши админу.",
        "en": "⛔ Access blocked.\n\nIf you think this is a mistake — contact admin.",
        "kk": "⛔ Қолжетімділік бұғатталды.\n\nЕгер бұл қате деп ойласаңыз — әкімшіге жазыңыз.",
        "tr": "⛔ Erişim engellendi.\n\nBunun bir hata olduğunu düşünüyorsanız — yöneticiye yazın.",
        "uk": "⛔ Доступ заблоковано.\n\nЯкщо ти вважаєш це помилкою — напиши адміну.",
        "fr": "⛔ Accès bloqué.\n\nSi tu penses que c'est une erreur — écris à l'administrateur."
    },
    "need_pay": {
        "ru": "💰 Чтобы открыть Mini App, нужно купить пакет.\n\nОплату подключим позже.",
        "en": "💰 To open Mini App, you need to buy a package.\n\nPayment will be connected later.",
        "kk": "💰 Mini App ашу үшін пакет сатып алу керек.\n\nТөлем кейінірек қосылады.",
        "tr": "💰 Mini App'i açmak için bir paket satın almanız gerekiyor.\n\nÖdeme daha sonra bağlanacak.",
        "uk": "💰 Щоб відкрити Mini App, потрібно купити пакет.\n\nОплату підключимо пізніше.",
        "fr": "💰 Pour ouvrir Mini App, tu dois acheter un pack.\n\nLe paiement sera connecté plus tard."
    },
    "need_stars": {
        "ru": "⭐ Для доступа к Mini App нужна хотя бы 1 звезда.\n\nКупите пакет звезд ниже 👇",
        "en": "⭐ To access Mini App you need at least 1 star.\n\nBuy a star pack below 👇",
        "kk": "⭐ Mini App кіру үшін кемінде 1 жұлдыз қажет.\n\nТөменде жұлдыздар пакетін сатып алыңыз 👇",
        "tr": "⭐ Mini App'e erişmek için en az 1 yıldıza ihtiyacınız var.\n\nAşağıdan yıldız paketi satın alın 👇",
        "uk": "⭐ Для доступу до Mini App потрібна хоча б 1 зірка.\n\nКупіть пакет зірок нижче 👇",
        "fr": "⭐ Pour accéder à Mini App, tu as besoin d'au moins 1 étoile.\n\nAchète un pack d'étoiles ci-dessous 👇"
    },
    "need_stars_chat": {
        "ru": "⭐ Недостаточно звезд для чата с ИИ.\n\nДля доступа к чату нужна хотя бы 1 звезда.\n\nКупите звезды в меню ниже 👇",
        "en": "⭐ Not enough stars for AI chat.\n\nTo access chat you need at least 1 star.\n\nBuy stars in the menu below 👇",
        "kk": "⭐ AI чат үшін жұлдыздар жеткіліксіз.\n\nЧатқа кіру үшін кемінде 1 жұлдыз қажет.\n\nТөмендегі мәзірден жұлдыздар сатып алыңыз 👇",
        "tr": "⭐ YZ sohbeti için yeterli yıldız yok.\n\nSohbete erişmek için en az 1 yıldıza ihtiyacınız var.\n\nAşağıdaki menüden yıldız satın alın 👇",
        "uk": "⭐ Недостатньо зірок для чату з ШІ.\n\nДля доступу до чату потрібна хоча б 1 зірка.\n\nКупіть зірки в меню нижче 👇",
        "fr": "⭐ Pas assez d'étoiles pour le chat IA.\n\nPour accéder au chat, tu as besoin d'au moins 1 étoile.\n\nAchète des étoiles dans le menu ci-dessous 👇"
    },
    "need_stars_miniapp": {
        "ru": "⭐ Недостаточно звезд для Mini App.\n\nДля доступа к Mini App нужна хотя бы 1 звезда.\n\nКупите звезды в меню ниже 👇",
        "en": "⭐ Not enough stars for Mini App.\n\nTo access Mini App you need at least 1 star.\n\nBuy stars in the menu below 👇",
        "kk": "⭐ Mini App үшін жұлдыздар жеткіліксіз.\n\nMini App кіру үшін кемінде 1 жұлдыз қажет.\n\nТөмендегі мәзірден жұлдыздар сатып алыңыз 👇",
        "tr": "⭐ Mini App için yeterli yıldız yok.\n\nMini App'e erişmek için en az 1 yıldıza ihtiyacınız var.\n\nAşağıdaki menüden yıldız satın alın 👇",
        "uk": "⭐ Недостатньо зірок для Mini App.\n\nДля доступу до Mini App потрібна хоча б 1 зірка.\n\nКупіть зірки в меню нижче 👇",
        "fr": "⭐ Pas assez d'étoiles pour Mini App.\n\nPour accéder à Mini App, tu as besoin d'au moins 1 étoile.\n\nAchète des étoiles dans le menu ci-dessous 👇"
    },
    "need_stars_image": {
        "ru": "❌ Недостаточно звезд (нужно 10).",
        "en": "❌ Not enough stars (need 10).",
        "kk": "❌ Жұлдыздар жеткіліксіз (10 қажет).",
        "tr": "❌ Yeterli yıldız yok (10 gerekli).",
        "uk": "❌ Недостатньо зірок (потрібно 10).",
        "fr": "❌ Pas assez d'étoiles (10 nécessaires)."
    },
    "buy_pack": {
        "ru": "💰 Купить пакет\n\nПакеты сообщений (пример):\n• 100 сообщений — 99₽\n• 500 сообщений — 399₽\n• 2000 сообщений — 999₽\n\nОплату подключим позже.",
        "en": "💰 Buy package\n\nMessage packs (example):\n• 100 messages — $1.99\n• 500 messages — $8.99\n• 2000 messages — $29.99\n\nPayment will be connected later.",
        "kk": "💰 Пакет сатып алу\n\nХабарлама пакеттері (мысал):\n• 100 хабарлама — 99₽\n• 500 хабарлама — 399₽\n• 2000 хабарлама — 999₽\n\nТөлем кейінірек қосылады.",
        "tr": "💰 Paket satın al\n\nMesaj paketleri (örnek):\n• 100 mesaj — 99₽\n• 500 mesaj — 399₽\n• 2000 mesaj — 999₽\n\nÖdeme daha sonra bağlanacak.",
        "uk": "💰 Купити пакет\n\nПакети повідомлень (приклад):\n• 100 повідомлень — 99₽\n• 500 повідомлень — 399₽\n• 2000 повідомлень — 999₽\n\nОплату підключимо пізніше.",
        "fr": "💰 Acheter un pack\n\nPacks de messages (exemple):\n• 100 messages — 99₽\n• 500 messages — 399₽\n• 2000 messages — 999₽\n\nLe paiement sera connecté plus tard."
    },
    "settings_title": {
        "ru": "⚙️ Настройки\n\nВыбери раздел:",
        "en": "⚙️ Settings\n\nSelect section:",
        "kk": "⚙️ Баптаулар\n\nБөлімді таңдаңыз:",
        "tr": "⚙️ Ayarlar\n\nBölüm seçin:",
        "uk": "⚙️ Налаштування\n\nОберіть розділ:",
        "fr": "⚙️ Paramètres\n\nChoisis une section:"
    },
    "help_text": {
        "ru": "❓ Помощь\n\nНажми «Открыть Mini App» или используй встроенный чат.",
        "en": "❓ Help\n\nClick «Open Mini App» or use inline chat.",
        "kk": "❓ Көмек\n\n«Mini App ашу» батырмасын басыңыз немесе кіріктірілген чатты пайдаланыңыз.",
        "tr": "❓ Yardım\n\n«Mini App Aç» düğmesine tıklayın veya yerleşik sohbeti kullanın.",
        "uk": "❓ Допомога\n\nНатисніть «Відкрити Mini App» або використовуй вбудований чат.",
        "fr": "❓ Aide\n\nClique sur «Ouvrir Mini App» ou utilise le chat intégré."
    },
    "status_text": {
        "ru": "📌 Статус\n\nРаздел в разработке.",
        "en": "📌 Status\n\nSection under development.",
        "kk": "📌 Күй\n\nБөлім әзірленуде.",
        "tr": "📌 Durum\n\nBölüm geliştirme aşamasında.",
        "uk": "📌 Статус\n\nРозділ у розробці.",
        "fr": "📌 Statut\n\nSection en développement."
    },
    "ref_text": {
        "ru": "🎁 Рефералы\n\nРаздел в разработке.",
        "en": "🎁 Referrals\n\nSection under development.",
        "kk": "🎁 Рефералдар\n\nБөлім әзірленуде.",
        "tr": "🎁 Referanslar\n\nBölüm geliştirme aşamasında.",
        "uk": "🎁 Реферали\n\nРозділ у розробці.",
        "fr": "🎁 Parrainages\n\nSection en développement."
    },
    "support_text": {
        "ru": "💬 Поддержка\n\nНапиши свой вопрос.",
        "en": "💬 Support\n\nWrite your question.",
        "kk": "💬 Қолдау\n\nСұрағыңызды жазыңыз.",
        "tr": "💬 Destek\n\nSorunuzu yazın.",
        "uk": "💬 Підтримка\n\nНапиши своє питання.",
        "fr": "💬 Support\n\nÉcris ta question."
    },
    "support_blocked_text": {
        "ru": "⛔ Поддержка заблокирована",
        "en": "⛔ Support is blocked",
        "kk": "⛔ Қолдау бұғатталды",
        "tr": "⛔ Destek engellendi",
        "uk": "⛔ Підтримка заблокована",
        "fr": "⛔ Support bloqué"
    },
    "faq_text": {
        "ru": "📚 FAQ\n\nРаздел в разработке.",
        "en": "📚 FAQ\n\nSection under development.",
        "kk": "📚 FAQ\n\nБөлім әзірленуде.",
        "tr": "📚 SSS\n\nBölüm geliştirme aşamasında.",
        "uk": "📚 FAQ\n\nРозділ у розробці.",
        "fr": "📚 FAQ\n\nSection en développement."
    },
    "about_text": {
        "ru": "ℹ️ О проекте\n\nРаздел в разработке.",
        "en": "ℹ️ About\n\nSection under development.",
        "kk": "ℹ️ Жоба туралы\n\nБөлім әзірленуде.",
        "tr": "ℹ️ Proje hakkında\n\nBölüm geliştirme aşamasında.",
        "uk": "ℹ️ Про проєкт\n\nРозділ у розробці.",
        "fr": "ℹ️ À propos\n\nSection en développement."
    },
    "buy_stars": {
        "ru": "⭐ Пакеты звезд\n\nВыберите пакет для пополнения:",
        "en": "⭐ Star packs\n\nSelect a pack to top up:",
        "kk": "⭐ Жұлдыздар пакеттері\n\nТолтыру үшін пакетті таңдаңыз:",
        "tr": "⭐ Yıldız paketleri\n\nYüklemek için bir paket seçin:",
        "uk": "⭐ Пакети зірок\n\nВиберіть пакет для поповнення:",
        "fr": "⭐ Packs d'étoiles\n\nChoisis un pack pour recharger:"
    },
    "balance_text": {
        "ru": "⭐ Ваш баланс звезд",
        "en": "⭐ Your star balance",
        "kk": "⭐ Сіздің жұлдыздар балансыңыз",
        "tr": "⭐ Yıldız bakiyeniz",
        "uk": "⭐ Ваш баланс зірок",
        "fr": "⭐ Votre solde d'étoiles"
    },
    "balance_text_with_value": {
        "ru": "⭐ Ваш баланс: {balance} звезд",
        "en": "⭐ Your balance: {balance} stars",
        "kk": "⭐ Сіздің балансыңыз: {balance} жұлдыз",
        "tr": "⭐ Bakiyeniz: {balance} yıldız",
        "uk": "⭐ Ваш баланс: {balance} зірок",
        "fr": "⭐ Votre solde: {balance} étoiles"
    },
    "mode_settings": {
        "ru": "🔄 Режим работы\n\nВыбери как пользоваться ботом:",
        "en": "🔄 Work mode\n\nChoose how to use the bot:",
        "kk": "🔄 Жұмыс режимі\n\nБотты қалай пайдалану керектігін таңдаңыз:",
        "tr": "🔄 Çalışma modu\n\nBotu nasıl kullanacağınızı seçin:",
        "uk": "🔄 Режим роботи\n\nОбери як користуватися ботом:",
        "fr": "🔄 Mode de travail\n\nChoisis comment utiliser le bot:"
    },
    "persona_settings": {
        "ru": "🎭 Характер ИИ\n\nВыбери как ИИ будет отвечать:",
        "en": "🎭 AI Personality\n\nChoose how AI will respond:",
        "kk": "🎭 AI мінезі\n\nAI қалай жауап беретінін таңдаңыз:",
        "tr": "🎭 YZ Karakteri\n\nYZ'nin nasıl yanıt vereceğini seçin:",
        "uk": "🎭 Характер ШІ\n\nОбери як ШІ відповідатиме:",
        "fr": "🎭 Personnalité IA\n\nChoisis comment l'IA répondra:"
    },
    "style_settings": {
        "ru": "📝 Стиль ответа\n\nВыбери стиль ответов ИИ:",
        "en": "📝 Response style\n\nChoose AI response style:",
        "kk": "📝 Жауап стилі\n\nAI жауап стилін таңдаңыз:",
        "tr": "📝 Yanıt stili\n\nYZ yanıt stilini seçin:",
        "uk": "📝 Стиль відповіді\n\nОбери стиль відповідей ШІ:",
        "fr": "📝 Style de réponse\n\nChoisis le style de réponse de l'IA:"
    },
    "lang_settings": {
        "ru": "🌐 Язык интерфейса\n\nВыбери язык меню и кнопок:",
        "en": "🌐 Interface language\n\nChoose menu and buttons language:",
        "kk": "🌐 Интерфейс тілі\n\nМәзір мен батырмалар тілін таңдаңыз:",
        "tr": "🌐 Arayüz dili\n\nMenü ve buton dilini seçin:",
        "uk": "🌐 Мова інтерфейсу\n\nОбери мову меню та кнопок:",
        "fr": "🌐 Langue de l'interface\n\nChoisis la langue du menu et des boutons:"
    },
    "ai_lang_settings": {
        "ru": "🌐 Язык ответов ИИ\n\nВыбери на каком языке будет отвечать ИИ:",
        "en": "🌐 AI response language\n\nChoose the language AI will respond in:",
        "kk": "🌐 AI жауап тілі\n\nAI қай тілде жауап беретінін таңдаңыз:",
        "tr": "🌐 YZ yanıt dili\n\nYZ'nin hangi dilde yanıt vereceğini seçin:",
        "uk": "🌐 Мова відповідей ШІ\n\nОбери якою мовою ШІ відповідатиме:",
        "fr": "🌐 Langue de réponse IA\n\nChoisis la langue dans laquelle l'IA répondra:"
    },
    "ai_mode_settings": {
        "ru": "⚡ Режим ИИ\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 БЫСТРЫЙ (0.3 ⭐)\n• Groq AI\n• Можно менять характер, стиль и язык ответов\n\n💎 КАЧЕСТВЕННЫЙ (1 ⭐)\n• OpenAI\n• Можно менять только стиль\n• Язык определяется автоматически\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Сегодня осталось смен режима: {changes_left}/8\n⏰ Сброс в 00:00 (GMT+6)",
        "en": "⚡ AI Mode\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 FAST (0.3 ⭐)\n• Groq AI\n• Can change personality, style and response language\n\n💎 QUALITY (1 ⭐)\n• OpenAI\n• Can change only style\n• Language is detected automatically\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Mode changes left today: {changes_left}/8\n⏰ Reset at 00:00 (GMT+6)",
        "kk": "⚡ AI режимі\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 ЖЫЛДАМ (0.3 ⭐)\n• Groq AI\n• Мінезді, стильді және жауап тілін өзгертуге болады\n\n💎 САПАЛЫ (1 ⭐)\n• OpenAI\n• Тек стильді өзгертуге болады\n• Тіл автоматты түрде анықталады\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Бүгін қалған режим ауыстыру: {changes_left}/8\n⏰ Қалпына келтіру 00:00 (GMT+6)",
        "tr": "⚡ YZ Modu\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 HIZLI (0.3 ⭐)\n• Groq AI\n• Karakter, stil ve yanıt dili değiştirilebilir\n\n💎 KALİTELİ (1 ⭐)\n• OpenAI\n• Sadece stil değiştirilebilir\n• Dil otomatik algılanır\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Bugün kalan mod değişikliği: {changes_left}/8\n⏰ Sıfırlama 00:00 (GMT+6)",
        "uk": "⚡ Режим ШІ\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 ШВИДКИЙ (0.3 ⭐)\n• Groq AI\n• Можна міняти характер, стиль і мову відповідей\n\n💎 ЯКІСНИЙ (1 ⭐)\n• OpenAI\n• Можна міняти тільки стиль\n• Мова визначається автоматично\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Сьогодні залишилось змін режиму: {changes_left}/8\n⏰ Скидання о 00:00 (GMT+6)",
        "fr": "⚡ Mode IA\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 RAPIDE (0.3 ⭐)\n• Groq AI\n• Peut changer la personnalité, le style et la langue de réponse\n\n💎 QUALITÉ (1 ⭐)\n• OpenAI\n• Peut changer uniquement le style\n• La langue est détectée automatiquement\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Changements de mode restants aujourd'hui: {changes_left}/8\n⏰ Réinitialisation à 00:00 (GMT+6)"
    },
    "confirm_ai_mode_change": {
        "ru": "⚠️ ПОДТВЕРЖДЕНИЕ\n\nВы выбрали режим: {new_mode}\n\nТекущий режим: {current_mode}\n\nПри смене режима:\n• История чата будет полностью очищена\n• Все предыдущие сообщения удалятся\n\nПродолжить?",
        "en": "⚠️ CONFIRMATION\n\nYou selected mode: {new_mode}\n\nCurrent mode: {current_mode}\n\nWhen changing mode:\n• Chat history will be completely cleared\n• All previous messages will be deleted\n\nContinue?",
        "kk": "⚠️ РАСТАУ\n\nСіз режимді таңдадыңыз: {new_mode}\n\nАғымдағы режим: {current_mode}\n\nРежимді өзгерту кезінде:\n• Чат тарихы толығымен жойылады\n• Барлық алдыңғы хабарламалар жойылады\n\nЖалғастыру?",
        "tr": "⚠️ ONAYLAMA\n\nSeçtiğiniz mod: {new_mode}\n\nMevcut mod: {current_mode}\n\nMod değiştirirken:\n• Sohbet geçmişi tamamen silinecek\n• Tüm önceki mesajlar silinecek\n\nDevam et?",
        "uk": "⚠️ ПІДТВЕРДЖЕННЯ\n\nВи обрали режим: {new_mode}\n\nПоточний режим: {current_mode}\n\nПри зміні режиму:\n• Історія чату буде повністю очищена\n• Всі попередні повідомлення видаляться\n\nПродовжити?",
        "fr": "⚠️ CONFIRMATION\n\nVous avez sélectionné le mode: {new_mode}\n\nMode actuel: {current_mode}\n\nEn changeant de mode:\n• L'historique du chat sera complètement effacé\n• Tous les messages précédents seront supprimés\n\nContinuer?"
    },
    "limit_exceeded": {
        "ru": "⛔ Лимит исчерпан\n\nСегодня больше нельзя менять эту настройку.\nПопробуй завтра после 00:00.",
        "en": "⛔ Limit exceeded\n\nYou can't change this setting anymore today.\nTry again tomorrow after 00:00.",
        "kk": "⛔ Лимит аяқталды\n\nБүгін бұл баптауды өзгертуге болмайды.\nЕртең 00:00-ден кейін қайталаңыз.",
        "tr": "⛔ Limit aşıldı\n\nBugün bu ayarı değiştiremezsiniz.\nYarın 00:00'dan sonra tekrar deneyin.",
        "uk": "⛔ Ліміт вичерпано\n\nСьогодні більше не можна міняти це налаштування.\nСпробуй завтра після 00:00.",
        "fr": "⛔ Limite dépassée\n\nTu ne peux plus changer ce paramètre aujourd'hui.\nRéessaie demain après 00:00."
    },
    "mode_changed": {
        "ru": "✅ Режим изменен на {mode}\n\n🧹 История чата очищена.\n📊 Сегодня осталось смен режима: {remaining}/8",
        "en": "✅ Mode changed to {mode}\n\n🧹 Chat history cleared.\n📊 Mode changes left today: {remaining}/8",
        "kk": "✅ Режим {mode} өзгертілді\n\n🧹 Чат тарихы жойылды.\n📊 Бүгін қалған режим ауыстыру: {remaining}/8",
        "tr": "✅ Mod {mode} olarak değiştirildi\n\n🧹 Sohbet geçmişi temizlendi.\n📊 Bugün kalan mod değişikliği: {remaining}/8",
        "uk": "✅ Режим змінено на {mode}\n\n🧹 Історію чату очищено.\n📊 Сьогодні залишилось змін режиму: {remaining}/8",
        "fr": "✅ Mode changé en {mode}\n\n🧹 Historique du chat effacé.\n📊 Changements de mode restants aujourd'hui: {remaining}/8"
    },
    "mode_changed_work": {
        "ru": "✅ Режим работы переключен на {mode}!",
        "en": "✅ Work mode switched to {mode}!",
        "kk": "✅ Жұмыс режимі {mode} режиміне ауыстырылды!",
        "tr": "✅ Çalışma modu {mode} olarak değiştirildi!",
        "uk": "✅ Режим роботи переключено на {mode}!",
        "fr": "✅ Mode de travail changé en {mode}!"
    },
    "lang_changed": {
        "ru": "✅ Язык изменен",
        "en": "✅ Language changed",
        "kk": "✅ Тіл өзгертілді",
        "tr": "✅ Dil değiştirildi",
        "uk": "✅ Мову змінено",
        "fr": "✅ Langue changée"
    },
    "persona_changed": {
        "ru": "✅ Характер изменен на: {persona}",
        "en": "✅ Personality changed to: {persona}",
        "kk": "✅ Мінез {persona} өзгертілді",
        "tr": "✅ Karakter {persona} olarak değiştirildi",
        "uk": "✅ Характер змінено на: {persona}",
        "fr": "✅ Personnalité changée en: {persona}"
    },
    "persona_not_available_quality": {
        "ru": "❌ В качественном режиме (OpenAI) характер недоступен.\nПереключитесь на быстрый режим (Groq) чтобы изменить характер.",
        "en": "❌ In quality mode (OpenAI) personality is not available.\nSwitch to fast mode (Groq) to change personality.",
        "kk": "❌ Сапалы режимде (OpenAI) мінез қолжетімсіз.\nМінезді өзгерту үшін жылдам режимге (Groq) ауысыңыз.",
        "tr": "❌ Kaliteli modda (OpenAI) karakter mevcut değil.\nKarakteri değiştirmek için hızlı moda (Groq) geçin.",
        "uk": "❌ У якісному режимі (OpenAI) характер недоступний.\nПереключіться на швидкий режим (Groq) щоб змінити характер.",
        "fr": "❌ En mode qualité (OpenAI) la personnalité n'est pas disponible.\nPasse en mode rapide (Groq) pour changer la personnalité."
    },
    "package_selected": {
        "ru": "✅ Вы выбрали пакет {name}\n⭐ {stars} звезд за ${price}\n\nОплата через Telegram Stars будет доступна позже.",
        "en": "✅ You selected {name} pack\n⭐ {stars} stars for ${price}\n\nPayment via Telegram Stars will be available later.",
        "kk": "✅ Сіз {name} пакетін таңдадыңыз\n⭐ {stars} жұлдыз ${price}\n\nTelegram Stars арқылы төлем кейінірек қолжетімді болады.",
        "tr": "✅ {name} paketini seçtiniz\n⭐ {stars} yıldız ${price}\n\nTelegram Stars ile ödeme daha sonra kullanıma sunulacaktır.",
        "uk": "✅ Ви обрали пакет {name}\n⭐ {stars} зірок за ${price}\n\nОплата через Telegram Stars буде доступна пізніше.",
        "fr": "✅ Vous avez sélectionné le pack {name}\n⭐ {stars} étoiles pour ${price}\n\nLe paiement via Telegram Stars sera disponible plus tard."
    },
    "package_not_found": {
        "ru": "❌ Пакет не найден",
        "en": "❌ Package not found",
        "kk": "❌ Пакет табылмады",
        "tr": "❌ Paket bulunamadı",
        "uk": "❌ Пакет не знайдено",
        "fr": "❌ Pack non trouvé"
    },
    
    # Текст профиля
    "profile_template": {
        "ru": "        👤 ПРОФИЛЬ\n\nНик: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Сообщений: {messages}\n🎨 Картинок: {images}\n💸 Потрачено: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ ТЕКУЩЕЕ\n🌐 Язык: {lang}\n📱 Режим: {mode}\n🤖 ИИ: {ai_mode}",
        "en": "        👤 PROFILE\n\nUsername: {username}\n📅 {registered}\n\n        📊 STATISTICS\n💬 Messages: {messages}\n🎨 Images: {images}\n💸 Spent: {spent} ⭐\n💰 Balance: {balance} ⭐\n\n        ⚙️ CURRENT\n🌐 Language: {lang}\n📱 Mode: {mode}\n🤖 AI: {ai_mode}",
        "kk": "        👤 ПРОФИЛЬ\n\nНик: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Хабарламалар: {messages}\n🎨 Суреттер: {images}\n💸 Жұмсалды: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ АҒЫМДАҒЫ\n🌐 Тіл: {lang}\n📱 Режим: {mode}\n🤖 AI: {ai_mode}",
        "tr": "        👤 PROFİL\n\nKullanıcı adı: {username}\n📅 {registered}\n\n        📊 İSTATİSTİKLER\n💬 Mesajlar: {messages}\n🎨 Görseller: {images}\n💸 Harcanan: {spent} ⭐\n💰 Bakiye: {balance} ⭐\n\n        ⚙️ GÜNCEL\n🌐 Dil: {lang}\n📱 Mod: {mode}\n🤖 YZ: {ai_mode}",
        "uk": "        👤 ПРОФІЛЬ\n\nНік: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Повідомлень: {messages}\n🎨 Картинок: {images}\n💸 Витрачено: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ ПОТОЧНЕ\n🌐 Мова: {lang}\n📱 Режим: {mode}\n🤖 ШІ: {ai_mode}",
        "fr": "        👤 PROFIL\n\nPseudo: {username}\n📅 {registered}\n\n        📊 STATISTIQUES\n💬 Messages: {messages}\n🎨 Images: {images}\n💸 Dépensé: {spent} ⭐\n💰 Solde: {balance} ⭐\n\n        ⚙️ ACTUEL\n🌐 Langue: {lang}\n📱 Mode: {mode}\n🤖 IA: {ai_mode}"
    },
    
    # Текст рефералов
    "ref_template": {
        "ru": "🎁 **РЕФЕРАЛЫ**\n\n📊 **Статистика**\n👥 Приглашено друзей: {count}\n⭐ Заработано звезд: {bonus}\n\n🔗 **Твоя реферальная ссылка:**\n{ref_link}\n\n👇 Нажми на ссылку чтобы скопировать",
        "en": "🎁 **REFERRALS**\n\n📊 **Statistics**\n👥 Friends invited: {count}\n⭐ Stars earned: {bonus}\n\n🔗 **Your referral link:**\n{ref_link}\n\n👇 Click the link to copy",
        "kk": "🎁 **РЕФЕРАЛДАР**\n\n📊 **Статистика**\n👥 Шақырылған достар: {count}\n⭐ Табылған жұлдыздар: {bonus}\n\n🔗 **Сіздің рефералдық сілтемеңіз:**\n{ref_link}\n\n👇 Көшіру үшін сілтемені басыңыз",
        "tr": "🎁 **REFERANSLAR**\n\n📊 **İstatistikler**\n👥 Davet edilen arkadaşlar: {count}\n⭐ Kazanılan yıldızlar: {bonus}\n\n🔗 **Referans bağlantınız:**\n{ref_link}\n\n👇 Kopyalamak için bağlantıya tıklayın",
        "uk": "🎁 **РЕФЕРАЛИ**\n\n📊 **Статистика**\n👥 Запрошено друзів: {count}\n⭐ Зароблено зірок: {bonus}\n\n🔗 **Твоє реферальне посилання:**\n{ref_link}\n\n👇 Натисни на посилання щоб скопіювати",
        "fr": "🎁 **PARRAINAGES**\n\n📊 **Statistiques**\n👥 Amis invités: {count}\n⭐ Étoiles gagnées: {bonus}\n\n🔗 **Ton lien de parrainage:**\n{ref_link}\n\n👇 Clique sur le lien pour copier"
    },
    "share_text": {
        "ru": "🎁 Присоединяйся ко мне в NextAI! {ref_link}",
        "en": "🎁 Join me on NextAI! {ref_link}",
        "kk": "🎁 Маған NextAI-да қосылыңыз! {ref_link}",
        "tr": "🎁 NextAI'de bana katıl! {ref_link}",
        "uk": "🎁 Приєднуйся до мене в NextAI! {ref_link}",
        "fr": "🎁 Rejoins-moi sur NextAI! {ref_link}"
    },
    
    # Тексты чата
    "chat_start_fast": {
        "ru": "💬 Напиши сообщение.\n\nРежим: {mode}\nЯзык ответов: {ai_lang}\nСтиль: {style}\nСтоимость: {cost}⭐",
        "en": "💬 Write a message.\n\nMode: {mode}\nResponse language: {ai_lang}\nStyle: {style}\nCost: {cost}⭐",
        "kk": "💬 Хабарлама жазыңыз.\n\nРежим: {mode}\nЖауап тілі: {ai_lang}\nСтиль: {style}\nҚұны: {cost}⭐",
        "tr": "💬 Bir mesaj yazın.\n\nMod: {mode}\nYanıt dili: {ai_lang}\nStil: {style}\nMaliyet: {cost}⭐",
        "uk": "💬 Напиши повідомлення.\n\nРежим: {mode}\nМова відповідей: {ai_lang}\nСтиль: {style}\nВартість: {cost}⭐",
        "fr": "💬 Écris un message.\n\nMode: {mode}\nLangue de réponse: {ai_lang}\nStyle: {style}\nCoût: {cost}⭐"
    },
    "chat_start_quality": {
        "ru": "💬 Напиши сообщение.\n\nРежим: {mode}\nСтиль: {style}\nСтоимость: {cost}⭐",
        "en": "💬 Write a message.\n\nMode: {mode}\nStyle: {style}\nCost: {cost}⭐",
        "kk": "💬 Хабарлама жазыңыз.\n\nРежим: {mode}\nСтиль: {style}\nҚұны: {cost}⭐",
        "tr": "💬 Bir mesaj yazın.\n\nMod: {mode}\nStil: {style}\nMaliyet: {cost}⭐",
        "uk": "💬 Напиши повідомлення.\n\nРежим: {mode}\nСтиль: {style}\nВартість: {cost}⭐",
        "fr": "💬 Écris un message.\n\nMode: {mode}\nStyle: {style}\nCoût: {cost}⭐"
    },
    "typing": {
        "ru": "⏳ Печатает...",
        "en": "⏳ Typing...",
        "kk": "⏳ Басып жатыр...",
        "tr": "⏳ Yazıyor...",
        "uk": "⏳ Друкує...",
        "fr": "⏳ Écrit..."
    },
    "error": {
        "ru": "❌ Ошибка: {error}",
        "en": "❌ Error: {error}",
        "kk": "❌ Қате: {error}",
        "tr": "❌ Hata: {error}",
        "uk": "❌ Помилка: {error}",
        "fr": "❌ Erreur: {error}"
    },
    
    # Тексты генерации картинок
    "image_start": {
        "ru": "🖼 Напиши описание картинки.\nСтоимость: 10⭐",
        "en": "🖼 Write a description of the image.\nCost: 10⭐",
        "kk": "🖼 Суреттің сипаттамасын жазыңыз.\nҚұны: 10⭐",
        "tr": "🖼 Görselin açıklamasını yazın.\nMaliyet: 10⭐",
        "uk": "🖼 Напиши опис картинки.\nВартість: 10⭐",
        "fr": "🖼 Écris une description de l'image.\nCoût: 10⭐"
    },
    "image_unavailable": {
        "ru": "❌ Сервис генерации недоступен.",
        "en": "❌ Generation service is unavailable.",
        "kk": "❌ Генерация қызметі қолжетімсіз.",
        "tr": "❌ Oluşturma hizmeti kullanılamıyor.",
        "uk": "❌ Сервіс генерації недоступний.",
        "fr": "❌ Le service de génération n'est pas disponible."
    },
    "generating": {
        "ru": "🎨 Генерирую...",
        "en": "🎨 Generating...",
        "kk": "🎨 Генерациялау...",
        "tr": "🎨 Oluşturuluyor...",
        "uk": "🎨 Генерую...",
        "fr": "🎨 Génération..."
    },
    "image_caption": {
        "ru": "🖼 {prompt}...",
        "en": "🖼 {prompt}...",
        "kk": "🖼 {prompt}...",
        "tr": "🖼 {prompt}...",
        "uk": "🖼 {prompt}...",
        "fr": "🖼 {prompt}..."
    },
    
    # НОВЫЙ КЛЮЧ ДЛЯ SAFETY ОШИБКИ
    "image_safety_error": {
        "ru": "❌ Запрос заблокирован системой безопасности.\n\nВозможные причины:\n• Известные персонажи (Tom and Jerry, Mickey Mouse и т.д.)\n• Знаменитости\n• Защищённые бренды\n• Запрещённый контент\n\nПопробуйте переформулировать запрос.",
        "en": "❌ Request blocked by safety system.\n\nPossible reasons:\n• Famous characters (Tom and Jerry, Mickey Mouse, etc.)\n• Celebrities\n• Protected brands\n• Prohibited content\n\nTry rephrasing your request.",
        "kk": "❌ Сұраныс қауіпсіздік жүйесімен бұғатталды.\n\nМүмкін себептер:\n• Танымал кейіпкерлер (Том мен Джерри, Микки Маус және т.б.)\n• Атақты тұлғалар\n• Қорғалған брендтер\n• Тыйым салынған контент\n\nСұранысты қайта тұжырымдап көріңіз.",
        "tr": "❌ İstek güvenlik sistemi tarafından engellendi.\n\nOlası nedenler:\n• Ünlü karakterler (Tom ve Jerry, Mickey Mouse vb.)\n• Ünlüler\n• Korunan markalar\n• Yasaklı içerik\n\nİsteğinizi yeniden ifade etmeyi deneyin.",
        "uk": "❌ Запит заблоковано системою безпеки.\n\nМожливі причини:\n• Відомі персонажі (Том і Джеррі, Міккі Маус тощо)\n• Знаменитості\n• Захищені бренди\n• Заборонений контент\n\nСпробуйте переформулювати запит.",
        "fr": "❌ Requête bloquée par le système de sécurité.\n\nRaisons possibles:\n• Personnages célèbres (Tom et Jerry, Mickey Mouse, etc.)\n• Célébrités\n• Marques protégées\n• Contenu interdit\n\nEssayez de reformuler votre demande."
    },
    
    # Тексты поддержки
    "support_start": {
        "ru": "💬 Поддержка\n\nОпиши свою проблему или вопрос в одном сообщении.\n\nАдмины ответят как можно скорее.\n\n⚠️ Принимаются только текстовые сообщения",
        "en": "💬 Support\n\nDescribe your problem or question in one message.\n\nAdmins will reply as soon as possible.\n\n⚠️ Only text messages are accepted",
        "kk": "💬 Қолдау\n\nМәселеңізді немесе сұрағыңызды бір хабарламада сипаттаңыз.\n\nӘкімшілер мүмкіндігінше тезірек жауап береді.\n\n⚠️ Тек мәтіндік хабарламалар қабылданады",
        "tr": "💬 Destek\n\nSorununuzu veya sorunuzu tek bir mesajda açıklayın.\n\nYöneticiler en kısa sürede cevap verecektir.\n\n⚠️ Sadece metin mesajları kabul edilir",
        "uk": "💬 Підтримка\n\nОпиши свою проблему або питання в одному повідомленні.\n\nАдміни дадуть відповідь якнайшвидше.\n\n⚠️ Приймаються тільки текстові повідомлення",
        "fr": "💬 Support\n\nDécris ton problème ou ta question en un seul message.\n\nLes administrateurs répondront dès que possible.\n\n⚠️ Seuls les messages texte sont acceptés"
    },
    "support_blocked": {
        "ru": "⛔ Доступ в поддержку заблокирован.\nОсталось: {hours}ч {minutes}мин\n\nЧат с ИИ и другие функции работают.",
        "en": "⛔ Support access is blocked.\nRemaining: {hours}h {minutes}min\n\nAI chat and other functions work.",
        "kk": "⛔ Қолдауға кіру бұғатталды.\nҚалды: {hours}с {minutes}мин\n\nAI чат және басқа функциялар жұмыс істейді.",
        "tr": "⛔ Destek erişimi engellendi.\nKalan: {hours}s {minutes}dk\n\nYZ sohbet ve diğer işlevler çalışıyor.",
        "uk": "⛔ Доступ у підтримку заблоковано.\nЗалишилось: {hours}г {minutes}хв\n\nЧат з ШІ та інші функції працюють.",
        "fr": "⛔ L'accès au support est bloqué.\nRestant: {hours}h {minutes}min\n\nLe chat IA et les autres fonctions fonctionnent."
    },
    "support_you_blocked": {
        "ru": "⛔ Вы заблокированы в поддержке.\nОсталось: {hours}ч {minutes}мин",
        "en": "⛔ You are blocked from support.\nRemaining: {hours}h {minutes}min",
        "kk": "⛔ Сіз қолдаудан бұғатталдыңыз.\nҚалды: {hours}с {minutes}мин",
        "tr": "⛔ Destekten engellendiniz.\nKalan: {hours}s {minutes}dk",
        "uk": "⛔ Вас заблоковано в підтримці.\nЗалишилось: {hours}г {minutes}хв",
        "fr": "⛔ Vous êtes bloqué du support.\nRestant: {hours}h {minutes}min"
    },
    "support_unavailable": {
        "ru": "❌ Служба поддержки временно недоступна",
        "en": "❌ Support service is temporarily unavailable",
        "kk": "❌ Қолдау қызметі уақытша қолжетімсіз",
        "tr": "❌ Destek hizmeti geçici olarak kullanılamıyor",
        "uk": "❌ Служба підтримки тимчасово недоступна",
        "fr": "❌ Le service de support est temporairement indisponible"
    },
    "support_text_only": {
        "ru": "❌ В поддержку можно отправлять только текстовые сообщения.",
        "en": "❌ Only text messages can be sent to support.",
        "kk": "❌ Қолдауға тек мәтіндік хабарламаларды жіберуге болады.",
        "tr": "❌ Desteğe yalnızca metin mesajları gönderilebilir.",
        "uk": "❌ У підтримку можна відправляти тільки текстові повідомлення.",
        "fr": "❌ Seuls les messages texte peuvent être envoyés au support."
    },
    "support_sent": {
        "ru": "✅ Сообщение отправлено в поддержку.\nОжидайте ответа.",
        "en": "✅ Message sent to support.\nWait for a response.",
        "kk": "✅ Хабарлама қолдауға жіберілді.\nЖауап күтіңіз.",
        "tr": "✅ Mesaj desteğe gönderildi.\nYanıt bekleyin.",
        "uk": "✅ Повідомлення надіслано в підтримку.\nОчікуйте відповіді.",
        "fr": "✅ Message envoyé au support.\nAttends une réponse."
    },
    "support_error": {
        "ru": "❌ Ошибка при отправке. Попробуйте позже.",
        "en": "❌ Error sending. Try again later.",
        "kk": "❌ Жіберу кезінде қате. Кейінірек қайталаңыз.",
        "tr": "❌ Gönderme hatası. Daha sonra tekrar deneyin.",
        "uk": "❌ Помилка при відправленні. Спробуйте пізніше.",
        "fr": "❌ Erreur lors de l'envoi. Réessaie plus tard."
    },
    
    # НОВЫЙ КЛЮЧ - ОТВЕТ ОТ ПОДДЕРЖКИ
    "support_reply": {
        "ru": "📨 Ответ от поддержки:\n\n{reply}",
        "en": "📨 Reply from support:\n\n{reply}",
        "kk": "📨 Қолдаудан жауап:\n\n{reply}",
        "tr": "📨 Destekten yanıt:\n\n{reply}",
        "uk": "📨 Відповідь від підтримки:\n\n{reply}",
        "fr": "📨 Réponse du support:\n\n{reply}"
    },
    
    # ========== НОВЫЕ КЛЮЧИ ДЛЯ ПОМОЩИ ==========
    
    # Заголовок меню помощи
    "help_title": {
        "ru": "❓ ПОМОЩЬ\n\nВыбери раздел:",
        "en": "❓ HELP\n\nSelect a section:",
        "kk": "❓ КӨМЕК\n\nБөлімді таңдаңыз:",
        "tr": "❓ YARDIM\n\nBir bölüm seçin:",
        "uk": "❓ ДОПОМОГА\n\nОберіть розділ:",
        "fr": "❓ AIDE\n\nChoisis une section:"
    },
    
    # Кнопки разделов помощи
    "help_chat_btn": {
        "ru": "💬 Чат с ИИ",
        "en": "💬 AI Chat",
        "kk": "💬 AI чат",
        "tr": "💬 YZ Sohbet",
        "uk": "💬 Чат з ШІ",
        "fr": "💬 Chat IA"
    },
    "help_image_btn": {
        "ru": "🖼 Генерация картинки",
        "en": "🖼 Image generation",
        "kk": "🖼 Сурет генерациялау",
        "tr": "🖼 Görsel oluşturma",
        "uk": "🖼 Генерація зображення",
        "fr": "🖼 Génération d'image"
    },
    "help_fast_mode_btn": {
        "ru": "🚀 Быстрый режим",
        "en": "🚀 Fast mode",
        "kk": "🚀 Жылдам режим",
        "tr": "🚀 Hızlı mod",
        "uk": "🚀 Швидкий режим",
        "fr": "🚀 Mode rapide"
    },
    "help_quality_mode_btn": {
        "ru": "💎 Качественный режим",
        "en": "💎 Quality mode",
        "kk": "💎 Сапалы режим",
        "tr": "💎 Kaliteli mod",
        "uk": "💎 Якісний режим",
        "fr": "💎 Mode qualité"
    },
    "help_personas_btn": {
        "ru": "🎭 Характеры",
        "en": "🎭 Personalities",
        "kk": "🎭 Мінездер",
        "tr": "🎭 Karakterler",
        "uk": "🎭 Характери",
        "fr": "🎭 Personnalités"
    },
    "help_styles_btn": {
        "ru": "📝 Стили ответов",
        "en": "📝 Response styles",
        "kk": "📝 Жауап стильдері",
        "tr": "📝 Yanıt stilleri",
        "uk": "📝 Стилі відповідей",
        "fr": "📝 Styles de réponse"
    },
    "help_stars_btn": {
        "ru": "⭐ Звезды и баланс",
        "en": "⭐ Stars and balance",
        "kk": "⭐ Жұлдыздар және баланс",
        "tr": "⭐ Yıldızlar ve bakiye",
        "uk": "⭐ Зірки та баланс",
        "fr": "⭐ Étoiles et solde"
    },
    "help_referrals_btn": {
        "ru": "🎁 Рефералы",
        "en": "🎁 Referrals",
        "kk": "🎁 Рефералдар",
        "tr": "🎁 Referanslar",
        "uk": "🎁 Реферали",
        "fr": "🎁 Parrainages"
    },
    "help_modes_btn": {
        "ru": "📱 Режимы работы",
        "en": "📱 Work modes",
        "kk": "📱 Жұмыс режимдері",
        "tr": "📱 Çalışma modları",
        "uk": "📱 Режими роботи",
        "fr": "📱 Modes de travail"
    },
    
    # Тексты разделов помощи
    "help_chat_text": {
        "ru": "💬 ЧАТ С ИИ\n\nБот поддерживает два режима работы:\n• Быстрый режим — 0.3⭐ за сообщение\n• Качественный режим — 1⭐ за сообщение\n\nКак пользоваться:\n1. Выбери режим работы (Mini App или Встроенный)\n2. Нажми «💬 Чат с ИИ»\n3. Напиши сообщение — бот ответит\n4. После ответа нажми «⬅️ Назад» для выхода\n\nОсобенности:\n• Помнит историю диалога (до 100 сообщений)\n• Можно менять характер и стиль ответа\n• История сохраняется в памяти бота",
        "en": "💬 AI CHAT\n\nThe bot supports two modes:\n• Fast mode — 0.3⭐ per message\n• Quality mode — 1⭐ per message\n\nHow to use:\n1. Choose work mode (Mini App or Inline)\n2. Click «💬 AI Chat»\n3. Write a message — bot will reply\n4. After reply click «⬅️ Back» to exit\n\nFeatures:\n• Remembers chat history (up to 100 messages)\n• Can change personality and response style\n• History is saved in bot memory",
        "kk": "💬 AI ЧАТ\n\nБот екі режимді қолдайды:\n• Жылдам режим — 0.3⭐ хабарламаға\n• Сапалы режим — 1⭐ хабарламаға\n\nҚалай пайдалану:\n1. Жұмыс режимін таңдаңыз (Mini App немесе Кіріктірілген)\n2. «💬 AI Чат» батырмасын басыңыз\n3. Хабарлама жазыңыз — бот жауап береді\n4. Жауаптан кейін шығу үшін «⬅️ Артқа» басыңыз\n\nЕрекшеліктер:\n• Чат тарихын есте сақтайды (100 хабарламаға дейін)\n• Мінез бен жауап стилін өзгертуге болады\n• Тарих бот жадында сақталады",
        "tr": "💬 YZ SOHBET\n\nBot iki modu destekler:\n• Hızlı mod — mesaj başına 0.3⭐\n• Kaliteli mod — mesaj başına 1⭐\n\nNasıl kullanılır:\n1. Çalışma modunu seçin (Mini App veya Yerleşik)\n2. «💬 YZ Sohbet» düğmesine tıklayın\n3. Bir mesaj yazın — bot yanıt verecek\n4. Yanıttan sonra çıkmak için «⬅️ Geri» tıklayın\n\nÖzellikler:\n• Sohbet geçmişini hatırlar (100 mesaja kadar)\n• Karakter ve yanıt stili değiştirilebilir\n• Geçmiş bot hafızasında saklanır",
        "uk": "💬 ЧАТ З ШІ\n\nБот підтримує два режими:\n• Швидкий режим — 0.3⭐ за повідомлення\n• Якісний режим — 1⭐ за повідомлення\n\nЯк користуватися:\n1. Виберіть режим роботи (Mini App або Вбудований)\n2. Натисніть «💬 Чат з ШІ»\n3. Напишіть повідомлення — бот відповість\n4. Після відповіді натисніть «⬅️ Назад» для виходу\n\nОсобливості:\n• Пам'ятає історію діалогу (до 100 повідомлень)\n• Можна змінювати характер і стиль відповіді\n• Історія зберігається в пам'яті бота",
        "fr": "💬 CHAT IA\n\nLe bot prend en charge deux modes:\n• Mode rapide — 0.3⭐ par message\n• Mode qualité — 1⭐ par message\n\nComment utiliser:\n1. Choisis le mode de travail (Mini App ou Intégré)\n2. Clique sur «💬 Chat IA»\n3. Écris un message — le bot répondra\n4. Après la réponse, clique sur «⬅️ Retour» pour sortir\n\nCaractéristiques:\n• Se souvient de l'historique des messages (jusqu'à 100 messages)\n• Peut changer la personnalité et le style de réponse\n• L'historique est sauvegardé dans la mémoire du bot"
    },
    "help_image_text": {
        "ru": "🎨 ГЕНЕРАЦИЯ КАРТИНКИ\n\nСтоимость: 10⭐ за одну картинку\n\nКак пользоваться:\n1. Выбери режим работы (Mini App или Встроенный)\n2. Нажми «🖼 Генерация картинки»\n3. Введи описание того, что хочешь увидеть\n4. Нажми «Сгенерировать»\n5. После генерации можно сохранить в бота или повторить\n\nСоветы для хорошего промпта:\n• Пиши подробно: «красивый закат в горах, розовое небо, снежные вершины»\n• Добавляй стили: «в стиле аниме», «фотореалистично», «акварель»\n• Указывай детали: «котик в очках читает книгу»\n\nРезультат отправляется в Telegram бота, чтобы сохранить в галерею.",
        "en": "🎨 IMAGE GENERATION\n\nCost: 10⭐ per image\n\nHow to use:\n1. Choose work mode (Mini App or Inline)\n2. Click «🖼 Image generation»\n3. Enter a description of what you want to see\n4. Click «Generate»\n5. After generation, you can save to bot or repeat\n\nTips for a good prompt:\n• Be detailed: «beautiful sunset in mountains, pink sky, snow peaks»\n• Add styles: «anime style», «photorealistic», «watercolor»\n• Specify details: «cat in glasses reading a book»\n\nThe result is sent to Telegram bot to save to gallery.",
        "kk": "🎨 СУРЕТ ГЕНЕРАЦИЯСЫ\n\nҚұны: 10⭐ бір суретке\n\nҚалай пайдалану:\n1. Жұмыс режимін таңдаңыз (Mini App немесе Кіріктірілген)\n2. «🖼 Сурет генерациялау» батырмасын басыңыз\n3. Көргіңіз келетін нәрсенің сипаттамасын енгізіңіз\n4. «Жасау» батырмасын басыңыз\n5. Жасалғаннан кейін ботқа сақтауға немесе қайталауға болады\n\nЖақсы промпт үшін кеңестер:\n• Егжей-тегжейлі жазыңыз: «тауларда әдемі күн бату, қызғылт аспан, қарлы шыңдар»\n• Стильдерді қосыңыз: «аниме стилінде», «фотореалистік», «акварель»\n• Детальдарды көрсетіңіз: «көзілдіріктегі мысық кітап оқиды»\n\nНәтиже Telegram ботына галереяда сақтау үшін жіберіледі.",
        "tr": "🎨 GÖRSEL OLUŞTURMA\n\nMaliyet: Görsel başına 10⭐\n\nNasıl kullanılır:\n1. Çalışma modunu seçin (Mini App veya Yerleşik)\n2. «🖼 Görsel oluşturma» düğmesine tıklayın\n3. Görmek istediğin şeyin açıklamasını girin\n4. «Oluştur» düğmesine tıklayın\n5. Oluşturulduktan sonra bota kaydedebilir veya tekrarlayabilirsin\n\nİyi bir komut için ipuçları:\n• Ayrıntılı yazın: «dağlarda güzel gün batımı, pembe gökyüzü, karlı zirveler»\n• Stiller ekleyin: «anime tarzında», «fotogerçekçi», «suluboya»\n• Detayları belirtin: «gözlüklü kedi kitap okuyor»\n\nSonuç, galeriye kaydetmek için Telegram botuna gönderilir.",
        "uk": "🎨 ГЕНЕРАЦІЯ ЗОБРАЖЕННЯ\n\nВартість: 10⭐ за одне зображення\n\nЯк користуватися:\n1. Виберіть режим роботи (Mini App або Вбудований)\n2. Натисніть «🖼 Генерація зображення»\n3. Введіть опис того, що хочете побачити\n4. Натисніть «Згенерувати»\n5. Після генерації можна зберегти в бота або повторити\n\nПоради для гарного промпту:\n• Пишіть детально: «красивий захід сонця в горах, рожеве небо, сніжні вершини»\n• Додавайте стилі: «в стилі аніме», «фотореалістично», «акварель»\n• Вказуйте деталі: «котик в окулярах читає книгу»\n\nРезультат надсилається в Telegram бота, щоб зберегти в галерею.",
        "fr": "🎨 GÉNÉRATION D'IMAGE\n\nCoût: 10⭐ par image\n\nComment utiliser:\n1. Choisis le mode de travail (Mini App ou Intégré)\n2. Clique sur «🖼 Génération d'image»\n3. Saisis une description de ce que tu veux voir\n4. Clique sur «Générer»\n5. Après génération, tu peux enregistrer dans le bot ou répéter\n\nConseils pour un bon prompt:\n• Sois détaillé: «beau coucher de soleil dans les montagnes, ciel rose, sommets enneigés»\n• Ajoute des styles: «style anime», «photorealistic», «aquarelle»\n• Spécifie les détails: «chat aux lunettes lisant un livre»\n\nLe résultat est envoyé au bot Telegram pour être sauvegardé dans la galerie."
    },
    "help_fast_mode_text": {
        "ru": "⚡ БЫСТРЫЙ РЕЖИМ\n\nСтоимость: 0.3⭐ за сообщение\n\nВозможности:\n• ✅ Можно менять характер (Общительный, Весёлый, Умный, Строгий)\n• ✅ Можно менять стиль ответа (Коротко, По шагам, Подробно)\n• ✅ Можно выбирать язык ответов ИИ\n• ✅ Очень быстрые ответы (1-3 секунды)\n• ✅ Лимит изменений: 5 смен характера в день, 5 смен стиля в день\n\nДля кого подходит:\n• Тем, кто ценит скорость\n• Кому важно менять характер и стиль общения\n• Для повседневных вопросов и диалогов",
        "en": "⚡ FAST MODE\n\nCost: 0.3⭐ per message\n\nFeatures:\n• ✅ Change personality (Friendly, Fun, Smart, Strict)\n• ✅ Change response style (Short, Step by step, Detailed)\n• ✅ Choose AI response language\n• ✅ Very fast responses (1-3 seconds)\n• ✅ Change limits: 5 personality changes per day, 5 style changes per day\n\nWho it's for:\n• Those who value speed\n• Those who want to change personality and communication style\n• For everyday questions and conversations",
        "kk": "⚡ ЖЫЛДАМ РЕЖИМ\n\nҚұны: 0.3⭐ хабарламаға\n\nМүмкіндіктер:\n• ✅ Мінезді өзгертуге болады (Көпшіл, Көңілді, Ақылды, Қатал)\n• ✅ Жауап стилін өзгертуге болады (Қысқа, Қадамдық, Егжей-тегжейлі)\n• ✅ AI жауап тілін таңдауға болады\n• ✅ Өте жылдам жауаптар (1-3 секунд)\n• ✅ Өзгерту лимиті: күніне 5 мінез өзгерту, 5 стиль өзгерту\n\nКімге жараса:\n• Жылдамдықты бағалайтындарға\n• Мінез бен қарым-қатынас стилін өзгерту маңыздыларға\n• Күнделікті сұрақтар мен диалогтар үшін",
        "tr": "⚡ HIZLI MOD\n\nMaliyet: mesaj başına 0.3⭐\n\nÖzellikler:\n• ✅ Karakter değiştirilebilir (Arkadaş canlısı, Eğlenceli, Zeki, Sert)\n• ✅ Yanıt stili değiştirilebilir (Kısa, Adım adım, Detaylı)\n• ✅ YZ yanıt dili seçilebilir\n• ✅ Çok hızlı yanıtlar (1-3 saniye)\n• ✅ Değişim limitleri: günde 5 karakter değişimi, 5 stil değişimi\n\nKimler için uygun:\n• Hızı önemseyenler için\n• Karakter ve iletişim stilini değiştirmek isteyenler için\n• Günlük sorular ve sohbetler için",
        "uk": "⚡ ШВИДКИЙ РЕЖИМ\n\nВартість: 0.3⭐ за повідомлення\n\nМожливості:\n• ✅ Можна міняти характер (Товариський, Веселий, Розумний, Суворий)\n• ✅ Можна міняти стиль відповіді (Коротко, По кроках, Детально)\n• ✅ Можна вибирати мову відповідей ШІ\n• ✅ Дуже швидкі відповіді (1-3 секунди)\n• ✅ Ліміт змін: 5 змін характеру на день, 5 змін стилю на день\n\nДля кого підходить:\n• Для тих, хто цінує швидкість\n• Кому важливо міняти характер і стиль спілкування\n• Для повсякденних питань і діалогів",
        "fr": "⚡ MODE RAPIDE\n\nCoût: 0.3⭐ par message\n\nFonctionnalités:\n• ✅ Changer la personnalité (Amical, Drôle, Intelligent, Strict)\n• ✅ Changer le style de réponse (Court, Pas à pas, Détaillé)\n• ✅ Choisir la langue de réponse IA\n• ✅ Réponses très rapides (1-3 secondes)\n• ✅ Limites de changement: 5 changements de personnalité par jour, 5 changements de style par jour\n\nPour qui:\n• Ceux qui apprécient la rapidité\n• Ceux qui veulent changer de personnalité et de style de communication\n• Pour les questions quotidiennes et les conversations"
    },
    "help_quality_mode_text": {
        "ru": "💎 КАЧЕСТВЕННЫЙ РЕЖИМ\n\nСтоимость: 1⭐ за сообщение\n\nВозможности:\n• ✅ Более глубокие и продуманные ответы\n• ✅ Можно менять стиль ответа (Коротко, По шагам, Подробно)\n• ✅ Поддерживает множество языков\n• ✅ Лимит изменений стиля: 7 смен в день\n\nДля кого подходит:\n• Для сложных вопросов и развернутых ответов\n• Когда важна глубина и качество текста\n• Для творческих задач и анализа",
        "en": "💎 QUALITY MODE\n\nCost: 1⭐ per message\n\nFeatures:\n• ✅ Deeper and more thoughtful responses\n• ✅ Change response style (Short, Step by step, Detailed)\n• ✅ Supports many languages\n• ✅ Style change limit: 7 changes per day\n\nWho it's for:\n• For complex questions and detailed answers\n• When depth and text quality matter\n• For creative tasks and analysis",
        "kk": "💎 САПАЛЫ РЕЖИМ\n\nҚұны: 1⭐ хабарламаға\n\nМүмкіндіктер:\n• ✅ Тереңірек және ойластырылған жауаптар\n• ✅ Жауап стилін өзгертуге болады (Қысқа, Қадамдық, Егжей-тегжейлі)\n• ✅ Көптеген тілдерді қолдайды\n• ✅ Стиль өзгерту лимиті: күніне 7 өзгерту\n\nКімге жараса:\n• Күрделі сұрақтар мен толық жауаптар үшін\n• Мәтіннің тереңдігі мен сапасы маңызды болғанда\n• Шығармашылық тапсырмалар мен талдау үшін",
        "tr": "💎 KALİTELİ MOD\n\nMaliyet: mesaj başına 1⭐\n\nÖzellikler:\n• ✅ Daha derin ve düşünceli yanıtlar\n• ✅ Yanıt stili değiştirilebilir (Kısa, Adım adım, Detaylı)\n• ✅ Birçok dili destekler\n• ✅ Stil değişim limiti: günde 7 değişim\n\nKimler için uygun:\n• Karmaşık sorular ve detaylı cevaplar için\n• Metin derinliği ve kalitesi önemli olduğunda\n• Yaratıcı görevler ve analiz için",
        "uk": "💎 ЯКІСНИЙ РЕЖИМ\n\nВартість: 1⭐ за повідомлення\n\nМожливості:\n• ✅ Глибші та продуманіші відповіді\n• ✅ Можна міняти стиль відповіді (Коротко, По кроках, Детально)\n• ✅ Підтримує багато мов\n• ✅ Ліміт змін стилю: 7 змін на день\n\nДля кого підходить:\n• Для складних питань і розгорнутих відповідей\n• Коли важлива глибина та якість тексту\n• Для творчих завдань та аналізу",
        "fr": "💎 MODE QUALITÉ\n\nCoût: 1⭐ par message\n\nFonctionnalités:\n• ✅ Réponses plus profondes et réfléchies\n• ✅ Changer le style de réponse (Court, Pas à pas, Détaillé)\n• ✅ Supporte de nombreuses langues\n• ✅ Limite de changement de style: 7 changements par jour\n\nPour qui:\n• Pour les questions complexes et les réponses détaillées\n• Quand la profondeur et la qualité du texte comptent\n• Pour les tâches créatives et l'analyse"
    },
    "help_personas_text": {
        "ru": "🎭 ХАРАКТЕРЫ (доступны в Быстром режиме)\n\n😊 Общительный\n• Дружелюбный и тёплый стиль общения\n• Использует эмодзи\n• Поддерживает диалог, задаёт вопросы\n• Идеален для обычного общения\n\n😂 Весёлый\n• Легкий, юмористический тон\n• Шутит, использует иронию\n• Поднимает настроение\n• Хорош для непринуждённой беседы\n\n🧐 Умный\n• Экспертный, аналитический стиль\n• Объясняет сложное простыми словами\n• Приводит примеры и факты\n• Подходит для обучения и разбора тем\n\n😐 Строгий\n• По делу, без лишних слов\n• Чёткие и короткие ответы\n• Только полезная информация\n• Для тех, кто ценит лаконичность\n\nЛимит: 5 изменений характера в день",
        "en": "🎭 PERSONALITIES (available in Fast mode)\n\n😊 Friendly\n• Friendly and warm communication style\n• Uses emojis\n• Engages in dialogue, asks questions\n• Ideal for everyday conversation\n\n😂 Fun\n• Light, humorous tone\n• Jokes, uses irony\n• Lifts the mood\n• Great for casual conversation\n\n🧐 Smart\n• Expert, analytical style\n• Explains complex things simply\n• Gives examples and facts\n• Suitable for learning and topic analysis\n\n😐 Strict\n• To the point, no unnecessary words\n• Clear and short answers\n• Only useful information\n• For those who value brevity\n\nLimit: 5 personality changes per day",
        "kk": "🎭 МІНЕЗДЕР (Жылдам режимде қолжетімді)\n\n😊 Көпшіл\n• Достық және жылы сөйлесу стилі\n• Эмодзи қолданады\n• Диалогты қолдайды, сұрақтар қояды\n• Кәдімгі сөйлесу үшін өте қолайлы\n\n😂 Көңілді\n• Жеңіл, әзіл-оспақ тон\n• Әзілдейді, ирония қолданады\n• Көңіл-күйді көтереді\n• Еркін әңгіме үшін жақсы\n\n🧐 Ақылды\n• Сараптамалық, аналитикалық стиль\n• Күрделі нәрселерді қарапайым тілмен түсіндіреді\n• Мысалдар мен фактілер келтіреді\n• Оқу және тақырыптарды талдау үшін қолайлы\n\n😐 Қатал\n• Іске, қосымша сөздерсіз\n• Нақты және қысқа жауаптар\n• Тек пайдалы ақпарат\n• Қысқалықты бағалайтындар үшін\n\nЛимит: күніне 5 мінез өзгерту",
        "tr": "🎭 KARAKTERLER (Hızlı modda mevcuttur)\n\n😊 Arkadaş canlısı\n• Samimi ve sıcak iletişim tarzı\n• Emoji kullanır\n• Diyaloğu destekler, sorular sorar\n• Günlük sohbet için ideal\n\n😂 Eğlenceli\n• Hafif, esprili ton\n• Şakalar yapar, ironi kullanır\n• Moral yükseltir\n• Rahat sohbetler için harika\n\n🧐 Zeki\n• Uzman, analitik stil\n• Karmaşık şeyleri basitçe açıklar\n• Örnekler ve gerçekler sunar\n• Öğrenme ve konu analizi için uygundur\n\n😐 Sert\n• Konuya doğrudan, gereksiz kelime yok\n• Net ve kısa cevaplar\n• Sadece faydalı bilgiler\n• Kısa ve öz olanı sevenler için\n\nLimit: Günde 5 karakter değişikliği",
        "uk": "🎭 ХАРАКТЕРИ (доступні в Швидкому режимі)\n\n😊 Товариський\n• Дружній і теплий стиль спілкування\n• Використовує емодзі\n• Підтримує діалог, задає питання\n• Ідеальний для звичайного спілкування\n\n😂 Веселий\n• Легкий, гумористичний тон\n• Жартує, використовує іронію\n• Піднімає настрій\n• Добре підходить для невимушеної бесіди\n\n🧐 Розумний\n• Експертний, аналітичний стиль\n• Пояснює складне простими словами\n• Наводить приклади та факти\n• Підходить для навчання та розбору тем\n\n😐 Суворий\n• По суті, без зайвих слів\n• Чіткі та короткі відповіді\n• Тільки корисна інформація\n• Для тих, хто цінує лаконічність\n\nЛіміт: 5 змін характеру на день",
        "fr": "🎭 PERSONNALITÉS (disponibles en mode Rapide)\n\n😊 Amical\n• Style de communication amical et chaleureux\n• Utilise des emojis\n• Engage le dialogue, pose des questions\n• Idéal pour la conversation quotidienne\n\n😂 Drôle\n• Ton léger et humoristique\n• Blague, utilise l'ironie\n• Remonte le moral\n• Parfait pour une conversation décontractée\n\n🧐 Intelligent\n• Style expert et analytique\n• Explique les choses complexes simplement\n• Donne des exemples et des faits\n• Adapté pour l'apprentissage et l'analyse de sujets\n\n😐 Strict\n• Va droit au but, pas de mots inutiles\n• Réponses claires et courtes\n• Seulement des informations utiles\n• Pour ceux qui apprécient la concision\n\nLimite: 5 changements de personnalité par jour"
    },
    "help_styles_text": {
        "ru": "📝 СТИЛИ ОТВЕТОВ\n\n📏 Коротко\n• 1-3 предложения\n• Только суть, без воды\n• Максимальная лаконичность\n• Подходит для быстрых ответов\n\n📋 По шагам\n• Структурированный ответ\n• Разбивка на пункты\n• Пошаговое объяснение\n• Идеально для инструкций и алгоритмов\n\n📚 Подробно\n• Развёрнутое объяснение\n• Примеры и детали\n• 3-5 предложений\n• Для глубокого понимания темы\n\nЛимит в Быстром режиме: 5 изменений в день\nЛимит в Качественном режиме: 7 изменений в день",
        "en": "📝 RESPONSE STYLES\n\n📏 Short\n• 1-3 sentences\n• Just the essence, no fluff\n• Maximum conciseness\n• Suitable for quick answers\n\n📋 Step by step\n• Structured response\n• Broken down into points\n• Step-by-step explanation\n• Perfect for instructions and algorithms\n\n📚 Detailed\n• Detailed explanation\n• Examples and details\n• 3-5 sentences\n• For deep understanding of the topic\n\nLimit in Fast mode: 5 changes per day\nLimit in Quality mode: 7 changes per day",
        "kk": "📝 ЖАУАП СТИЛЬДЕРІ\n\n📏 Қысқа\n• 1-3 сөйлем\n• Тек мәні, артық сөздерсіз\n• Максималды қысқалық\n• Жылдам жауаптар үшін қолайлы\n\n📋 Қадамдық\n• Құрылымдалған жауап\n• Пункттерге бөлінген\n• Қадамдық түсініктеме\n• Нұсқаулықтар мен алгоритмдер үшін өте қолайлы\n\n📚 Егжей-тегжейлі\n• Толық түсініктеме\n• Мысалдар мен детальдар\n• 3-5 сөйлем\n• Тақырыпты терең түсіну үшін\n\nЖылдам режимдегі лимит: күніне 5 өзгерту\nСапалы режимдегі лимит: күніне 7 өзгерту",
        "tr": "📝 YANIT STİLLERİ\n\n📏 Kısa\n• 1-3 cümle\n• Sadece öz, gereksiz kelime yok\n• Maksimum kısalık\n• Hızlı cevaplar için uygundur\n\n📋 Adım adım\n• Yapılandırılmış yanıt\n• Maddelere ayrılmış\n• Adım adım açıklama\n• Talimatlar ve algoritmalar için ideal\n\n📚 Detaylı\n• Ayrıntılı açıklama\n• Örnekler ve detaylar\n• 3-5 cümle\n• Konuyu derinlemesine anlamak için\n\nHızlı modda limit: günde 5 değişiklik\nKaliteli modda limit: günde 7 değişiklik",
        "uk": "📝 СТИЛІ ВІДПОВІДЕЙ\n\n📏 Коротко\n• 1-3 речення\n• Тільки суть, без води\n• Максимальна лаконічність\n• Підходить для швидких відповідей\n\n📋 По кроках\n• Структурована відповідь\n• Розбивка на пункти\n• Покрокове пояснення\n• Ідеально для інструкцій та алгоритмів\n\n📚 Детально\n• Розгорнуте пояснення\n• Приклади та деталі\n• 3-5 речень\n• Для глибокого розуміння теми\n\nЛіміт у Швидкому режимі: 5 змін на день\nЛіміт у Якісному режимі: 7 змін на день",
        "fr": "📝 STYLES DE RÉPONSE\n\n📏 Court\n• 1-3 phrases\n• Juste l'essentiel, sans superflu\n• Concision maximale\n• Adapté pour les réponses rapides\n\n📋 Pas à pas\n• Réponse structurée\n• Décomposée en points\n• Explication étape par étape\n• Parfait pour les instructions et les algorithmes\n\n📚 Détaillé\n• Explication détaillée\n• Exemples et détails\n• 3-5 phrases\n• Pour une compréhension approfondie du sujet\n\nLimite en mode Rapide: 5 changements par jour\nLimite en mode Qualité: 7 changements par jour"
    },
    "help_stars_text": {
        "ru": "⭐ ЗВЕЗДЫ И БАЛАНС\n\nЗа что списываются звезды:\n• Сообщение в Быстром режиме — 0.3⭐\n• Сообщение в Качественном режиме — 1⭐\n• Генерация картинки — 10⭐\n\nКак заработать звезды:\n• 🎁 Пригласи друга по реферальной ссылке — +10⭐\n• 💰 Пополнение через Telegram Stars (в разработке)\n\nГде посмотреть баланс:\n• В главном меню кнопка «⭐ Баланс: X звезд»\n• В профиле также отображается баланс\n\nВажно:\n• При недостатке звезд чат и генерация будут недоступны\n• Баланс обновляется автоматически после каждого действия",
        "en": "⭐ STARS AND BALANCE\n\nWhat stars are spent on:\n• Message in Fast mode — 0.3⭐\n• Message in Quality mode — 1⭐\n• Image generation — 10⭐\n\nHow to earn stars:\n• 🎁 Invite a friend via referral link — +10⭐\n• 💰 Top up via Telegram Stars (in development)\n\nWhere to check balance:\n• In main menu button «⭐ Balance: X stars»\n• Balance is also displayed in profile\n\nImportant:\n• If stars are insufficient, chat and generation will be unavailable\n• Balance updates automatically after each action",
        "kk": "⭐ ЖҰЛДЫЗДАР ЖӘНЕ БАЛАНС\n\nНеге жұлдыздар жұмсалады:\n• Жылдам режимдегі хабарлама — 0.3⭐\n• Сапалы режимдегі хабарлама — 1⭐\n• Сурет генерациялау — 10⭐\n\nЖұлдыздарды қалай табуға болады:\n• 🎁 Досыңызды рефералдық сілтеме арқылы шақырыңыз — +10⭐\n• 💰 Telegram Stars арқылы толтыру (әзірленуде)\n\nБалансты қайдан көруге болады:\n• Негізгі мәзірдегі «⭐ Баланс: {balance} жұлдыз» батырмасы\n• Профильде де баланс көрсетіледі\n\nМаңызды:\n• Жұлдыздар жеткіліксіз болса, чат және генерация қолжетімсіз болады\n• Баланс әр әрекеттен кейін автоматты түрде жаңартылады",
        "tr": "⭐ YILDIZLAR VE BAKİYE\n\nYıldızlar ne için harcanır:\n• Hızlı modda mesaj — 0.3⭐\n• Kaliteli modda mesaj — 1⭐\n• Görsel oluşturma — 10⭐\n\nYıldız nasıl kazanılır:\n• 🎁 Arkadaşını referans bağlantısıyla davet et — +10⭐\n• 💰 Telegram Stars ile yükleme (geliştiriliyor)\n\nBakiye nereden kontrol edilir:\n• Ana menüde «⭐ Bakiye: {balance} yıldız» düğmesi\n• Profilde de bakiye görüntülenir\n\nÖnemli:\n• Yıldızlar yetersizse sohbet ve oluşturma kullanılamaz\n• Bakiye her işlemden sonra otomatik güncellenir",
        "uk": "⭐ ЗІРКИ ТА БАЛАНС\n\nНа що витрачаються зірки:\n• Повідомлення в Швидкому режимі — 0.3⭐\n• Повідомлення в Якісному режимі — 1⭐\n• Генерація зображення — 10⭐\n\nЯк заробити зірки:\n• 🎁 Запроси друга за реферальним посиланням — +10⭐\n• 💰 Поповнення через Telegram Stars (в розробці)\n\nДе подивитися баланс:\n• У головному меню кнопка «⭐ Баланс: {balance} зірок»\n• У профілі також відображається баланс\n\nВажливо:\n• При недостачі зірок чат і генерація будуть недоступні\n• Баланс оновлюється автоматично після кожної дії",
        "fr": "⭐ ÉTOILES ET SOLDE\n\nÀ quoi servent les étoiles:\n• Message en mode Rapide — 0.3⭐\n• Message en mode Qualité — 1⭐\n• Génération d'image — 10⭐\n\nComment gagner des étoiles:\n• 🎁 Invite un ami avec un lien de parrainage — +10⭐\n• 💰 Recharge via Telegram Stars (en développement)\n\nOù vérifier le solde:\n• Dans le menu principal, bouton «⭐ Solde: {balance} étoiles»\n• Le solde est également affiché dans le profil\n\nImportant:\n• Si les étoiles sont insuffisantes, le chat et la génération seront indisponibles\n• Le solde se met à jour automatiquement après chaque action"
    },
    "help_referrals_text": {
        "ru": "🎁 РЕФЕРАЛЫ\n\nКак это работает:\n1. Перейди в раздел «🎁 Рефералы»\n2. Скопируй свою уникальную ссылку\n3. Отправь ссылку другу\n4. Когда друг впервые запустит бота по твоей ссылке — ты получишь 10⭐\n\nБонусы:\n• Пригласивший получает 10⭐ на баланс\n• Новый пользователь получает уведомление\n• Количество приглашённых не ограничено\n\nСтатистика:\n• В разделе «Рефералы» видно, сколько друзей пригласил\n• Также отображается общая сумма заработанных звезд",
        "en": "🎁 REFERRALS\n\nHow it works:\n1. Go to «🎁 Referrals» section\n2. Copy your unique link\n3. Send the link to a friend\n4. When a friend launches the bot for the first time via your link — you get 10⭐\n\nBonuses:\n• The inviter gets 10⭐ added to balance\n• The new user receives a notification\n• Number of invites is unlimited\n\nStatistics:\n• The «Referrals» section shows how many friends you've invited\n• Also shows the total amount of stars earned",
        "kk": "🎁 РЕФЕРАЛДАР\n\nҚалай жұмыс істейді:\n1. «🎁 Рефералдар» бөліміне өтіңіз\n2. Өзіңіздің бірегей сілтемеңізді көшіріңіз\n3. Сілтемені досыңызға жіберіңіз\n4. Досыңыз ботты сіздің сілтемеңіз арқылы алғаш рет іске қосқанда — сіз 10⭐ аласыз\n\nБонустар:\n• Шақырушы 10⭐ алады\n• Жаңа пайдаланушы хабарландыру алады\n• Шақырылғандар саны шектелмеген\n\nСтатистика:\n• «Рефералдар» бөлімінде қанша дос шақырғаныңызды көруге болады\n• Сондай-ақ табылған жұлдыздардың жалпы сомасы көрсетіледі",
        "tr": "🎁 REFERANSLAR\n\nNasıl çalışır:\n1. «🎁 Referanslar» bölümüne gidin\n2. Benzersiz bağlantınızı kopyalayın\n3. Bağlantıyı arkadaşınıza gönderin\n4. Arkadaşınız botu sizin bağlantınızla ilk kez başlattığında — 10⭐ kazanırsınız\n\nBonuslar:\n• Davet eden 10⭐ alır\n• Yeni kullanıcı bildirim alır\n• Davet edilen sayısı sınırsızdır\n\nİstatistikler:\n• «Referanslar» bölümünde kaç arkadaş davet ettiğinizi görebilirsiniz\n• Ayrıca kazanılan toplam yıldız miktarı gösterilir",
        "uk": "🎁 РЕФЕРАЛИ\n\nЯк це працює:\n1. Перейди в розділ «🎁 Реферали»\n2. Скопіюй своє унікальне посилання\n3. Надішли посилання другу\n4. Коли друг вперше запустить бота за твоїм посиланням — ти отримаєш 10⭐\n\nБонуси:\n• Той, хто запросив, отримує 10⭐ на баланс\n• Новий користувач отримує сповіщення\n• Кількість запрошених не обмежена\n\nСтатистика:\n• У розділі «Реферали» видно, скільки друзів ти запросив\n• Також відображається загальна сума зароблених зірок",
        "fr": "🎁 PARRAINAGES\n\nComment ça marche:\n1. Va dans la section «🎁 Parrainages»\n2. Copie ton lien unique\n3. Envoie le lien à un ami\n4. Quand ton ami lance le bot pour la première fois avec ton lien — tu reçois 10⭐\n\nBonus:\n• Le parrain reçoit 10⭐ sur son solde\n• Le nouvel utilisateur reçoit une notification\n• Le nombre d'invitations est illimité\n\nStatistiques:\n• La section «Parrainages» montre combien d'amis tu as invités\n• Affiche également le montant total des étoiles gagnées"
    },
    "help_modes_text": {
        "ru": "📱 РЕЖИМЫ РАБОТЫ\n\n📱 Mini App (Telegram Web App)\n• Открывается внутри Telegram\n• Полноэкранный интерфейс\n• Удобный чат с историей\n• Генерация картинок\n• Все настройки в интерфейсе\n\n💬 Встроенный режим\n• Общение через Telegram чат\n• Кнопки и меню в сообщениях\n• Настройки через кнопки\n• Требует интернет-соединения\n\nКак переключить:\n1. Зайди в «⚙️ Настройки»\n2. Нажми «🔄 Режим работы»\n3. Выбери удобный вариант\n\nОба режима используют один баланс звезд и общую историю чата.",
        "en": "📱 WORK MODES\n\n📱 Mini App (Telegram Web App)\n• Opens inside Telegram\n• Full-screen interface\n• Convenient chat with history\n• Image generation\n• All settings in the interface\n\n💬 Inline mode\n• Communication via Telegram chat\n• Buttons and menu in messages\n• Settings via buttons\n• Requires internet connection\n\nHow to switch:\n1. Go to «⚙️ Settings»\n2. Click «🔄 Work mode»\n3. Choose the convenient option\n\nBoth modes use the same star balance and shared chat history.",
        "kk": "📱 ЖҰМЫС РЕЖИМДЕРІ\n\n📱 Mini App (Telegram Web App)\n• Telegram ішінде ашылады\n• Толық экранды интерфейс\n• Тарихы бар ыңғайлы чат\n• Сурет генерациялау\n• Барлық баптаулар интерфейсте\n\n💬 Кіріктірілген режим\n• Telegram чат арқылы қарым-қатынас\n• Хабарламалардағы батырмалар мен мәзір\n• Баптаулар батырмалар арқылы\n• Интернет байланысын қажет етеді\n\nҚалай ауыстыру:\n1. «⚙️ Баптаулар» бөліміне өтіңіз\n2. «🔄 Жұмыс режимі» батырмасын басыңыз\n3. Ыңғайлы нұсқаны таңдаңыз\n\nЕкі режим де бір жұлдыз балансын және ортақ чат тарихын пайдаланады.",
        "tr": "📱 ÇALIŞMA MODLARI\n\n📱 Mini App (Telegram Web App)\n• Telegram içinde açılır\n• Tam ekran arayüz\n• Geçmişli kullanışlı sohbet\n• Görsel oluşturma\n• Tüm ayarlar arayüzde\n\n💬 Yerleşik mod\n• Telegram sohbeti üzerinden iletişim\n• Mesajlardaki butonlar ve menü\n• Ayarlar butonlar aracılığıyla\n• İnternet bağlantısı gerektirir\n\nNasıl değiştirilir:\n1. «⚙️ Ayarlar» bölümüne gidin\n2. «🔄 Çalışma modu» düğmesine tıklayın\n3. Uygun seçeneği seçin\n\nHer iki mod da aynı yıldız bakiyesini ve ortak sohbet geçmişini kullanır.",
        "uk": "📱 РЕЖИМИ РОБОТИ\n\n📱 Mini App (Telegram Web App)\n• Відкривається всередині Telegram\n• Повноекранний інтерфейс\n• Зручний чат з історією\n• Генерація зображень\n• Всі налаштування в інтерфейсі\n\n💬 Вбудований режим\n• Спілкування через Telegram чат\n• Кнопки та меню в повідомленнях\n• Налаштування через кнопки\n• Потребує інтернет-з'єднання\n\nЯк переключити:\n1. Зайди в «⚙️ Налаштування»\n2. Натисни «🔄 Режим роботи»\n3. Обери зручний варіант\n\nОбидва режими використовують один баланс зірок і спільну історію чату.",
        "fr": "📱 MODES DE TRAVAIL\n\n📱 Mini App (Telegram Web App)\n• S'ouvre dans Telegram\n• Interface plein écran\n• Chat pratique avec historique\n• Génération d'images\n• Tous les paramètres dans l'interface\n\n💬 Mode intégré\n• Communication via le chat Telegram\n• Boutons et menu dans les messages\n• Paramètres via boutons\n• Nécessite une connexion internet\n\nComment changer:\n1. Va dans «⚙️ Paramètres»\n2. Clique sur «🔄 Mode de travail»\n3. Choisis l'option pratique\n\nLes deux modes utilisent le même solde d'étoiles et l'historique de chat commun."
    }
}

# =========================
# ХАРАКТЕРЫ
# =========================
PERSONAS = {
    "friendly": {
        "ru": "😊 Общительный",
        "en": "😊 Friendly",
        "kk": "😊 Көпшіл",
        "tr": "😊 Arkadaş canlısı",
        "uk": "😊 Товариський",
        "fr": "😊 Amical"
    },
    "fun": {
        "ru": "😂 Весёлый",
        "en": "😂 Fun",
        "kk": "😂 Көңілді",
        "tr": "😂 Eğlenceli",
        "uk": "😂 Веселий",
        "fr": "😂 Drôle"
    },
    "smart": {
        "ru": "🧐 Умный",
        "en": "🧐 Smart",
        "kk": "🧐 Ақылды",
        "tr": "🧐 Zeki",
        "uk": "🧐 Розумний",
        "fr": "🧐 Intelligent"
    },
    "strict": {
        "ru": "😐 Строгий",
        "en": "😐 Strict",
        "kk": "😐 Қатал",
        "tr": "😐 Sert",
        "uk": "😐 Суворий",
        "fr": "😐 Strict"
    }
}

# =========================
# СТИЛИ
# =========================
STYLES = {
    "short": {
        "ru": "📏 Коротко",
        "en": "📏 Short",
        "kk": "📏 Қысқа",
        "tr": "📏 Kısa",
        "uk": "📏 Коротко",
        "fr": "📏 Court"
    },
    "steps": {
        "ru": "📋 По шагам",
        "en": "📋 Step by step",
        "kk": "📋 Қадамдық",
        "tr": "📋 Adım adım",
        "uk": "📋 По кроках",
        "fr": "📋 Pas à pas"
    },
    "detail": {
        "ru": "📚 Подробно",
        "en": "📚 Detailed",
        "kk": "📚 Егжей-тегжейлі",
        "tr": "📚 Detaylı",
        "uk": "📚 Детально",
        "fr": "📚 Détaillé"
    }
}

# =========================
# РЕЖИМЫ ИИ
# =========================
AI_MODES = {
    "fast": {
        "ru": "🚀 Быстрый",
        "en": "🚀 Fast",
        "kk": "🚀 Жылдам",
        "tr": "🚀 Hızlı",
        "uk": "🚀 Швидкий",
        "fr": "🚀 Rapide"
    },
    "quality": {
        "ru": "💎 Качественный",
        "en": "💎 Quality",
        "kk": "💎 Сапалы",
        "tr": "💎 Kaliteli",
        "uk": "💎 Якісний",
        "fr": "💎 Qualité"
    }
}

# =========================
# РЕЖИМЫ РАБОТЫ
# =========================
WORK_MODES = {
    "miniapp": {
        "ru": "📱 Mini App",
        "en": "📱 Mini App",
        "kk": "📱 Mini App",
        "tr": "📱 Mini App",
        "uk": "📱 Mini App",
        "fr": "📱 Mini App"
    },
    "inline": {
        "ru": "💬 Встроенный",
        "en": "💬 Inline",
        "kk": "💬 Кіріктірілген",
        "tr": "💬 Yerleşik",
        "uk": "💬 Вбудований",
        "fr": "💬 Intégré"
    }
}

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def get_user_language(user_id: int) -> str:
    """Получить язык пользователя"""
    from api import get_user_lang
    return get_user_lang(user_id) or "ru"

def get_text(user_id: int, key: str, **kwargs) -> str:
    """Получить текст на языке пользователя"""
    lang = get_user_language(user_id)
    text_dict = TEXTS.get(key, {})
    text = text_dict.get(lang, text_dict.get("ru", key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

def get_button_text(user_id: int, key: str, **kwargs) -> str:
    """Получить текст кнопки"""
    return get_text(user_id, key, **kwargs)

def get_persona_name(user_id: int, persona_id: str) -> str:
    """Получить название характера на языке пользователя"""
    lang = get_user_language(user_id)
    persona = PERSONAS.get(persona_id, {})
    return persona.get(lang, persona.get("ru", persona_id))

def get_style_name(user_id: int, style_id: str) -> str:
    """Получить название стиля на языке пользователя"""
    lang = get_user_language(user_id)
    style = STYLES.get(style_id, {})
    return style.get(lang, style.get("ru", style_id))

def get_mode_name(user_id: int, mode_id: str) -> str:
    """Получить название режима ИИ на языке пользователя"""
    lang = get_user_language(user_id)
    mode = AI_MODES.get(mode_id, {})
    return mode.get(lang, mode.get("ru", mode_id))

def get_ai_mode_name(user_id: int, mode_id: str) -> str:
    """Алиас для get_mode_name"""
    return get_mode_name(user_id, mode_id)

def get_work_mode_name(user_id: int, mode_id: str) -> str:
    """Получить название режима работы на языке пользователя"""
    lang = get_user_language(user_id)
    mode = WORK_MODES.get(mode_id, {})
    return mode.get(lang, mode.get("ru", mode_id))

def get_lang_name(user_id: int, lang_code: str) -> str:
    """Получить название языка"""
    return LANGUAGES.get(lang_code, lang_code)