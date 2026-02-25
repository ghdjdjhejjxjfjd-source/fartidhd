// docs/js/index.js
const tg = window.Telegram?.WebApp;

// ===== VH (Telegram/iOS) =====
function applyVH(){
  if (tg && typeof tg.viewportHeight === "number") {
    document.documentElement.style.setProperty("--vh", tg.viewportHeight + "px");
  } else {
    document.documentElement.style.setProperty("--vh", window.innerHeight + "px");
  }
}

if (tg) {
  tg.ready();
  tg.expand();
  applyVH();
  tg.onEvent("viewportChanged", applyVH);
} else {
  applyVH();
  window.addEventListener("resize", applyVH);
}

// ===== storage keys =====
const STORAGE_LANG = "miniapp_lang_v1";
const STORAGE_THEME = "miniapp_theme_v1";
const STORAGE_STYLE = "miniapp_style_v1";
const STORAGE_TOOLS = "tools_menu_open";

// ===== DOM элементы =====
const chatBtn = document.getElementById("chatBtn");
const imgBtn = document.getElementById("imgBtn");
const subText = document.getElementById("subText");
const verText = document.getElementById("verText");
const langTitle = document.getElementById("langTitle");

const langBtn = document.getElementById("langBtn");
const langBtnText = document.getElementById("langBtnText");
const langOverlay = document.getElementById("langOverlay");
const langList = document.getElementById("langList");
const langClose = document.getElementById("langClose");
const langSheetTitle = document.getElementById("langSheetTitle");

const themeBtn = document.getElementById("themeBtn");
const themeBtnText = document.getElementById("themeBtnText");
const themeOverlay = document.getElementById("themeOverlay");
const themeList = document.getElementById("themeList");
const themeClose = document.getElementById("themeClose");
const themeSheetTitle = document.getElementById("themeSheetTitle");

// ===== Элементы инструментов =====
const toolsBtn = document.getElementById("toolsBtn");
const toolsDropdown = document.getElementById("toolsDropdown");
const toolsChev = document.getElementById("toolsChev");
const toolsBtnText = document.getElementById("toolsBtnText");

const toolRemoveBgText = document.getElementById("toolRemoveBgText");
const toolTextFromImageText = document.getElementById("toolTextFromImageText");
const toolSelfieFiltersText = document.getElementById("toolSelfieFiltersText");
const toolMusicText = document.getElementById("toolMusicText");
const toolMemeText = document.getElementById("toolMemeText");
const toolQrText = document.getElementById("toolQrText");

