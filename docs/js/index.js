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
const STORAGE_PURCHASED_THEMES = "purchased_themes_v1";
const STORAGE_LAST_LANG = "last_lang_v1";
const STORAGE_LAST_THEME = "last_theme_v1";

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

function getLastLang(){
  try{ return localStorage.getItem(STORAGE_LAST_LANG) || "ru"; }
  catch(e){ return "ru"; }
}
function saveLastLang(lang){
  try{ localStorage.setItem(STORAGE_LAST_LANG, lang); }catch(e){}
}

function getSavedTheme(){
  try{ return localStorage.getItem(STORAGE_THEME) || "blue"; }
  catch(e){ return "blue"; }
}
function saveTheme(theme){
  try{ localStorage.setItem(STORAGE_THEME, theme); }catch(e){}
}

function getLastTheme(){
  try{ return localStorage.getItem(STORAGE_LAST_THEME) || "blue"; }
  catch(e){ return "blue"; }
}
function saveLastTheme(theme){
  try{ localStorage.setItem(STORAGE_LAST_THEME, theme); }catch(e){}
}

// Купленные темы
function getPurchasedThemes() {
  try {
    const purchased = localStorage.getItem(STORAGE_PURCHASED_THEMES);
    return purchased ? JSON.parse(purchased) : [];
  } catch(e) {
    return [];
  }
}

function addPurchasedTheme(theme) {
  try {
    const purchased = getPurchasedThemes();
    if (!purchased.includes(theme)) {
      purchased.push(theme);
      localStorage.setItem(STORAGE_PURCHASED_THEMES, JSON.stringify(purchased));
    }
  } catch(e) {}
}

function applyTheme(theme){
  document.documentElement.setAttribute("data-theme", theme || "blue");
}

// Функция для получения баланса звезд
async function getStarsBalance() {
  try {
    const user = getTelegramUser();
    if (!user.tg_user_id) return 0;
    
    const API_BASE = "https://fayrat-production.up.railway.app";
    const r = await fetch(`${API_BASE}/api/stars/balance/${user.tg_user_id}`);
    if (r.ok) {
      const data = await r.json();
      return data.balance || 0;
    }
  } catch (e) {
    console.error("Error fetching balance:", e);
  }
  return 0;
}

