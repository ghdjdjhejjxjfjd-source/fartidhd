# bot/locales.py
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

# Основные тексты
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
    
    # Текст профиля
    "profile_template": {
        "ru": "        👤 ПРОФИЛЬ\n\nНик: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Сообщений: {messages}\n🎨 Картинок: {images}\n💸 Потрачено: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ ТЕКУЩЕЕ\n🌐 Язык: {lang}\n📱 Режим: {mode}\n🤖 ИИ: {ai_mode}",
        "en": "        👤 PROFILE\n\nUsername: {username}\n📅 {registered}\n\n        📊 STATISTICS\n💬 Messages: {messages}\n🎨 Images: {images}\n💸 Spent: {spent} ⭐\n💰 Balance: {balance} ⭐\n\n        ⚙️ CURRENT\n🌐 Language: {lang}\n📱 Mode: {mode}\n🤖 AI: {ai_mode}",
        "kk": "        👤 ПРОФИЛЬ\n\nНик: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Хабарламалар: {messages}\n🎨 Суреттер: {images}\n💸 Жұмсалды: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ АҒЫМДАҒЫ\n🌐 Тіл: {lang}\n📱 Режим: {mode}\n🤖 AI: {ai_mode}",
        "tr": "        👤 PROFİL\n\nKullanıcı adı: {username}\n📅 {registered}\n\n        📊 İSTATİSTİKLER\n💬 Mesajlar: {messages}\n🎨 Görseller: {images}\n💸 Harcanan: {spent} ⭐\n💰 Bakiye: {balance} ⭐\n\n        ⚙️ GÜNCEL\n🌐 Dil: {lang}\n📱 Mod: {mode}\n🤖 YZ: {ai_mode}",
        "uk": "        👤 ПРОФІЛЬ\n\nНік: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Повідомлень: {messages}\n🎨 Картинок: {images}\n💸 Витрачено: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ ПОТОЧНЕ\n🌐 Мова: {lang}\n📱 Режим: {mode}\n🤖 ШІ: {ai_mode}",
        "fr": "        👤 PROFIL\n\nPseudo: {username}\n📅 {registered}\n\n        📊 STATISTIQUES\n💬 Messages: {messages}\n🎨 Images: {images}\n💸 Dépensé: {spent} ⭐\n💰 Solde: {balance} ⭐\n\n        ⚙️ ACTUEL\n🌐 Langue: {lang}\n📱 Mode: {mode}\n🤖 IA: {ai_mode}"
    }
}

# Характеры
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

# Стили ответов
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

# Режимы ИИ
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

# Режимы работы
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

def get_work_mode_name(user_id: int, mode_id: str) -> str:
    """Получить название режима работы на языке пользователя"""
    lang = get_user_language(user_id)
    mode = WORK_MODES.get(mode_id, {})
    return mode.get(lang, mode.get("ru", mode_id))

def get_lang_name(user_id: int, lang_code: str) -> str:
    """Получить название языка"""
    lang = get_user_language(user_id)
    return LANGUAGES.get(lang_code, lang_code)