// ===== i18n словарь =====
const I18N = {
  ru: { 
    chat: "Чат с ИИ", 
    img: "Генерация картинки", 
    tools: "🔧 Инструменты",
    removeBg: "Удаление фона",
    textFromImage: "Текст с фото",
    selfieFilters: "Селфи фильтры",
    music: "Создание музыки",
    meme: "Создание мемов",
    qr: "QR коды",
    sub: "Быстрые ответы • Память • Заметки", 
    ver: "miniapp v3", 
    lang: "Язык интерфейса", 
    sheetLang: "Язык",
    sheetTheme: "Оформление",
    theme: "Тема",
    style: "Стиль",
    styleNormal: "Обычный",
    colors: {
      blue: "Синий",
      black: "Черный",
      purple: "Фиолетовый",
      green: "Зеленый",
      gray: "Серый",
      normal: "Обычный"
    }
  },
  kk: { 
    chat: "AI чат", 
    img: "Сурет генерациясы",
    tools: "🔧 Құралдар",
    removeBg: "Фонды кетіру",
    textFromImage: "Фотонан мәтін",
    selfieFilters: "Селфи фильтрлер",
    music: "Музыка жасау",
    meme: "Мем жасау",
    qr: "QR кодтар",
    sub: "Жылдам жауаптар • Есте сақтау • Жазбалар", 
    ver: "miniapp v3", 
    lang: "Тіл", 
    sheetLang: "Тіл",
    sheetTheme: "Безендіру",
    theme: "Тақырып",
    style: "Стиль",
    styleNormal: "Қарапайым",
    colors: {
      blue: "Көк",
      black: "Қара",
      purple: "Күлгін",
      green: "Жасыл",
      gray: "Сұр",
      normal: "Қарапайым"
    }
  },
  en: { 
    chat: "AI Chat", 
    img: "Image generation",
    tools: "🔧 Tools",
    removeBg: "Remove Background",
    textFromImage: "Text from Image",
    selfieFilters: "Selfie Filters",
    music: "Create Music",
    meme: "Create Meme",
    qr: "QR Codes",
    sub: "Fast replies • Memory • Notes", 
    ver: "miniapp v3", 
    lang: "Language", 
    sheetLang: "Language",
    sheetTheme: "Style",
    theme: "Theme",
    style: "Style",
    styleNormal: "Normal",
    colors: {
      blue: "Blue",
      black: "Black",
      purple: "Purple",
      green: "Green",
      gray: "Gray",
      normal: "Normal"
    }
  },
  tr: { 
    chat: "Yapay Zekâ Sohbet", 
    img: "Görsel üretimi",
    tools: "🔧 Araçlar",
    removeBg: "Arka planı kaldır",
    textFromImage: "Fotodan yazı",
    selfieFilters: "Selfie filtreleri",
    music: "Müzik oluştur",
    meme: "Meme oluştur",
    qr: "QR kodlar",
    sub: "Hızlı yanıtlar • Hafıza • Notlar", 
    ver: "miniapp v3", 
    lang: "Dil", 
    sheetLang: "Dil",
    sheetTheme: "Tema",
    theme: "Tema",
    style: "Stil",
    styleNormal: "Normal",
    colors: {
      blue: "Mavi",
      black: "Siyah",
      purple: "Mor",
      green: "Yeşil",
      gray: "Gri",
      normal: "Normal"
    }
  },
  uk: { 
    chat: "AI чат", 
    img: "Генерація зображень",
    tools: "🔧 Інструменти",
    removeBg: "Видалити фон",
    textFromImage: "Текст з фото",
    selfieFilters: "Селфі фільтри",
    music: "Створити музику",
    meme: "Створити мем",
    qr: "QR коди",
    sub: "Швидкі відповіді • Пам’ять • Нотатки", 
    ver: "miniapp v3", 
    lang: "Мова", 
    sheetLang: "Мова",
    sheetTheme: "Оформлення",
    theme: "Тема",
    style: "Стиль",
    styleNormal: "Звичайний",
    colors: {
      blue: "Синій",
      black: "Чорний",
      purple: "Фіолетовий",
      green: "Зелений",
      gray: "Сірий",
      normal: "Звичайний"
    }
  },
  fr: { 
    chat: "Chat IA", 
    img: "Génération d'image",
    tools: "🔧 Outils",
    removeBg: "Supprimer l'arrière-plan",
    textFromImage: "Texte depuis l'image",
    selfieFilters: "Filtres selfie",
    music: "Créer de la musique",
    meme: "Créer un mème",
    qr: "Codes QR",
    sub: "Réponses rapides • Mémoire • Notes", 
    ver: "miniapp v3", 
    lang: "Langue", 
    sheetLang: "Langue",
    sheetTheme: "Style",
    theme: "Thème",
    style: "Style",
    styleNormal: "Normal",
    colors: {
      blue: "Bleu",
      black: "Noir",
      purple: "Violet",
      green: "Vert",
      gray: "Gris",
      normal: "Normal"
    }
  },
};

// ===== Списки =====
const LANGS = [
  { code: "ru", label: "Русский (RU)" },
  { code: "kk", label: "Қазақша (KZ)" },
  { code: "en", label: "English (EN)" },
  { code: "tr", label: "Türkçe (TR)" },
  { code: "uk", label: "Українська (UA)" },
  { code: "fr", label: "Français (FR)" },
];