// Функция для списания звезд
async function spendStars(amount) {
  try {
    const user = getTelegramUser();
    if (!user.tg_user_id) return false;
    
    const API_BASE = "https://fayrat-production.up.railway.app";
    const r = await fetch(`${API_BASE}/api/stars/spend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tg_user_id: user.tg_user_id,
        amount: amount
      })
    });
    return r.ok;
  } catch (e) {
    console.error("Error spending stars:", e);
    return false;
  }
}

function getTelegramUser(){
  const tg = window.Telegram?.WebApp;
  if (!tg || !tg.initDataUnsafe?.user) return {};

  const u = tg.initDataUnsafe.user;
  return {
    tg_user_id: u.id,
    tg_username: u.username || "—",
    tg_first_name: u.first_name || "—",
  };
}

// Уведомление (только при реальной смене)
function showNotification(message, type = 'success') {
  // Проверяем что мы на главной странице
  if (!window.location.pathname.includes('index.html') && window.location.pathname !== '/') {
    return;
  }
  
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

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

// ===== i18n с переводами для цветов =====
const I18N = {
  ru: { 
    btn:"Чат с ИИ", 
    img:"Генерация картинки", 
    sub:"Быстрые ответы • Память • Заметки", 
    ver:"miniapp v2", 
    lang:"Язык интерфейса", 
    sheet:"Язык",
    colors: {
      blue: "Синий",
      black: "Черный",
      purple: "Фиолетовый",
      green: "Зеленый",
      gray: "Серый",
      ios: "iOS стиль"
    },
    theme_title: "Цвет"
  },
  kk: { 
    btn:"AI чат", 
    img:"Сурет генерациясы", 
    sub:"Жылдам жауаптар • Есте сақтау • Жазбалар", 
    ver:"miniapp v2", 
    lang:"Тіл", 
    sheet:"Тіл",
    colors: {
      blue: "Көк",
      black: "Қара",
      purple: "Күлгін",
      green: "Жасыл",
      gray: "Сұр",
      ios: "iOS стилі"
    },
    theme_title: "Түс"
  },
  en: { 
    btn:"AI Chat", 
    img:"Image generation", 
    sub:"Fast replies • Memory • Notes", 
    ver:"miniapp v2", 
    lang:"Language", 
    sheet:"Language",
    colors: {
      blue: "Blue",
      black: "Black",
      purple: "Purple",
      green: "Green",
      gray: "Gray",
      ios: "iOS style"
    },
    theme_title: "Color"
  },
  tr: { 
    btn:"Yapay Zekâ Sohbet", 
    img:"Görsel üretimi", 
    sub:"Hızlı yanıtlar • Hafıza • Notlar", 
    ver:"miniapp v2", 
    lang:"Dil", 
    sheet:"Dil",
    colors: {
      blue: "Mavi",
      black: "Siyah",
      purple: "Mor",
      green: "Yeşil",
      gray: "Gri",
      ios: "iOS stili"
    },
    theme_title: "Renk"
  },
  uk: { 
    btn:"AI чат", 
    img:"Генерація зображень", 
    sub:"Швидкі відповіді • Пам’ять • Нотатки", 
    ver:"miniapp v2", 
    lang:"Мова", 
    sheet:"Мова",
    colors: {
      blue: "Синій",
      black: "Чорний",
      purple: "Фіолетовий",
      green: "Зелений",
      gray: "Сірий",
      ios: "iOS стиль"
    },
    theme_title: "Колір"
  },
  fr: { 
    btn:"Chat IA", 
    img:"Génération d'image", 
    sub:"Réponses rapides • Mémoire • Notes", 
    ver:"miniapp v2", 
    lang:"Langue", 
    sheet:"Langue",
    colors: {
      blue: "Bleu",
      black: "Noir",
      purple: "Violet",
      green: "Vert",
      gray: "Gris",
      ios: "Style iOS"
    },
    theme_title: "Couleur"
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

// Названия языков для уведомлений
const LANG_NAMES = {
  ru: "Русский",
  kk: "Қазақша",
  en: "English",
  tr: "Türkçe",
  uk: "Українська",
  fr: "Français"
};

// ===== THEMES =====
const THEMES = [
  { code:"blue", price: 0 },
  { code:"black", price: 0 },
  { code:"purple", price: 0 },
  { code:"green", price: 0 },
  { code:"gray", price: 0 },
  { code:"ios", price: 100 },
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

async function setLang(lang){
  const oldLang = getLastLang();
  const t = I18N[lang] || I18N.ru;

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
  
  // Обновляем кнопку темы с новым языком
  const currentTheme = getSavedTheme();
  setPillLabel(themeBtn, t.theme_title + ": " + themeLabel(currentTheme, lang));

  setChatLink(lang, currentTheme);
  setImgLink(lang, currentTheme);
  
  // Показываем уведомление ТОЛЬКО если язык реально изменился
  if (oldLang !== lang) {
    showNotification(`🌐 Язык изменен на ${LANG_NAMES[lang] || lang}`);
    saveLastLang(lang);
  }
}

async function setTheme(theme){
  const oldTheme = getLastTheme();
  const currentLang = getSavedLang();
  const t = I18N[currentLang] || I18N.ru;
  
  // Проверяем доступность темы
  const themeData = THEMES.find(t => t.code === theme);
  if (!themeData) return;
  
  // Проверяем куплена ли уже тема
  const purchasedThemes = getPurchasedThemes();
  const isPurchased = purchasedThemes.includes(theme);
  
  // Если тема платная и не куплена - пробуем купить
  if (themeData.price > 0 && !isPurchased) {
    const balance = await getStarsBalance();
    if (balance < themeData.price) {
      showNotification(`❌ Недостаточно звезд. Нужно ${themeData.price} ⭐`, 'error');
      return;
    }
    
    const success = await spendStars(themeData.price);
    if (!success) {
      showNotification("❌ Ошибка при покупке. Попробуйте позже.", 'error');
      return;
    }
    
    addPurchasedTheme(theme);
  }
  
  applyTheme(theme);
  saveTheme(theme);
  paintSelectedTheme(theme);

  setPillLabel(themeBtn, t.theme_title + ": " + themeLabel(theme, currentLang));

  setChatLink(currentLang, theme);
  setImgLink(currentLang, theme);
  
  // Показываем уведомление ТОЛЬКО если тема реально изменилась
  if (oldTheme !== theme) {
    showNotification(`🎨 Тема изменена на ${themeLabel(theme, currentLang)}`);
    saveLastTheme(theme);
  }
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
    b.addEventListener("click", () => {
      setLang(x.code);
      closeLang();
    });
    langList.appendChild(b);
  }
}

function buildThemeList(){
  if (!themeList) return;
  themeList.innerHTML = "";
  
  const currentLang = getSavedLang();
  const t = I18N[currentLang] || I18N.ru;
  const purchasedThemes = getPurchasedThemes();
  
  for (const x of THEMES){
    const b = document.createElement("button");
    b.type = "button";
    b.className = "themeItem";
    b.setAttribute("data-theme", x.code);
    
    const label = t.colors[x.code] || x.code;
    const isPurchased = purchasedThemes.includes(x.code);
    const priceText = (x.price > 0 && !isPurchased) ? ` (${x.price} ⭐)` : "";
    
    b.innerHTML = `<span>${label}${priceText}</span><span class="check">✓</span>`;
    
    b.addEventListener("click", () => {
      setTheme(x.code);
      closeTheme();
    });
    themeList.appendChild(b);
  }
}

// ===== init =====
buildLangList();
buildThemeList();

// Устанавливаем сохраненные значения без уведомлений
const savedLang = getSavedLang();
const savedTheme = getSavedTheme();

// Сохраняем как последние
saveLastLang(savedLang);
saveLastTheme(savedTheme);

// Применяем без уведомлений
const t = I18N[savedLang] || I18N.ru;
if (chatBtn) chatBtn.textContent = t.btn;
if (imgBtn) imgBtn.textContent = t.img;
if (subText) subText.textContent = t.sub;
if (verText) verText.textContent = t.ver;
if (langTitle) langTitle.textContent = t.lang;
if (langSheetTitle) langSheetTitle.textContent = t.sheet;

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