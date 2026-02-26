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
    sheetTheme: "Цвет",
    theme: "Цвет",
    colors: {
      blue: "Синий",
      black: "Черный",
      purple: "Фиолетовый",
      green: "Зеленый",
      gray: "Серый"
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
    sheetTheme: "Түс",
    theme: "Түс",
    colors: {
      blue: "Көк",
      black: "Қара",
      purple: "Күлгін",
      green: "Жасыл",
      gray: "Сұр"
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
    sheetTheme: "Color",
    theme: "Color",
    colors: {
      blue: "Blue",
      black: "Black",
      purple: "Purple",
      green: "Green",
      gray: "Gray"
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
    sheetTheme: "Renk",
    theme: "Renk",
    colors: {
      blue: "Mavi",
      black: "Siyah",
      purple: "Mor",
      green: "Yeşil",
      gray: "Gri"
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
    sheetTheme: "Колір",
    theme: "Колір",
    colors: {
      blue: "Синій",
      black: "Чорний",
      purple: "Фіолетовий",
      green: "Зелений",
      gray: "Сірий"
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
    sheetTheme: "Couleur",
    theme: "Couleur",
    colors: {
      blue: "Bleu",
      black: "Noir",
      purple: "Violet",
      green: "Vert",
      gray: "Gris"
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
  { code: "blue", label: { ru: "Синий", kk: "Көк", en: "Blue", tr: "Mavi", uk: "Синій", fr: "Bleu" } },
  { code: "black", label: { ru: "Черный", kk: "Қара", en: "Black", tr: "Siyah", uk: "Чорний", fr: "Noir" } },
  { code: "purple", label: { ru: "Фиолетовый", kk: "Күлгін", en: "Purple", tr: "Mor", uk: "Фіолетовий", fr: "Violet" } },
  { code: "green", label: { ru: "Зеленый", kk: "Жасыл", en: "Green", tr: "Yeşil", uk: "Зелений", fr: "Vert" } },
  { code: "gray", label: { ru: "Серый", kk: "Сұр", en: "Gray", tr: "Gri", uk: "Сірий", fr: "Gris" } },
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

function saveTheme(theme){
  try{ localStorage.setItem(STORAGE_THEME, theme); }catch(e){}
}

function applyTheme(theme){
  document.documentElement.setAttribute("data-theme", theme || "blue");
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
function updateLinks(lang, theme){
  if (chatBtn) {
    chatBtn.setAttribute('onclick', `openPage('chat.html')`);
  }
  if (imgBtn) {
    imgBtn.setAttribute('onclick', `openPage('image.html')`);
  }
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
  if (themeBtnText) {
    themeBtnText.textContent = `${t.theme}: ${getThemeLabel(currentTheme, lang)}`;
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
    const labelSpan = item.querySelector('.theme-label');
    if (labelSpan) {
      labelSpan.textContent = getThemeLabel(code, lang);
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

function paintSelectedTheme(theme){
  if (!themeList) return;
  const items = themeList.querySelectorAll(".themeItem");
  items.forEach(btn => {
    const code = btn.getAttribute("data-theme");
    btn.classList.toggle("selected", code === theme);
  });
}

// ===== Установка языка =====
function setLang(lang){
  console.log("setLang:", lang);
  
  saveLang(lang);
  updateUILanguage(lang);
  
  const currentTheme = getSavedTheme();
  updateLinks(lang, currentTheme);
  
  closeLang();
  showNotification(`🌐 ${I18N[lang]?.sheetLang || "Language"}: ${LANGS.find(l => l.code === lang)?.label || lang}`);
}

// ===== Установка темы =====
function setTheme(theme){
  console.log("setTheme:", theme);
  
  applyTheme(theme);
  saveTheme(theme);
  paintSelectedTheme(theme);
  
  const currentLang = getSavedLang();
  const t = I18N[currentLang] || I18N.ru;
  
  if (themeBtnText) {
    themeBtnText.textContent = `${t.theme}: ${getThemeLabel(theme, currentLang)}`;
  }
  
  updateLinks(currentLang, theme);
  
  closeTheme();
  showNotification(`🎨 ${t.sheetTheme}: ${getThemeLabel(theme, currentLang)}`);
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
    
    const currentLang = getSavedLang();
    const labelText = theme.label[currentLang] || theme.label.ru;
    btn.innerHTML = `<span class="theme-label">${labelText}</span><span class="check">✓</span>`;
    
    btn.addEventListener("click", () => setTheme(theme.code));
    themeList.appendChild(btn);
  });
}

// ===== Инициализация =====
function init(){
  buildLangList();
  buildThemeList();
  
  const savedLang = getSavedLang();
  const savedTheme = getSavedTheme();
  
  applyTheme(savedTheme);
  
  updateUILanguage(savedLang);
  paintSelectedTheme(savedTheme);
  
  updateLinks(savedLang, savedTheme);
  
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

// Экспортируем функции для глобального доступа
window.openPage = function(page) {
  const lang = getSavedLang();
  const theme = getSavedTheme();
  const baseUrl = window.location.origin + window.location.pathname.replace('index.html', '');
  const fullUrl = `${baseUrl}${page}?lang=${encodeURIComponent(lang)}&theme=${encodeURIComponent(theme)}`;
  window.location.href = fullUrl;
};

window.openTool = function(toolPage) {
  const lang = getSavedLang();
  const theme = getSavedTheme();
  const baseUrl = window.location.origin + window.location.pathname.replace('index.html', '');
  const fullUrl = `${baseUrl}tools/${toolPage}?lang=${encodeURIComponent(lang)}&theme=${encodeURIComponent(theme)}`;
  window.location.href = fullUrl;
};