const THEMES = [
  { code: "blue", type: "theme", label: { ru: "Синий", kk: "Көк", en: "Blue", tr: "Mavi", uk: "Синій", fr: "Bleu" } },
  { code: "black", type: "theme", label: { ru: "Черный", kk: "Қара", en: "Black", tr: "Siyah", uk: "Чорний", fr: "Noir" } },
  { code: "purple", type: "theme", label: { ru: "Фиолетовый", kk: "Күлгін", en: "Purple", tr: "Mor", uk: "Фіолетовий", fr: "Violet" } },
  { code: "green", type: "theme", label: { ru: "Зеленый", kk: "Жасыл", en: "Green", tr: "Yeşil", uk: "Зелений", fr: "Vert" } },
  { code: "gray", type: "theme", label: { ru: "Серый", kk: "Сұр", en: "Gray", tr: "Gri", uk: "Сірий", fr: "Gris" } },
  { code: "normal", type: "style", label: { ru: "Обычный", kk: "Қарапайым", en: "Normal", tr: "Normal", uk: "Звичайний", fr: "Normal" } },
];

// ===== helpers =====
function getSavedLang(){
  try{ return localStorage.getItem(STORAGE_LANG) || "ru"; }
  catch(e){ return "ru"; }
}

function saveLang(lang){
  try{ localStorage.setItem(STORAGE_LANG, lang); }catch(e){}
}

function getSavedTheme(){
  try{ return localStorage.getItem(STORAGE_THEME) || "blue"; }
  catch(e){ return "blue"; }
}

function getSavedStyle(){
  try{ return localStorage.getItem(STORAGE_STYLE) || ""; }
  catch(e){ return ""; }
}

function saveTheme(theme){
  try{ localStorage.setItem(STORAGE_THEME, theme); }catch(e){}
}

function saveStyle(style){
  try{ localStorage.setItem(STORAGE_STYLE, style); }catch(e){}
}

function applyTheme(theme){
  document.documentElement.setAttribute("data-theme", theme || "blue");
}

function applyStyle(style){
  if (style) {
    document.documentElement.setAttribute("data-style", style);
  } else {
    document.documentElement.removeAttribute("data-style");
  }
}

// ===== Уведомления =====
function showNotification(message) {
  setTimeout(() => {
    const oldToasts = document.querySelectorAll('.toast-notification');
    oldToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }, 500);
}

// ===== Обновление ссылок =====
function updateLinks(lang, theme, style){
  if (chatBtn) {
    chatBtn.href = `./chat.html?v=2&lang=${encodeURIComponent(lang)}&theme=${encodeURIComponent(theme)}&style=${encodeURIComponent(style)}`;
  }
  if (imgBtn) {
    imgBtn.href = `./image.html?v=1&lang=${encodeURIComponent(lang)}&theme=${encodeURIComponent(theme)}&style=${encodeURIComponent(style)}`;
  }
  
  const toolLinks = document.querySelectorAll('.tool-item');
  toolLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && !href.includes('?')) {
      link.href = `${href}?lang=${encodeURIComponent(lang)}&theme=${encodeURIComponent(theme)}&style=${encodeURIComponent(style)}`;
    }
  });
}

// ===== Обновление UI =====
function updateUILanguage(lang){
  const t = I18N[lang] || I18N.ru;
  
  if (chatBtn) chatBtn.textContent = t.chat;
  if (imgBtn) imgBtn.textContent = t.img;
  if (toolsBtnText) toolsBtnText.innerHTML = t.tools;
  if (toolRemoveBgText) toolRemoveBgText.textContent = t.removeBg;
  if (toolTextFromImageText) toolTextFromImageText.textContent = t.textFromImage;
  if (toolSelfieFiltersText) toolSelfieFiltersText.textContent = t.selfieFilters;
  if (toolMusicText) toolMusicText.textContent = t.music;
  if (toolMemeText) toolMemeText.textContent = t.meme;
  if (toolQrText) toolQrText.textContent = t.qr;
  if (subText) subText.textContent = t.sub;
  if (verText) verText.textContent = t.ver;
  if (langTitle) langTitle.textContent = t.lang;
  if (langSheetTitle) langSheetTitle.textContent = t.sheetLang;
  if (themeSheetTitle) themeSheetTitle.textContent = t.sheetTheme;
  
  const foundLang = LANGS.find(x => x.code === lang);
  if (langBtnText) {
    langBtnText.textContent = foundLang ? foundLang.label : "Русский (RU)";
  }
  
  const currentTheme = getSavedTheme();
  const currentStyle = getSavedStyle();
  
  if (themeBtnText) {
    if (currentStyle === "normal") {
      themeBtnText.textContent = `${t.style}: ${t.styleNormal}`;
    } else {
      themeBtnText.textContent = `${t.theme}: ${getThemeLabel(currentTheme, lang)}`;
    }
  }
  
  paintSelectedLang(lang);
  updateThemeList(lang);
}

