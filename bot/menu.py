# bot/menu.py - ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ С ЛОКАЛИЗАЦИЕЙ
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from api import get_use_mini_app, get_user_persona, get_user_lang, get_user_ai_lang, get_user_style, get_ai_mode, get_user_limits
from payments import get_balance
from .config import MINIAPP_URL, is_valid_https_url
from datetime import datetime
from .helpers import format_balance
from bot.support import support_blocks


# =========================
# ВСЕ ТЕКСТЫ НА ВСЕХ ЯЗЫКАХ
# =========================
TEXTS = {
    "ru": {
        "menu_title": "💫 NextAI\n\nВыбирай действие кнопками ниже 👇",
        "balance_btn": "⭐ Баланс: {balance} звезд",
        "chat_btn": "💬 Чат с ИИ",
        "image_btn": "🖼 Генерация картинки",
        "buy_stars_btn": "⭐ Купить звезды",
        "settings_btn": "⚙️ Настройки",
        "help_btn": "❓ Помощь",
        "profile_btn": "👤 Профиль",
        "status_btn": "📌 Статус",
        "referral_btn": "🎁 Рефералы",
        "support_btn": "💬 Поддержка",
        "blocked": "⛔ Доступ заблокирован.\n\nЕсли ты считаешь это ошибкой — напиши админу.",
        "need_pay": "💰 Чтобы открыть Mini App, нужно купить пакет.\n\nОплату подключим позже.",
        "need_stars_chat": "⭐ Недостаточно звезд для чата с ИИ.\n\nКупите звезды в меню ниже 👇",
        "need_stars_miniapp": "⭐ Недостаточно звезд для Mini App.\n\nКупите звезды в меню ниже 👇",
        "settings": "⚙️ Настройки\n\nВыбери раздел:",
        "help": "❓ Помощь\n\nНажми «Открыть Mini App» или используй встроенный чат.",
        "profile": "        👤 ПРОФИЛЬ\n\nНик: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Сообщений: {messages}\n🎨 Картинок: {images}\n💸 Потрачено: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ ТЕКУЩЕЕ\n🌐 Язык: {lang}\n📱 Режим: {mode}\n🤖 ИИ: {ai_mode}",
        "status": "📌 Статус\n\nРаздел в разработке.",
        "ref": "🎁 Рефералы\n\nРаздел в разработке.",
        "support": "💬 Поддержка\n\nНапиши свой вопрос.",
        "support_blocked": "⛔ Поддержка заблокирована",
        "buy_stars": "⭐ Пакеты звезд\n\nВыберите пакет для пополнения:",
        "balance": "⭐ Ваш баланс звезд",
        "mode_settings": "🔄 Режим работы\n\nВыбери как пользоваться ботом:",
        "persona_settings": "🎭 Характер ИИ\n\nВыбери как ИИ будет отвечать:",
        "style_settings": "📝 Стиль ответа\n\nВыбери стиль ответов ИИ:",
        "lang_settings": "🌐 Язык интерфейса\n\nВыбери язык меню и кнопок:",
        "ai_lang_settings": "🌐 Язык ответов ИИ\n\nВыбери на каком языке будет отвечать ИИ:",
        "ai_mode_settings": "⚡ Режим ИИ\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 БЫСТРЫЙ (0.3 ⭐)\n• Быстрые ответы\n• Можно менять характер, стиль и язык ответов\n\n💎 КАЧЕСТВЕННЫЙ (1 ⭐)\n• Глубокие ответы\n• Можно менять только стиль\n• Язык определяется автоматически\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Сегодня осталось смен режима: {changes_left}/8\n⏰ Сброс в 00:00",
        "confirm_ai_mode_change": "⚠️ ПОДТВЕРЖДЕНИЕ\n\nВы выбрали режим: {new_mode}\n\nТекущий режим: {current_mode}\n\nПри смене режима:\n• История чата будет полностью очищена\n• Все предыдущие сообщения удалятся\n\nПродолжить?",
        "limit_exceeded": "⛔ Лимит исчерпан\n\nСегодня больше нельзя менять эту настройку.\nПопробуй завтра после 00:00.",
        "back_btn": "⬅️ Назад",
        "confirm_yes": "✅ Да, сменить",
        "confirm_no": "❌ Нет, отмена",
        "mode_miniapp": "📱 Mini App",
        "mode_inline": "💬 Встроенный",
        "ai_mode_fast": "🚀 Быстрый",
        "ai_mode_quality": "💎 Качественный",
        "persona_friendly": "😊 Общительный",
        "persona_fun": "😂 Весёлый",
        "persona_smart": "🧐 Умный",
        "persona_strict": "😐 Строгий",
        "style_short": "📏 Коротко",
        "style_steps": "📋 По шагам",
        "style_detail": "📚 Подробно",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "lang_kk": "🇰🇿 Қазақша",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_uk": "🇺🇦 Українська",
        "lang_fr": "🇫🇷 Français",
        "image_start": "🖼 Напиши описание картинки.\nСтоимость: 10⭐",
        "insufficient_stars": "❌ Недостаточно звезд (нужно {cost}⭐).\nКупи звезды в меню: ⭐ Купить звезды",
        "blocked_access": "⛔ Доступ заблокирован.",
        "generating": "🎨 Генерирую...",
        "error": "❌ Ошибка: {error}",
        "setting_changed": "✅ Настройка изменена",
        "persona_changed": "✅ Характер изменен на: {persona}",
        "style_changed": "✅ Стиль изменен на: {style}",
        "lang_changed": "✅ Язык изменен",
        "ai_lang_changed": "✅ Язык ответов ИИ изменен на: {lang}",
        "mode_changed": "✅ Режим работы переключен на {mode}!",
        "ai_mode_changed": "✅ Режим изменен на {mode}\n\n🧹 История чата очищена.\n📊 Сегодня осталось смен режима: {left}/8",
    },
    "en": {
        "menu_title": "💫 NextAI\n\nChoose an action with the buttons below 👇",
        "balance_btn": "⭐ Balance: {balance} stars",
        "chat_btn": "💬 AI Chat",
        "image_btn": "🖼 Image Generation",
        "buy_stars_btn": "⭐ Buy Stars",
        "settings_btn": "⚙️ Settings",
        "help_btn": "❓ Help",
        "profile_btn": "👤 Profile",
        "status_btn": "📌 Status",
        "referral_btn": "🎁 Referrals",
        "support_btn": "💬 Support",
        "blocked": "⛔ Access blocked.\n\nIf you think this is a mistake — contact admin.",
        "need_pay": "💰 To open Mini App, you need to buy a package.\n\nPayment will be added later.",
        "need_stars_chat": "⭐ Not enough stars for AI chat.\n\nBuy stars in the menu below 👇",
        "need_stars_miniapp": "⭐ Not enough stars for Mini App.\n\nBuy stars in the menu below 👇",
        "settings": "⚙️ Settings\n\nSelect a section:",
        "help": "❓ Help\n\nClick «Open Mini App» or use the built-in chat.",
        "profile": "        👤 PROFILE\n\nUsername: {username}\n📅 {registered}\n\n        📊 STATISTICS\n💬 Messages: {messages}\n🎨 Images: {images}\n💸 Spent: {spent} ⭐\n💰 Balance: {balance} ⭐\n\n        ⚙️ CURRENT\n🌐 Language: {lang}\n📱 Mode: {mode}\n🤖 AI: {ai_mode}",
        "status": "📌 Status\n\nSection in development.",
        "ref": "🎁 Referrals\n\nSection in development.",
        "support": "💬 Support\n\nWrite your question.",
        "support_blocked": "⛔ Support blocked",
        "buy_stars": "⭐ Star packages\n\nSelect a package to top up:",
        "balance": "⭐ Your star balance",
        "mode_settings": "🔄 Operation mode\n\nChoose how to use the bot:",
        "persona_settings": "🎭 AI Personality\n\nChoose how AI will respond:",
        "style_settings": "📝 Response style\n\nChoose the style of AI responses:",
        "lang_settings": "🌐 Interface language\n\nChoose menu and button language:",
        "ai_lang_settings": "🌐 AI response language\n\nChoose the language AI will respond in:",
        "ai_mode_settings": "⚡ AI Mode\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 FAST (0.3 ⭐)\n• Fast responses\n• Can change personality, style and language\n\n💎 QUALITY (1 ⭐)\n• Deep responses\n• Can change only style\n• Language is detected automatically\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Mode changes left today: {changes_left}/8\n⏰ Reset at 00:00",
        "confirm_ai_mode_change": "⚠️ CONFIRMATION\n\nYou selected mode: {new_mode}\n\nCurrent mode: {current_mode}\n\nWhen changing mode:\n• Chat history will be completely cleared\n• All previous messages will be deleted\n\nContinue?",
        "limit_exceeded": "⛔ Limit exceeded\n\nYou cannot change this setting anymore today.\nTry again tomorrow after 00:00.",
        "back_btn": "⬅️ Back",
        "confirm_yes": "✅ Yes, change",
        "confirm_no": "❌ No, cancel",
        "mode_miniapp": "📱 Mini App",
        "mode_inline": "💬 Built-in",
        "ai_mode_fast": "🚀 Fast",
        "ai_mode_quality": "💎 Quality",
        "persona_friendly": "😊 Friendly",
        "persona_fun": "😂 Fun",
        "persona_smart": "🧐 Smart",
        "persona_strict": "😐 Strict",
        "style_short": "📏 Short",
        "style_steps": "📋 Step by step",
        "style_detail": "📚 Detailed",
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "lang_kk": "🇰🇿 Kazakh",
        "lang_tr": "🇹🇷 Turkish",
        "lang_uk": "🇺🇦 Ukrainian",
        "lang_fr": "🇫🇷 French",
        "image_start": "🖼 Describe the image.\nCost: 10⭐",
        "insufficient_stars": "❌ Not enough stars (need {cost}⭐).\nBuy stars in the menu: ⭐ Buy stars",
        "blocked_access": "⛔ Access blocked.",
        "generating": "🎨 Generating...",
        "error": "❌ Error: {error}",
        "setting_changed": "✅ Setting changed",
        "persona_changed": "✅ Personality changed to: {persona}",
        "style_changed": "✅ Style changed to: {style}",
        "lang_changed": "✅ Language changed",
        "ai_lang_changed": "✅ AI response language changed to: {lang}",
        "mode_changed": "✅ Mode switched to {mode}!",
        "ai_mode_changed": "✅ Mode changed to {mode}\n\n🧹 Chat history cleared.\n📊 Mode changes left today: {left}/8",
    },
    "kk": {
        "menu_title": "💫 NextAI\n\nТөмендегі батырмалармен әрекетті таңдаңыз 👇",
        "balance_btn": "⭐ Баланс: {balance} жұлдыз",
        "chat_btn": "💬 AI чат",
        "image_btn": "🖼 Сурет генерациясы",
        "buy_stars_btn": "⭐ Жұлдыз сатып алу",
        "settings_btn": "⚙️ Баптаулар",
        "help_btn": "❓ Көмек",
        "profile_btn": "👤 Профиль",
        "status_btn": "📌 Мәртебе",
        "referral_btn": "🎁 Рефералдар",
        "support_btn": "💬 Қолдау",
        "blocked": "⛔ Қолжетімділік бұғатталды.\n\nҚате деп ойласаңыз — әкімшіге жазыңыз.",
        "need_pay": "💰 Mini App ашу үшін пакет сатып алу керек.\n\nТөлем кейін қосылады.",
        "need_stars_chat": "⭐ AI чат үшін жұлдыздар жеткіліксіз.\n\nТөмендегі мәзірден жұлдыздар сатып алыңыз 👇",
        "need_stars_miniapp": "⭐ Mini App үшін жұлдыздар жеткіліксіз.\n\nТөмендегі мәзірден жұлдыздар сатып алыңыз 👇",
        "settings": "⚙️ Баптаулар\n\nБөлімді таңдаңыз:",
        "help": "❓ Көмек\n\n«Mini App ашу» басыңыз немесе кіріктірілген чатты пайдаланыңыз.",
        "profile": "        👤 ПРОФИЛЬ\n\nНик: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Хабарламалар: {messages}\n🎨 Суреттер: {images}\n💸 Жұмсалған: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ АҒЫМДАҒЫ\n🌐 Тіл: {lang}\n📱 Режим: {mode}\n🤖 AI: {ai_mode}",
        "status": "📌 Мәртебе\n\nБөлім әзірленуде.",
        "ref": "🎁 Рефералдар\n\nБөлім әзірленуде.",
        "support": "💬 Қолдау\n\nСұрағыңызды жазыңыз.",
        "support_blocked": "⛔ Қолдау бұғатталған",
        "buy_stars": "⭐ Жұлдыз пакеттері\n\nТолтыру үшін пакетті таңдаңыз:",
        "balance": "⭐ Сіздің жұлдыз балансыңыз",
        "mode_settings": "🔄 Жұмыс режимі\n\nБотты қалай пайдалану керектігін таңдаңыз:",
        "persona_settings": "🎭 AI Мінезі\n\nAI қалай жауап беретінін таңдаңыз:",
        "style_settings": "📝 Жауап стилі\n\nAI жауап стилін таңдаңыз:",
        "lang_settings": "🌐 Интерфейс тілі\n\nМәзір және түймелер тілін таңдаңыз:",
        "ai_lang_settings": "🌐 AI жауап тілі\n\nAI қай тілде жауап беретінін таңдаңыз:",
        "ai_mode_settings": "⚡ AI Режимі\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 ЖЫЛДАМ (0.3 ⭐)\n• Жылдам жауаптар\n• Мінез, стиль және тілді өзгертуге болады\n\n💎 САПАЛЫ (1 ⭐)\n• Терең жауаптар\n• Тек стильді өзгертуге болады\n• Тіл автоматты түрде анықталады\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Бүгін режим ауыстыру қалды: {changes_left}/8\n⏰ Қалпына келтіру 00:00-де",
        "confirm_ai_mode_change": "⚠️ РАСТАУ\n\nСіз режимді таңдадыңыз: {new_mode}\n\nАғымдағы режим: {current_mode}\n\nРежимді ауыстырған кезде:\n• Чат тарихы толығымен жойылады\n• Барлық алдыңғы хабарламалар жойылады\n\nЖалғастыру?",
        "limit_exceeded": "⛔ Лимит толтырылды\n\nБүгін бұл параметрді өзгерту мүмкін емес.\nЕртең 00:00-ден кейін қайталап көріңіз.",
        "back_btn": "⬅️ Артқа",
        "confirm_yes": "✅ Иә, ауыстыру",
        "confirm_no": "❌ Жоқ, болдырмау",
        "mode_miniapp": "📱 Mini App",
        "mode_inline": "💬 Кіріктірілген",
        "ai_mode_fast": "🚀 Жылдам",
        "ai_mode_quality": "💎 Сапалы",
        "persona_friendly": "😊 Достық",
        "persona_fun": "😂 Көңілді",
        "persona_smart": "🧐 Ақылды",
        "persona_strict": "😐 Қатаң",
        "style_short": "📏 Қысқа",
        "style_steps": "📋 Қадаммен",
        "style_detail": "📚 Толық",
        "lang_ru": "🇷🇺 Орысша",
        "lang_en": "🇬🇧 Ағылшынша",
        "lang_kk": "🇰🇿 Қазақша",
        "lang_tr": "🇹🇷 Түрікше",
        "lang_uk": "🇺🇦 Украинша",
        "lang_fr": "🇫🇷 Французша",
        "image_start": "🖼 Суреттің сипаттамасын жазыңыз.\nҚұны: 10⭐",
        "insufficient_stars": "❌ Жұлдыздар жеткіліксіз (керек {cost}⭐).\nМәзірден жұлдыз сатып алыңыз: ⭐ Жұлдыз сатып алу",
        "blocked_access": "⛔ Қолжетімділік бұғатталды.",
        "generating": "🎨 Жасалуда...",
        "error": "❌ Қате: {error}",
        "setting_changed": "✅ Баптау өзгертілді",
        "persona_changed": "✅ Мінез {persona} өзгертілді",
        "style_changed": "✅ Стиль {style} өзгертілді",
        "lang_changed": "✅ Тіл өзгертілді",
        "ai_lang_changed": "✅ AI жауап тілі {lang} өзгертілді",
        "mode_changed": "✅ Жұмыс режимі {mode} ауыстырылды!",
        "ai_mode_changed": "✅ Режим {mode} өзгертілді\n\n🧹 Чат тарихы тазартылды.\n📊 Бүгін режим ауыстыру қалды: {left}/8",
    },
    "tr": {
        "menu_title": "💫 NextAI\n\nAşağıdaki butonlarla işlem seçin 👇",
        "balance_btn": "⭐ Bakiye: {balance} yıldız",
        "chat_btn": "💬 AI Sohbet",
        "image_btn": "🖼 Görsel Oluşturma",
        "buy_stars_btn": "⭐ Yıldız Satın Al",
        "settings_btn": "⚙️ Ayarlar",
        "help_btn": "❓ Yardım",
        "profile_btn": "👤 Profil",
        "status_btn": "📌 Durum",
        "referral_btn": "🎁 Davetler",
        "support_btn": "💬 Destek",
        "blocked": "⛔ Erişim engellendi.\n\nBunun bir hata olduğunu düşünüyorsanız — yöneticiye yazın.",
        "need_pay": "💰 Mini App'i açmak için paket satın almanız gerekiyor.\n\nÖdeme daha sonra eklenecek.",
        "need_stars_chat": "⭐ AI sohbeti için yeterli yıldız yok.\n\nAşağıdaki menüden yıldız satın alın 👇",
        "need_stars_miniapp": "⭐ Mini App için yeterli yıldız yok.\n\nAşağıdaki menüden yıldız satın alın 👇",
        "settings": "⚙️ Ayarlar\n\nBir bölüm seçin:",
        "help": "❓ Yardım\n\n«Mini App'i Aç»a tıklayın veya yerleşik sohbeti kullanın.",
        "profile": "        👤 PROFİL\n\nKullanıcı adı: {username}\n📅 {registered}\n\n        📊 İSTATİSTİKLER\n💬 Mesajlar: {messages}\n🎨 Resimler: {images}\n💸 Harcanan: {spent} ⭐\n💰 Bakiye: {balance} ⭐\n\n        ⚙️ GÜNCEL\n🌐 Dil: {lang}\n📱 Mod: {mode}\n🤖 AI: {ai_mode}",
        "status": "📌 Durum\n\nBölüm geliştirme aşamasında.",
        "ref": "🎁 Davetler\n\nBölüm geliştirme aşamasında.",
        "support": "💬 Destek\n\nSorunuzu yazın.",
        "support_blocked": "⛔ Destek engellendi",
        "buy_stars": "⭐ Yıldız paketleri\n\nYüklemek için bir paket seçin:",
        "balance": "⭐ Yıldız bakiyeniz",
        "mode_settings": "🔄 Çalışma modu\n\nBotu nasıl kullanacağınızı seçin:",
        "persona_settings": "🎭 AI Kişiliği\n\nAI'nın nasıl yanıt vereceğini seçin:",
        "style_settings": "📝 Yanıt stili\n\nAI yanıtlarının stilini seçin:",
        "lang_settings": "🌐 Arayüz dili\n\nMenü ve buton dilini seçin:",
        "ai_lang_settings": "🌐 AI yanıt dili\n\nAI'nın hangi dilde yanıt vereceğini seçin:",
        "ai_mode_settings": "⚡ AI Modu\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 HIZLI (0.3 ⭐)\n• Hızlı yanıtlar\n• Kişilik, stil ve dil değiştirilebilir\n\n💎 KALİTELİ (1 ⭐)\n• Derin yanıtlar\n• Sadece stil değiştirilebilir\n• Dil otomatik algılanır\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Bugün kalan mod değişikliği: {changes_left}/8\n⏰ Sıfırlama 00:00'da",
        "confirm_ai_mode_change": "⚠️ ONAYLAMA\n\nModu seçtiniz: {new_mode}\n\nMevcut mod: {current_mode}\n\nMod değiştirirken:\n• Sohbet geçmişi tamamen silinecek\n• Önceki tüm mesajlar silinecek\n\nDevam et?",
        "limit_exceeded": "⛔ Limit aşıldı\n\nBugün bu ayarı değiştiremezsiniz.\nYarın 00:00'dan sonra tekrar deneyin.",
        "back_btn": "⬅️ Geri",
        "confirm_yes": "✅ Evet, değiştir",
        "confirm_no": "❌ Hayır, iptal",
        "mode_miniapp": "📱 Mini App",
        "mode_inline": "💬 Yerleşik",
        "ai_mode_fast": "🚀 Hızlı",
        "ai_mode_quality": "💎 Kaliteli",
        "persona_friendly": "😊 Samimi",
        "persona_fun": "😂 Eğlenceli",
        "persona_smart": "🧐 Zeki",
        "persona_strict": "😐 Katı",
        "style_short": "📏 Kısa",
        "style_steps": "📋 Adım adım",
        "style_detail": "📚 Detaylı",
        "lang_ru": "🇷🇺 Rusça",
        "lang_en": "🇬🇧 İngilizce",
        "lang_kk": "🇰🇿 Kazakça",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_uk": "🇺🇦 Ukraynaca",
        "lang_fr": "🇫🇷 Fransızca",
        "image_start": "🖼 Resim açıklaması yaz.\nÜcret: 10⭐",
        "insufficient_stars": "❌ Yeterli yıldız yok (gerekli {cost}⭐).\nMenüden yıldız satın al: ⭐ Yıldız Satın Al",
        "blocked_access": "⛔ Erişim engellendi.",
        "generating": "🎨 Oluşturuluyor...",
        "error": "❌ Hata: {error}",
        "setting_changed": "✅ Ayar değiştirildi",
        "persona_changed": "✅ Kişilik {persona} olarak değiştirildi",
        "style_changed": "✅ Stil {style} olarak değiştirildi",
        "lang_changed": "✅ Dil değiştirildi",
        "ai_lang_changed": "✅ AI yanıt dili {lang} olarak değiştirildi",
        "mode_changed": "✅ Çalışma modu {mode} olarak değiştirildi!",
        "ai_mode_changed": "✅ Mod {mode} olarak değiştirildi\n\n🧹 Sohbet geçmişi temizlendi.\n📊 Bugün kalan mod değişikliği: {left}/8",
    },
    "uk": {
        "menu_title": "💫 NextAI\n\nОбери дію кнопками нижче 👇",
        "balance_btn": "⭐ Баланс: {balance} зірок",
        "chat_btn": "💬 Чат з ІІ",
        "image_btn": "🖼 Генерація картинки",
        "buy_stars_btn": "⭐ Купити зірки",
        "settings_btn": "⚙️ Налаштування",
        "help_btn": "❓ Допомога",
        "profile_btn": "👤 Профіль",
        "status_btn": "📌 Статус",
        "referral_btn": "🎁 Реферали",
        "support_btn": "💬 Підтримка",
        "blocked": "⛔ Доступ заблоковано.\n\nЯкщо ви вважаєте це помилкою — напишіть адміну.",
        "need_pay": "💰 Щоб відкрити Mini App, потрібно купити пакет.\n\nОплату підключимо пізніше.",
        "need_stars_chat": "⭐ Недостатньо зірок для чату з ІІ.\n\nКупіть зірки в меню нижче 👇",
        "need_stars_miniapp": "⭐ Недостатньо зірок для Mini App.\n\nКупіть зірки в меню нижче 👇",
        "settings": "⚙️ Налаштування\n\nВиберіть розділ:",
        "help": "❓ Допомога\n\nНатисніть «Відкрити Mini App» або використовуйте вбудований чат.",
        "profile": "        👤 ПРОФІЛЬ\n\nНік: {username}\n📅 {registered}\n\n        📊 СТАТИСТИКА\n💬 Повідомлень: {messages}\n🎨 Зображень: {images}\n💸 Витрачено: {spent} ⭐\n💰 Баланс: {balance} ⭐\n\n        ⚙️ ПОТОЧНЕ\n🌐 Мова: {lang}\n📱 Режим: {mode}\n🤖 ІІ: {ai_mode}",
        "status": "📌 Статус\n\nРозділ в розробці.",
        "ref": "🎁 Реферали\n\nРозділ в розробці.",
        "support": "💬 Підтримка\n\nНапишіть своє питання.",
        "support_blocked": "⛔ Підтримка заблокована",
        "buy_stars": "⭐ Пакети зірок\n\nВиберіть пакет для поповнення:",
        "balance": "⭐ Ваш баланс зірок",
        "mode_settings": "🔄 Режим роботи\n\nВиберіть як користуватися ботом:",
        "persona_settings": "🎭 Характер ІІ\n\nВиберіть як ІІ буде відповідати:",
        "style_settings": "📝 Стиль відповіді\n\nВиберіть стиль відповідей ІІ:",
        "lang_settings": "🌐 Мова інтерфейсу\n\nВиберіть мову меню та кнопок:",
        "ai_lang_settings": "🌐 Мова відповідей ІІ\n\nВиберіть якою мовою буде відповідати ІІ:",
        "ai_mode_settings": "⚡ Режим ІІ\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 ШВИДКИЙ (0.3 ⭐)\n• Швидкі відповіді\n• Можна змінювати характер, стиль та мову\n\n💎 ЯКІСНИЙ (1 ⭐)\n• Глибокі відповіді\n• Можна змінювати тільки стиль\n• Мова визначається автоматично\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Сьогодні залишилось змін режиму: {changes_left}/8\n⏰ Скидання о 00:00",
        "confirm_ai_mode_change": "⚠️ ПІДТВЕРДЖЕННЯ\n\nВи обрали режим: {new_mode}\n\nПоточний режим: {current_mode}\n\nПри зміні режиму:\n• Історія чату буде повністю очищена\n• Всі попередні повідомлення видаляться\n\nПродовжити?",
        "limit_exceeded": "⛔ Ліміт вичерпано\n\nСьогодні більше не можна змінювати цей параметр.\nСпробуйте завтра після 00:00.",
        "back_btn": "⬅️ Назад",
        "confirm_yes": "✅ Так, змінити",
        "confirm_no": "❌ Ні, скасувати",
        "mode_miniapp": "📱 Mini App",
        "mode_inline": "💬 Вбудований",
        "ai_mode_fast": "🚀 Швидкий",
        "ai_mode_quality": "💎 Якісний",
        "persona_friendly": "😊 Товариський",
        "persona_fun": "😂 Веселий",
        "persona_smart": "🧐 Розумний",
        "persona_strict": "😐 Суворий",
        "style_short": "📏 Коротко",
        "style_steps": "📋 Кроками",
        "style_detail": "📚 Детально",
        "lang_ru": "🇷🇺 Російська",
        "lang_en": "🇬🇧 Англійська",
        "lang_kk": "🇰🇿 Казахська",
        "lang_tr": "🇹🇷 Турецька",
        "lang_uk": "🇺🇦 Українська",
        "lang_fr": "🇫🇷 Французька",
        "image_start": "🖼 Напиши опис картинки.\nВартість: 10⭐",
        "insufficient_stars": "❌ Недостатньо зірок (потрібно {cost}⭐).\nКупи зірки в меню: ⭐ Купити зірки",
        "blocked_access": "⛔ Доступ заблоковано.",
        "generating": "🎨 Генерую...",
        "error": "❌ Помилка: {error}",
        "setting_changed": "✅ Налаштування змінено",
        "persona_changed": "✅ Характер змінено на: {persona}",
        "style_changed": "✅ Стиль змінено на: {style}",
        "lang_changed": "✅ Мову змінено",
        "ai_lang_changed": "✅ Мову відповідей ІІ змінено на: {lang}",
        "mode_changed": "✅ Режим роботи переключено на {mode}!",
        "ai_mode_changed": "✅ Режим змінено на {mode}\n\n🧹 Історія чату очищена.\n📊 Сьогодні залишилось змін режиму: {left}/8",
    },
    "fr": {
        "menu_title": "💫 NextAI\n\nChoisissez une action avec les boutons ci-dessous 👇",
        "balance_btn": "⭐ Solde : {balance} étoiles",
        "chat_btn": "💬 Chat IA",
        "image_btn": "🖼 Génération d'image",
        "buy_stars_btn": "⭐ Acheter des étoiles",
        "settings_btn": "⚙️ Paramètres",
        "help_btn": "❓ Aide",
        "profile_btn": "👤 Profil",
        "status_btn": "📌 Statut",
        "referral_btn": "🎁 Parrainage",
        "support_btn": "💬 Support",
        "blocked": "⛔ Accès bloqué.\n\nSi vous pensez que c'est une erreur — contactez l'admin.",
        "need_pay": "💰 Pour ouvrir Mini App, vous devez acheter un pack.\n\nLe paiement sera ajouté plus tard.",
        "need_stars_chat": "⭐ Pas assez d'étoiles pour le chat IA.\n\nAchetez des étoiles dans le menu ci-dessous 👇",
        "need_stars_miniapp": "⭐ Pas assez d'étoiles pour Mini App.\n\nAchetez des étoiles dans le menu ci-dessous 👇",
        "settings": "⚙️ Paramètres\n\nChoisissez une section :",
        "help": "❓ Aide\n\nCliquez sur « Ouvrir Mini App » ou utilisez le chat intégré.",
        "profile": "        👤 PROFIL\n\nPseudo : {username}\n📅 {registered}\n\n        📊 STATISTIQUES\n💬 Messages : {messages}\n🎨 Images : {images}\n💸 Dépensé : {spent} ⭐\n💰 Solde : {balance} ⭐\n\n        ⚙️ ACTUEL\n🌐 Langue : {lang}\n📱 Mode : {mode}\n🤖 IA : {ai_mode}",
        "status": "📌 Statut\n\nSection en développement.",
        "ref": "🎁 Parrainage\n\nSection en développement.",
        "support": "💬 Support\n\nÉcrivez votre question.",
        "support_blocked": "⛔ Support bloqué",
        "buy_stars": "⭐ Packs d'étoiles\n\nChoisissez un pack à recharger :",
        "balance": "⭐ Votre solde d'étoiles",
        "mode_settings": "🔄 Mode de fonctionnement\n\nChoisissez comment utiliser le bot :",
        "persona_settings": "🎭 Personnalité de l'IA\n\nChoisissez comment l'IA répondra :",
        "style_settings": "📝 Style de réponse\n\nChoisissez le style des réponses de l'IA :",
        "lang_settings": "🌐 Langue de l'interface\n\nChoisissez la langue du menu et des boutons :",
        "ai_lang_settings": "🌐 Langue des réponses de l'IA\n\nChoisissez la langue dans laquelle l'IA répondra :",
        "ai_mode_settings": "⚡ Mode IA\n\n━━━━━━━━━━━━━━━━━━━━━━\n🚀 RAPIDE (0.3 ⭐)\n• Réponses rapides\n• Peut changer personnalité, style et langue\n\n💎 QUALITÉ (1 ⭐)\n• Réponses approfondies\n• Peut changer seulement le style\n• Langue détectée automatiquement\n━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Changements de mode restants aujourd'hui : {changes_left}/8\n⏰ Réinitialisation à 00:00",
        "confirm_ai_mode_change": "⚠️ CONFIRMATION\n\nVous avez sélectionné le mode : {new_mode}\n\nMode actuel : {current_mode}\n\nEn changeant de mode :\n• L'historique du chat sera complètement effacé\n• Tous les messages précédents seront supprimés\n\nContinuer ?",
        "limit_exceeded": "⛔ Limite dépassée\n\nVous ne pouvez plus modifier ce paramètre aujourd'hui.\nRéessayez demain après 00:00.",
        "back_btn": "⬅️ Retour",
        "confirm_yes": "✅ Oui, changer",
        "confirm_no": "❌ Non, annuler",
        "mode_miniapp": "📱 Mini App",
        "mode_inline": "💬 Intégré",
        "ai_mode_fast": "🚀 Rapide",
        "ai_mode_quality": "💎 Qualité",
        "persona_friendly": "😊 Amical",
        "persona_fun": "😂 Drôle",
        "persona_smart": "🧐 Intelligent",
        "persona_strict": "😐 Strict",
        "style_short": "📏 Court",
        "style_steps": "📋 Étape par étape",
        "style_detail": "📚 Détaillé",
        "lang_ru": "🇷🇺 Russe",
        "lang_en": "🇬🇧 Anglais",
        "lang_kk": "🇰🇿 Kazakh",
        "lang_tr": "🇹🇷 Turc",
        "lang_uk": "🇺🇦 Ukrainien",
        "lang_fr": "🇫🇷 Français",
        "image_start": "🖼 Décrivez l'image.\nCoût : 10⭐",
        "insufficient_stars": "❌ Pas assez d'étoiles (besoin de {cost}⭐).\nAchetez des étoiles dans le menu : ⭐ Acheter des étoiles",
        "blocked_access": "⛔ Accès bloqué.",
        "generating": "🎨 Génération...",
        "error": "❌ Erreur : {error}",
        "setting_changed": "✅ Paramètre modifié",
        "persona_changed": "✅ Personnalité changée en : {persona}",
        "style_changed": "✅ Style changé en : {style}",
        "lang_changed": "✅ Langue changée",
        "ai_lang_changed": "✅ Langue des réponses de l'IA changée en : {lang}",
        "mode_changed": "✅ Mode changé en {mode} !",
        "ai_mode_changed": "✅ Mode changé en {mode}\n\n🧹 Historique du chat effacé.\n📊 Changements de mode restants aujourd'hui : {left}/8",
    },
}


