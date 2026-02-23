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

// ===== i18n словарь =====
const I18N = {
  ru: { 
    chat: "Чат с ИИ", 
    img: "Генерация картинки", 
    sub: "Быстрые ответы • Память • Заметки", 
    ver: "miniapp v2", 
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
    sub: "Жылдам жауаптар • Есте сақтау • Жазбалар", 
    ver: "miniapp v2", 
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
    sub: "Fast replies • Memory • Notes", 
    ver: "miniapp v2", 
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
    sub: "Hızlı yanıtlar • Hafıza • Notlar", 
    ver: "miniapp v2", 
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
    sub: "Швидкі відповіді • Пам’ять • Нотатки", 
    ver: "miniapp v2", 
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
    sub: "Réponses rapides • Mémoire • Notes", 
    ver: "miniapp v2", 
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
    chatBtn.href = `./chat.html?v=2&lang=${encodeURIComponent(lang)}&theme=${encodeURIComponent(theme)}`;
  }
  if (imgBtn) {
    imgBtn.href = `./image.html?v=1&lang=${encodeURIComponent(lang)}&theme=${encodeURIComponent(theme)}`;
  }
}

// ===== Обновление UI =====
function updateUILanguage(lang){
  const t = I18N[lang] || I18N.ru;
  
  // Обновляем тексты
  if (chatBtn) chatBtn.textContent = t.chat;
  if (imgBtn) imgBtn.textContent = t.img;
  if (subText) subText.textContent = t.sub;
  if (verText) verText.textContent = t.ver;
  if (langTitle) langTitle.textContent = t.lang;
  if (langSheetTitle) langSheetTitle.textContent = t.sheetLang;
  if (themeSheetTitle) themeSheetTitle.textContent = t.sheetTheme;
  
  // Обновляем текст на кнопке языка
  const foundLang = LANGS.find(x => x.code === lang);
  if (langBtnText) {
    langBtnText.textContent = foundLang ? foundLang.label : "Русский (RU)";
  }
  
  // Обновляем текст на кнопке темы
  const currentTheme = getSavedTheme();
  if (themeBtnText) {
    themeBtnText.textContent = `${t.theme}: ${getThemeLabel(currentTheme, lang)}`;
  }
  
  // Обновляем выделение в списке языков
  paintSelectedLang(lang);
  
  // Обновляем список тем
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
    
    // Устанавливаем начальный язык (русский) при создании
    const currentLang = getSavedLang();
    const labelText = theme.label[currentLang] || theme.label.ru;
    btn.innerHTML = `<span class="theme-label">${labelText}</span><span class="check">✓</span>`;
    
    btn.addEventListener("click", () => setTheme(theme.code));
    themeList.appendChild(btn);
  });
}

// ===== Инициализация =====
function init(){
  // Сборка списков
  buildLangList();
  buildThemeList();
  
  // Загрузка сохраненных значений
  const savedLang = getSavedLang();
  const savedTheme = getSavedTheme();
  
  // Применение темы
  applyTheme(savedTheme);
  
  // Обновление UI
  updateUILanguage(savedLang);
  paintSelectedTheme(savedTheme);
  
  // Обновление ссылок
  updateLinks(savedLang, savedTheme);
  
  // Обработчики для языка
  if (langBtn) langBtn.addEventListener("click", openLang);
  if (langClose) langClose.addEventListener("click", closeLang);
  if (langOverlay) {
    langOverlay.addEventListener("click", (e) => {
      if (e.target === langOverlay) closeLang();
    });
  }
  
  // Обработчики для темы
  if (themeBtn) themeBtn.addEventListener("click", openTheme);
  if (themeClose) themeClose.addEventListener("click", closeTheme);
  if (themeOverlay) {
    themeOverlay.addEventListener("click", (e) => {
      if (e.target === themeOverlay) closeTheme();
    });
  }
  
  // Закрытие по Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeLang();
      closeTheme();
    }
  });
}

// Запуск
init();