function getThemeLabel(themeCode, lang){
  const theme = THEMES.find(t => t.code === themeCode);
  if (!theme) return themeCode;
  return theme.label[lang] || theme.label.ru || themeCode;
}

function updateThemeList(lang){
  if (!themeList) return;
  
  const items = themeList.querySelectorAll('.themeItem');
  items.forEach(item => {
    const code = item.getAttribute('data-theme');
    const type = item.getAttribute('data-type');
    const theme = THEMES.find(t => t.code === code);
    if (theme) {
      const labelSpan = item.querySelector('.theme-label');
      if (labelSpan) {
        labelSpan.textContent = theme.label[lang] || theme.label.ru;
      }
    }
  });
}

function paintSelectedLang(lang){
  if (!langList) return;
  const items = langList.querySelectorAll(".langItem");
  items.forEach(btn => {
    const code = btn.getAttribute("data-lang");
    btn.classList.toggle("selected", code === lang);
  });
}

// ===== ИСПРАВЛЕННАЯ ФУНКЦИЯ ГАЛОЧЕК =====
function paintSelectedTheme(theme, style){
  if (!themeList) return;
  
  const items = themeList.querySelectorAll(".themeItem");
  items.forEach(btn => {
    const code = btn.getAttribute("data-theme");
    const type = btn.getAttribute("data-type");
    
    if (type === "style") {
      // Для "Обычный" - галочка если выбран style
      btn.classList.toggle("selected", code === style);
    } else {
      // Для цветных тем - галочка если выбрана тема И style пустой
      btn.classList.toggle("selected", code === theme && !style);
    }
  });
}

// ===== ИСПРАВЛЕННАЯ УСТАНОВКА ТЕМЫ/СТИЛЯ =====
function setTheme(themeCode){
  console.log("setTheme:", themeCode);
  
  const theme = THEMES.find(t => t.code === themeCode);
  
  if (theme.type === "style") {
    // Если выбрали "Обычный"
    applyStyle(themeCode);
    saveStyle(themeCode);
    // Сбрасываем цветную тему на дефолтную
    applyTheme("blue");
    saveTheme("blue");
  } else {
    // Если выбрали цветную тему
    applyTheme(themeCode);
    saveTheme(themeCode);
    // Убираем обычный стиль
    applyStyle("");
    saveStyle("");
  }
  
  // Обновляем галочки
  paintSelectedTheme(getSavedTheme(), getSavedStyle());
  
  const currentLang = getSavedLang();
  const t = I18N[currentLang] || I18N.ru;
  
  if (themeBtnText) {
    if (themeCode === "normal") {
      themeBtnText.textContent = `${t.style}: ${t.styleNormal}`;
    } else {
      themeBtnText.textContent = `${t.theme}: ${getThemeLabel(themeCode, currentLang)}`;
    }
  }
  
  updateLinks(currentLang, getSavedTheme(), getSavedStyle());
  
  closeTheme();
  showNotification(`🎨 ${t.sheetTheme}: ${theme.label[currentLang] || theme.label.ru}`);
}