def get_text(user_id: int, key: str, **kwargs) -> str:
    """Получить текст на языке пользователя"""
    from api import get_user_lang
    lang = get_user_lang(user_id) or "ru"
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text


# =========================
# ВСПОМОГАТЕЛЬНЫЕ КЛАВИАТУРЫ (используют get_text)
# =========================
def tab_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")]])


def settings_kb(user_id: int) -> InlineKeyboardMarkup:
    use_mini_app = get_use_mini_app(user_id)
    ai_mode = get_ai_mode(user_id)
    limits = get_user_limits(user_id)
    
    keyboard = []
    
    if not use_mini_app:
        if ai_mode == "fast":
            keyboard.append([InlineKeyboardButton(get_text(user_id, "ai_lang_settings"), callback_data="tab:ai_lang_settings")])
        
        if ai_mode == "fast":
            used = limits.get("groq_persona", 0)
            max_limit = 5
            remaining = max_limit - used
            btn_text = f"🎭 {get_text(user_id, 'persona_settings')} ({remaining}/{max_limit})"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:persona_settings")])
        
        if ai_mode == "fast":
            used = limits.get("groq_style", 0)
            max_limit = 5
        else:
            used = limits.get("openai_style", 0)
            max_limit = 7
        remaining = max_limit - used
        btn_text = f"📝 {get_text(user_id, 'style_settings')} ({remaining}/{max_limit})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:style_settings")])
        
        used = limits.get("ai_mode_changes", 0)
        max_limit = 8
        remaining = max_limit - used
        btn_text = f"⚡ {get_text(user_id, 'ai_mode_settings')} ({remaining}/{max_limit})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data="tab:ai_mode_settings")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "mode_settings"), callback_data="tab:mode_settings")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "lang_settings"), callback_data="tab:lang_settings")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    
    return InlineKeyboardMarkup(keyboard)


def mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    use_mini_app = get_use_mini_app(user_id)
    
    keyboard = []
    if use_mini_app:
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'mode_miniapp')}", callback_data="ignore")])
        keyboard.append([InlineKeyboardButton(get_text(user_id, 'mode_inline'), callback_data="switch_to_inline")])
    else:
        keyboard.append([InlineKeyboardButton(get_text(user_id, 'mode_miniapp'), callback_data="switch_to_miniapp")])
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'mode_inline')}", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def ai_mode_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    current = get_ai_mode(user_id) or "fast"
    limits = get_user_limits(user_id)
    used = limits.get("ai_mode_changes", 0)
    
    keyboard = []
    
    if current == "fast":
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'ai_mode_fast')}", callback_data="ignore")])
        if used < 8:
            keyboard.append([InlineKeyboardButton(get_text(user_id, 'ai_mode_quality'), callback_data="confirm_ai_mode:quality")])
        else:
            keyboard.append([InlineKeyboardButton(f"{get_text(user_id, 'ai_mode_quality')} (лимит)", callback_data="limit_exceeded")])
    else:
        if used < 8:
            keyboard.append([InlineKeyboardButton(get_text(user_id, 'ai_mode_fast'), callback_data="confirm_ai_mode:fast")])
        else:
            keyboard.append([InlineKeyboardButton(f"{get_text(user_id, 'ai_mode_fast')} (лимит)", callback_data="limit_exceeded")])
        keyboard.append([InlineKeyboardButton(f"✅ {get_text(user_id, 'ai_mode_quality')}", callback_data="ignore")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def confirm_ai_mode_kb(user_id: int, new_mode: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "confirm_yes"), callback_data=f"execute_ai_mode:{new_mode}")],
        [InlineKeyboardButton(get_text(user_id, "confirm_no"), callback_data="back_to_previous")]
    ]
    return InlineKeyboardMarkup(keyboard)


