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

// ===== DOM =====
const chatBtn = document.getElementById("chatBtn");
const subText = document.getElementById("subText");
const verText = document.getElementById("verText");
const langTitle = document.getElementById("langTitle");

const langBtn = document.getElementById("langBtn");
const langOverlay = document.getElementById("langOverlay");
const langList = document.getElementById("langList");
const langClose = document.getElementById("langClose");
const langSheetTitle = document.getElementById("langSheetTitle");

const imgBtn = document.getElementById("imgBtn");

const themeBtn = document.getElementById("themeBtn");
const themeOverlay = document.getElementById("themeOverlay");
const themeList = document.getElementById("themeList");
const themeClose = document.getElementById("themeClose");
const themeSheetTitle = document.getElementById("themeSheetTitle");

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

// Уведомление - показывается сразу
function showNotification(message) {
  console.log("🔔 Уведомление:", message);
  
  // Проверяем что мы на главной странице
  if (!window.location.pathname.includes('index.html') && window.location.pathname !== '/') {
    console.log("Не главная страница, уведомление не показываем");
    return;
  }
  
  // Удаляем старые уведомления
  const oldToasts = document.querySelectorAll('.toast-notification');
  oldToasts.forEach(toast => toast.remove());
  
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.8);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 30px;
    padding: 12px 24px;
    color: white;
    font-weight: 600;
    backdrop-filter: blur(10px);
    z-index: 100000;
    animation: slideDown 0.3s ease, fadeOut 0.3s ease 2.7s forwards;
  `;
  
  document.body.appendChild(toast);
  console.log("✅ Уведомление добавлено в DOM");
  
  setTimeout(() => {
    toast.remove();
    console.log("🗑️ Уведомление удалено");
  }, 3000);
}

// Добавляем анимации
const style = document.createElement('style');
style.textContent = `
  @keyframes slideDown {
    from {
      transform: translate(-50%, -100%);
      opacity: 0;
    }
    to {
      transform: translate(-50%, 0);
      opacity: 1;
    }
  }
  @keyframes fadeOut {
    to {
      opacity: 0;
      transform: translate(-50%, -20px);
    }
  }