// ===== Логика выпадающего меню инструментов =====
function initToolsMenu() {
  if (!toolsBtn || !toolsDropdown || !toolsChev) return;
  
  let isOpen = false;
  try {
    isOpen = localStorage.getItem(STORAGE_TOOLS) === 'true';
  } catch(e) {}
  
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
    
    try {
      localStorage.setItem(STORAGE_TOOLS, isOpen);
    } catch(e) {}
  }
  
  toolsBtn.addEventListener('click', toggleTools);
  
  document.addEventListener('click', (e) => {
    if (isOpen && !toolsBtn.contains(e.target) && !toolsDropdown.contains(e.target)) {
      toggleTools(e);
    }
  });
  
  if (isOpen) {
    toolsDropdown.classList.add('open');
    toolsBtn.classList.add('active');
    toolsChev.classList.remove('rotate');
    toolsChev.textContent = '▲';
  }
}

// ===== Overlay controls =====
function openLang(){
  if (!langOverlay || !langBtn) return;
  langOverlay.classList.add("show");
  langOverlay.setAttribute("aria-hidden", "false");
  langBtn.setAttribute("aria-expanded", "true");
}

function closeLang(){
  if (!langOverlay || !langBtn) return;
  langOverlay.classList.remove("show");
  langOverlay.setAttribute("aria-hidden", "true");
  langBtn.setAttribute("aria-expanded", "false");
}

function openTheme(){
  if (!themeOverlay || !themeBtn) return;
  themeOverlay.classList.add("show");
  themeOverlay.setAttribute("aria-hidden", "false");
  themeBtn.setAttribute("aria-expanded", "true");
}

function closeTheme(){
  if (!themeOverlay || !themeBtn) return;
  themeOverlay.classList.remove("show");
  themeOverlay.setAttribute("aria-hidden", "true");
  themeBtn.setAttribute("aria-expanded", "false");
}

// ===== Сборка списков =====
function buildLangList(){
  if (!langList) return;
  
  langList.innerHTML = "";
  LANGS.forEach(lang => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "langItem";
    btn.setAttribute("data-lang", lang.code);
    btn.innerHTML = `<span>${lang.label}</span><span class="check">✓</span>`;
    btn.addEventListener("click", () => setLang(lang.code));
    langList.appendChild(btn);
  });
}

function buildThemeList(){
  if (!themeList) return;
  
  themeList.innerHTML = "";
  THEMES.forEach(theme => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "themeItem";
    btn.setAttribute("data-theme", theme.code);
    btn.setAttribute("data-type", theme.type);
    
    const currentLang = getSavedLang();
    const labelText = theme.label[currentLang] || theme.label.ru;
    btn.innerHTML = `<span class="theme-label">${labelText}</span><span class="check">✓</span>`;
    
    btn.addEventListener("click", () => setTheme(theme.code));
    themeList.appendChild(btn);
  });
}

// ===== Установка языка =====
function setLang(lang){
  console.log("setLang:", lang);
  
  saveLang(lang);
  updateUILanguage(lang);
  
  const currentTheme = getSavedTheme();
  const currentStyle = getSavedStyle();
  updateLinks(lang, currentTheme, currentStyle);
  
  closeLang();
  showNotification(`🌐 ${I18N[lang]?.sheetLang || "Language"}: ${LANGS.find(l => l.code === lang)?.label || lang}`);
}

// ===== Инициализация =====
function init(){
  buildLangList();
  buildThemeList();
  
  const savedLang = getSavedLang();
  const savedTheme = getSavedTheme();
  const savedStyle = getSavedStyle();
  
  applyTheme(savedTheme);
  applyStyle(savedStyle);
  
  updateUILanguage(savedLang);
  paintSelectedTheme(savedTheme, savedStyle);
  
  updateLinks(savedLang, savedTheme, savedStyle);
  
  initToolsMenu();
  
  if (langBtn) langBtn.addEventListener("click", openLang);
  if (langClose) langClose.addEventListener("click", closeLang);
  if (langOverlay) {
    langOverlay.addEventListener("click", (e) => {
      if (e.target === langOverlay) closeLang();
    });
  }
  
  if (themeBtn) themeBtn.addEventListener("click", openTheme);
  if (themeClose) themeClose.addEventListener("click", closeTheme);
  if (themeOverlay) {
    themeOverlay.addEventListener("click", (e) => {
      if (e.target === themeOverlay) closeTheme();
    });
  }
  
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeLang();
      closeTheme();
    }
  });
}

init();