def persona_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    current = get_user_persona(user_id) or "friendly"
    limits = get_user_limits(user_id)
    used = limits.get("groq_persona", 0)
    
    personas = [
        ("friendly", get_text(user_id, "persona_friendly")),
        ("fun", get_text(user_id, "persona_fun")),
        ("smart", get_text(user_id, "persona_smart")),
        ("strict", get_text(user_id, "persona_strict"))
    ]
    
    keyboard = []
    for p_id, p_name in personas:
        if p_id == current:
            keyboard.append([InlineKeyboardButton(f"✅ {p_name}", callback_data="ignore")])
        else:
            if used < 5:
                keyboard.append([InlineKeyboardButton(p_name, callback_data=f"set_persona:{p_id}")])
            else:
                keyboard.append([InlineKeyboardButton(f"{p_name} (лимит)", callback_data="limit_exceeded")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def style_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    current = get_user_style(user_id) or "steps"
    ai_mode = get_ai_mode(user_id)
    limits = get_user_limits(user_id)
    
    if ai_mode == "fast":
        used = limits.get("groq_style", 0)
        max_limit = 5
    else:
        used = limits.get("openai_style", 0)
        max_limit = 7
    
    styles = [
        ("short", get_text(user_id, "style_short")),
        ("steps", get_text(user_id, "style_steps")),
        ("detail", get_text(user_id, "style_detail"))
    ]
    
    keyboard = []
    for s_id, s_name in styles:
        if s_id == current:
            keyboard.append([InlineKeyboardButton(f"✅ {s_name}", callback_data="ignore")])
        else:
            if used < max_limit:
                keyboard.append([InlineKeyboardButton(s_name, callback_data=f"set_style:{s_id}")])
            else:
                keyboard.append([InlineKeyboardButton(f"{s_name} (лимит)", callback_data="limit_exceeded")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def ai_lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    current = get_user_ai_lang(user_id) or "ru"
    
    languages = [
        ("ru", get_text(user_id, "lang_ru")),
        ("en", get_text(user_id, "lang_en")),
        ("kk", get_text(user_id, "lang_kk")),
        ("tr", get_text(user_id, "lang_tr")),
        ("uk", get_text(user_id, "lang_uk")),
        ("fr", get_text(user_id, "lang_fr"))
    ]
    
    keyboard = []
    row = []
    for i, (lang_id, lang_name) in enumerate(languages):
        if lang_id == current:
            row.append(InlineKeyboardButton(f"✅ {lang_name}", callback_data="ignore"))
        else:
            row.append(InlineKeyboardButton(lang_name, callback_data=f"set_ai_lang:{lang_id}"))
        if len(row) == 2 or i == len(languages) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def lang_settings_kb(user_id: int) -> InlineKeyboardMarkup:
    current = get_user_lang(user_id) or "ru"
    
    languages = [
        ("ru", get_text(user_id, "lang_ru")),
        ("en", get_text(user_id, "lang_en")),
        ("kk", get_text(user_id, "lang_kk")),
        ("tr", get_text(user_id, "lang_tr")),
        ("uk", get_text(user_id, "lang_uk")),
        ("fr", get_text(user_id, "lang_fr"))
    ]
    
    keyboard = []
    row = []
    for i, (lang_id, lang_name) in enumerate(languages):
        if lang_id == current:
            row.append(InlineKeyboardButton(f"✅ {lang_name}", callback_data="ignore"))
        else:
            row.append(InlineKeyboardButton(lang_name, callback_data=f"set_lang:{lang_id}"))
        if len(row) == 2 or i == len(languages) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


def stars_kb(user_id: int) -> InlineKeyboardMarkup:
    from payments import get_packages
    keyboard = []
    packages = get_packages()
    
    for p in packages:
        stars = p["stars"]
        price = f"${p['price_usd']:.2f}"
        discount = f" 🔥 -{p['discount']}%" if p['discount'] > 0 else ""
        popular = " ⭐" if p.get('popular', False) else ""
        
        btn_text = f"{stars} ⭐ – {price}{discount}{popular}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_stars:{p['id']}")])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_btn"), callback_data="back_to_previous")])
    return InlineKeyboardMarkup(keyboard)


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================
def main_menu_for_user(user_id: int) -> InlineKeyboardMarkup:
    from api import get_access
    a = get_access(user_id) if user_id else {"is_free": False, "is_blocked": False}
    balance = get_balance(user_id)
    formatted_balance = format_balance(balance)
    use_mini_app = get_use_mini_app(user_id)

    keyboard = []

    if a.get("is_blocked"):
        keyboard.append([InlineKeyboardButton(get_text(user_id, "blocked"), callback_data="tab:blocked")])
        return InlineKeyboardMarkup(keyboard)

    keyboard.append([InlineKeyboardButton(get_text(user_id, "balance_btn").format(balance=formatted_balance), callback_data="tab:balance")])

    if use_mini_app:
        can_open_miniapp = (balance >= 1 or a.get("is_free")) and is_valid_https_url(MINIAPP_URL)
        
        if can_open_miniapp:
            keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINIAPP_URL))])
        else:
            if balance < 1:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_stars_miniapp")])
            else:
                keyboard.append([InlineKeyboardButton("🚀 Открыть Mini App", callback_data="tab:need_pay")])
    else:
        can_use_chat = (balance >= 1 or a.get("is_free"))
        
        if can_use_chat:
            keyboard.append([InlineKeyboardButton(get_text(user_id, "chat_btn"), callback_data="inline_chat")])
            keyboard.append([InlineKeyboardButton(get_text(user_id, "image_btn"), callback_data="inline_image")])
        else:
            keyboard.append([InlineKeyboardButton(get_text(user_id, "chat_btn"), callback_data="tab:need_stars_chat")])
            keyboard.append([InlineKeyboardButton(get_text(user_id, "image_btn"), callback_data="tab:need_stars_chat")])

    keyboard.append([InlineKeyboardButton(get_text(user_id, "buy_stars_btn"), callback_data="tab:buy_stars")])

    bottom_row1 = []
    bottom_row1.append(InlineKeyboardButton(get_text(user_id, "settings_btn"), callback_data="tab:settings"))
    bottom_row1.append(InlineKeyboardButton(get_text(user_id, "help_btn"), callback_data="tab:help"))
    keyboard.append(bottom_row1)
    
    bottom_row2 = []
    bottom_row2.append(InlineKeyboardButton(get_text(user_id, "profile_btn"), callback_data="tab:profile"))
    bottom_row2.append(InlineKeyboardButton(get_text(user_id, "status_btn"), callback_data="tab:status"))
    keyboard.append(bottom_row2)
    
    bottom_row3 = []
    bottom_row3.append(InlineKeyboardButton(get_text(user_id, "referral_btn"), callback_data="tab:ref"))
    
    is_support_blocked = False
    if user_id in support_blocks:
        if datetime.now() < support_blocks[user_id]:
            is_support_blocked = True
    
    if is_support_blocked:
        bottom_row3.append(InlineKeyboardButton(get_text(user_id, "support_blocked"), callback_data="tab:support_blocked"))
    else:
        bottom_row3.append(InlineKeyboardButton(get_text(user_id, "support_btn"), callback_data="tab:support"))
    
    keyboard.append(bottom_row3)

    return InlineKeyboardMarkup(keyboard)