`;
document.head.appendChild(style);

function setPillLabel(btn, text){
  if (!btn) return;
  
  let textNode = null;
  for (const n of btn.childNodes) {
    if (n && n.nodeType === Node.TEXT_NODE) { textNode = n; break; }
  }

  if (!textNode) {
    textNode = document.createTextNode("");
    btn.insertBefore(textNode, btn.firstChild);
  }

  textNode.nodeValue = text + " ";
}

function setChatLink(lang, theme){
  if (!chatBtn) return;
  const baseHref = "./chat.html?v=2";
  chatBtn.href = baseHref
    + "&lang=" + encodeURIComponent(lang)
    + "&theme=" + encodeURIComponent(theme);
}

function setImgLink(lang, theme){
  if (!imgBtn) return;
  const baseHref = "./image.html?v=1";
  imgBtn.href = baseHref
    + "&lang=" + encodeURIComponent(lang)
    + "&theme=" + encodeURIComponent(theme);
}

// ===== i18n =====
const I18N = {
  ru: { 
    btn:"Чат с ИИ", 
    img:"Генерация картинки", 
    sub:"Быстрые ответы • Память • Заметки", 
    ver:"miniapp v2", 
    lang:"Язык интерфейса", 
    sheet:"Язык",
    theme_title: "Цвет",
    colors: {
      blue: "Синий",
      black: "Черный",
      purple: "Фиолетовый",
      green: "Зеленый",
      gray: "Серый"
    }
  },
  kk: { 
    btn:"AI чат", 
    img:"Сурет генерациясы", 
    sub:"Жылдам жауаптар • Есте сақтау • Жазбалар", 
    ver:"miniapp v2", 
    lang:"Тіл", 
    sheet:"Тіл",
    theme_title: "Түс",
    colors: {
      blue: "Көк",
      black: "Қара",
      purple: "Күлгін",
      green: "Жасыл",
      gray: "Сұр"
    }
  },
  en: { 
    btn:"AI Chat", 
    img:"Image generation", 
    sub:"Fast replies • Memory • Notes", 
    ver:"miniapp v2", 
    lang:"Language", 
    sheet:"Language",
    theme_title: "Color",
    colors: {
      blue: "Blue",
      black: "Black",
      purple: "Purple",
      green: "Green",
      gray: "Gray"
    }
  },
  tr: { 
    btn:"Yapay Zekâ Sohbet", 
    img:"Görsel üretimi", 
    sub:"Hızlı yanıtlar • Hafıza • Notlar", 
    ver:"miniapp v2", 
    lang:"Dil", 
    sheet:"Dil",
    theme_title: "Renk",
    colors: {
      blue: "Mavi",
      black: "Siyah",
      purple: "Mor",
      green: "Yeşil",
      gray: "Gri"
    }
  },
  uk: { 
    btn:"AI чат", 
    img:"Генерація зображень", 
    sub:"Швидкі відповіді • Пам’ять • Нотатки", 
    ver:"miniapp v2", 
    lang:"Мова", 
    sheet:"Мова",
    theme_title: "Колір",
    colors: {
      blue: "Синій",
      black: "Чорний",
      purple: "Фіолетовий",
      green: "Зелений",
      gray: "Сірий"
    }
  },
  fr: { 
    btn:"Chat IA", 
    img:"Génération d'image", 
    sub:"Réponses rapides • Mémoire • Notes", 
    ver:"miniapp v2", 
    lang:"Langue", 
    sheet:"Langue",
    theme_title: "Couleur",
    colors: {
      blue: "Bleu",
      black: "Noir",
      purple: "Violet",
      green: "Vert",
      gray: "Gris"
    }
  },
};

const LANGS = [
  { code:"ru", label:"Русский (RU)" },
  { code:"kk", label:"Қазақша (KZ)" },
  { code:"en", label:"English (EN)" },
  { code:"tr", label:"Türkçe (TR)" },
  { code:"uk", label:"Українська (UA)" },
  { code:"fr", label:"Français (FR)" },
];

const LANG_NAMES = {
  ru: "Русский",
  kk: "Қазақша",
  en: "English",
  tr: "Türkçe",
  uk: "Українська",
  fr: "Français"
};

const THEMES = [
  { code:"blue", label: "Синий" },
  { code:"black", label: "Черный" },
  { code:"purple", label: "Фиолетовый" },
  { code:"green", label: "Зеленый" },
  { code:"gray", label: "Серый" }
];

function themeLabel(theme, lang = "ru"){
  const t = I18N[lang] || I18N.ru;
  return t.colors[theme] || theme;
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

function updateThemeList(lang) {
  if (!themeList) return;
  
  const t = I18N[lang] || I18N.ru;
  
  if (themeSheetTitle) {
    themeSheetTitle.textContent = t.theme_title;
  }
  
  const items = themeList.querySelectorAll(".themeItem");
  items.forEach(btn => {
    const code = btn.getAttribute("data-theme");
    const label = t.colors[code] || code;
    const span = btn.querySelector("span:first-child");
    if (span) {
      span.textContent = label;
    }
  });
}

function setLang(lang){
  console.log("setLang called with:", lang);
  
  const t = I18N[lang] || I18N.ru;

  // Обновляем тексты
  if (chatBtn) chatBtn.textContent = t.btn;
  if (imgBtn) imgBtn.textContent = t.img;
  if (subText) subText.textContent = t.sub;
  if (verText) verText.textContent = t.ver;
  if (langTitle) langTitle.textContent = t.lang;
  if (langSheetTitle) langSheetTitle.textContent = t.sheet;

  const found = LANGS.find(x => x.code === lang);
  setPillLabel(langBtn, found ? found.label : "Русский (RU)");

  saveLang(lang);
  paintSelectedLang(lang);
  
  const currentTheme = getSavedTheme();
  setPillLabel(themeBtn, t.theme_title + ": " + themeLabel(currentTheme, lang));
  
  if (themeSheetTitle) {
    themeSheetTitle.textContent = t.theme_title;
  }
  updateThemeList(lang);

  setChatLink(lang, currentTheme);
  setImgLink(lang, currentTheme);
  
  // Закрываем оверлей
  closeLang();
  
  // ПОКАЗЫВАЕМ УВЕДОМЛЕНИЕ СРАЗУ ПОСЛЕ ЗАКРЫТИЯ
  setTimeout(() => {
    showNotification(`🌐 Язык изменен на ${LANG_NAMES[lang] || lang}`);
  }, 100);
}

function setTheme(theme){
  console.log("setTheme called with:", theme);
  
  const currentLang = getSavedLang();
  const t = I18N[currentLang] || I18N.ru;
  
  applyTheme(theme);
  saveTheme(theme);
  paintSelectedTheme(theme);

  setPillLabel(themeBtn, t.theme_title + ": " + themeLabel(theme, currentLang));

  setChatLink(currentLang, theme);
  setImgLink(currentLang, theme);
  
  // Закрываем оверлей
  closeTheme();
  
  // ПОКАЗЫВАЕМ УВЕДОМЛЕНИЕ СРАЗУ ПОСЛЕ ЗАКРЫТИЯ
  setTimeout(() => {
    showNotification(`🎨 Тема изменена на ${themeLabel(theme, currentLang)}`);
  }, 100);
}

// ===== overlays =====
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

function buildLangList(){
  if (!langList) return;
  langList.innerHTML = "";
  for (const x of LANGS){
    const b = document.createElement("button");
    b.type = "button";
    b.className = "langItem";
    b.setAttribute("data-lang", x.code);
    b.innerHTML = `<span>${x.label}</span><span class="check">✓</span>`;
    b.addEventListener("click", () => setLang(x.code));
    langList.appendChild(b);
  }
}

function buildThemeList(){
  if (!themeList) return;
  themeList.innerHTML = "";
  
  const currentLang = getSavedLang();
  const t = I18N[currentLang] || I18N.ru;
  
  for (const x of THEMES){
    const b = document.createElement("button");
    b.type = "button";
    b.className = "themeItem";
    b.setAttribute("data-theme", x.code);
    
    const label = t.colors[x.code] || x.code;
    b.innerHTML = `<span>${label}</span><span class="check">✓</span>`;
    
    b.addEventListener("click", () => setTheme(x.code));
    themeList.appendChild(b);
  }
  
  if (themeSheetTitle) {
    themeSheetTitle.textContent = t.theme_title;
  }
}

// ===== init =====
buildLangList();
buildThemeList();

const savedLang = getSavedLang();
const savedTheme = getSavedTheme();

const t = I18N[savedLang] || I18N.ru;
if (chatBtn) chatBtn.textContent = t.btn;
if (imgBtn) imgBtn.textContent = t.img;
if (subText) subText.textContent = t.sub;
if (verText) verText.textContent = t.ver;
if (langTitle) langTitle.textContent = t.lang;
if (langSheetTitle) langSheetTitle.textContent = t.sheet;
if (themeSheetTitle) themeSheetTitle.textContent = t.theme_title;

const found = LANGS.find(x => x.code === savedLang);
setPillLabel(langBtn, found ? found.label : "Русский (RU)");
paintSelectedLang(savedLang);

applyTheme(savedTheme);
setPillLabel(themeBtn, t.theme_title + ": " + themeLabel(savedTheme, savedLang));
paintSelectedTheme(savedTheme);

setChatLink(savedLang, savedTheme);
setImgLink(savedLang, savedTheme);

// handlers
if (langBtn) langBtn.addEventListener("click", openLang);
if (langClose) langClose.addEventListener("click", closeLang);
if (langOverlay) langOverlay.addEventListener("click", (e) => {
  if (e.target === langOverlay) closeLang();
});

if (themeBtn) themeBtn.addEventListener("click", openTheme);
if (themeClose) themeClose.addEventListener("click", closeTheme);
if (themeOverlay) themeOverlay.addEventListener("click", (e) => {
  if (e.target === themeOverlay) closeTheme();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") { closeLang(); closeTheme(); }
});