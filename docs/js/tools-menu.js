// docs/js/tools-menu.js

// Инициализация выпадающего меню инструментов
(function() {
  const toolsBtn = document.getElementById('toolsBtn');
  const toolsDropdown = document.getElementById('toolsDropdown');
  const toolsChev = document.getElementById('toolsChev');
  
  if (!toolsBtn || !toolsDropdown) return;
  
  // Проверяем сохраненное состояние
  let isOpen = false;
  try {
    isOpen = localStorage.getItem('tools_menu_open') === 'true';
  } catch(e) {}
  
  // Функция открытия/закрытия
  function toggleTools(e) {
    e.preventDefault();
    e.stopPropagation();
    
    isOpen = !isOpen;
    
    if (isOpen) {
      toolsDropdown.classList.add('open');
      toolsBtn.classList.add('active');
      toolsChev.classList.add('rotate');
      toolsChev.textContent = '▲';
    } else {
      toolsDropdown.classList.remove('open');
      toolsBtn.classList.remove('active');
      toolsChev.classList.remove('rotate');
      toolsChev.textContent = '▼';
    }
    
    // Сохраняем состояние
    try {
      localStorage.setItem('tools_menu_open', isOpen);
    } catch(e) {}
  }
  
  // Добавляем обработчик
  toolsBtn.addEventListener('click', toggleTools);
  
  // Закрываем при клике вне меню (опционально)
  document.addEventListener('click', (e) => {
    if (isOpen && !toolsBtn.contains(e.target) && !toolsDropdown.contains(e.target)) {
      toggleTools(e);
    }
  });
  
  // Устанавливаем начальное состояние
  if (isOpen) {
    toolsDropdown.classList.add('open');
    toolsBtn.classList.add('active');
    toolsChev.classList.remove('rotate');
    toolsChev.textContent = '▲';
  }
})();

// Обновление текстов при смене языка
export function updateToolsText(lang) {
  const translations = {
    ru: {
      tools: "🔧 Инструменты",
      removeBg: "Удаление фона",
      textFromImage: "Текст с фото",
      selfieFilters: "Селфи фильтры",
      music: "Создание музыки",
      meme: "Создание мемов",
      qr: "QR коды"
    },
    kk: {
      tools: "🔧 Құралдар",
      removeBg: "Фонды кетіру",
      textFromImage: "Фотонан мәтін",
      selfieFilters: "Селфи фильтрлер",
      music: "Музыка жасау",
      meme: "Мем жасау",
      qr: "QR кодтар"
    },
    en: {
      tools: "🔧 Tools",
      removeBg: "Remove Background",
      textFromImage: "Text from Image",
      selfieFilters: "Selfie Filters",
      music: "Create Music",
      meme: "Create Meme",
      qr: "QR Codes"
    },
    tr: {
      tools: "🔧 Araçlar",
      removeBg: "Arka planı kaldır",
      textFromImage: "Fotodan yazı",
      selfieFilters: "Selfie filtreleri",
      music: "Müzik oluştur",
      meme: "Meme oluştur",
      qr: "QR kodlar"
    },
    uk: {
      tools: "🔧 Інструменти",
      removeBg: "Видалити фон",
      textFromImage: "Текст з фото",
      selfieFilters: "Селфі фільтри",
      music: "Створити музику",
      meme: "Створити мем",
      qr: "QR коди"
    },
    fr: {
      tools: "🔧 Outils",
      removeBg: "Supprimer l'arrière-plan",
      textFromImage: "Texte depuis l'image",
      selfieFilters: "Filtres selfie",
      music: "Créer de la musique",
      meme: "Créer un mème",
      qr: "Codes QR"
    }
  };
  
  const t = translations[lang] || translations.ru;
  
  // Обновляем тексты
  const toolsBtnText = document.getElementById('toolsBtnText');
  const toolRemoveBgText = document.getElementById('toolRemoveBgText');
  const toolTextFromImageText = document.getElementById('toolTextFromImageText');
  const toolSelfieFiltersText = document.getElementById('toolSelfieFiltersText');
  const toolMusicText = document.getElementById('toolMusicText');
  const toolMemeText = document.getElementById('toolMemeText');
  const toolQrText = document.getElementById('toolQrText');
  
  if (toolsBtnText) toolsBtnText.innerHTML = t.tools;
  if (toolRemoveBgText) toolRemoveBgText.textContent = t.removeBg;
  if (toolTextFromImageText) toolTextFromImageText.textContent = t.textFromImage;
  if (toolSelfieFiltersText) toolSelfieFiltersText.textContent = t.selfieFilters;
  if (toolMusicText) toolMusicText.textContent = t.music;
  if (toolMemeText) toolMemeText.textContent = t.meme;
  if (toolQrText) toolQrText.textContent = t.qr;
}

// Экспортируем для использования в index.js
window.updateToolsText = updateToolsText;