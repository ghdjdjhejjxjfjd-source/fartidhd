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
    // Этот эндпоинт нужно добавить в api.py
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

// Одноразовое уведомление
function showOneTimeNotification(message, type = 'success') {
  // Проверяем, показывали ли уже это уведомление
  const notificationKey = `notification_${message}`;
  if (localStorage.getItem(notificationKey)) return;
  
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // Отмечаем что показали
  localStorage.setItem(notificationKey, 'true');
  
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

// ===== i18n =====
const I18N = {
  ru: { btn:"Чат с ИИ", img:"Генерация картинки", sub:"Быстрые ответы • Память • Заметки", ver:"miniapp v2", lang:"Язык интерфейса", sheet:"Язык" },
  kk: { btn:"AI чат", img:"Сурет генерациясы", sub:"Жылдам жауаптар • Есте сақтау • Жазбалар", ver:"miniapp v2", lang:"Тіл", sheet:"Тіл" },
  en: { btn:"AI Chat", img:"Image generation", sub:"Fast replies • Memory • Notes", ver:"miniapp v2", lang:"Language", sheet:"Language" },
  tr: { btn:"Yapay Zekâ Sohbet", img:"Görsel üretimi", sub:"Hızlı yanıtlar • Hafıza • Notlar", ver:"miniapp v2", lang:"Dil", sheet:"Dil" },
  uk: { btn:"AI чат", img:"Генерація зображень", sub:"Швидкі відповіді • Пам’ять • Нотатки", ver:"miniapp v2", lang:"Мова", sheet:"Мова" },
  fr: { btn:"Chat IA", img:"Génération d'image", sub:"Réponses rapides • Mémoire • Notes", ver:"miniapp v2", lang:"Langue", sheet:"Langue" },
};

const LANGS = [
  { code:"ru", label:"Русский (RU)" },
  { code:"kk", label:"Қазақша (KZ)" },
  { code:"en", label:"English (EN)" },
  { code:"tr", label:"Türkçe (TR)" },
  { code:"uk", label:"Українська (UA)" },
  { code:"fr", label:"Français (FR)" },
];

// ===== THEMES с ценами =====
const THEMES = [
  { code:"blue", label:"Синий", price: 0 },
  { code:"black", label:"Черный", price: 0 },
  { code:"purple", label:"Фиолетовый", price: 0 },
  { code:"green", label:"Зеленый", price: 0 },
  { code:"gray", label:"Серый", price: 0 },
  { code:"telegram", label:"Telegram стиль", price: 100 },
  { code:"ios", label:"iOS стиль", price: 100 },
];

function themeLabel(theme){
  const f = THEMES.find(x => x.code === theme);
  return f ? f.label : "Синий";
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

  setChatLink(lang, getSavedTheme());
  setImgLink(lang, getSavedTheme());
}

async function setTheme(theme){
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
      alert(`❌ Недостаточно звезд. Нужно ${themeData.price} ⭐`);
      return;
    }
    
    // Списываем звезды
    const success = await spendStars(themeData.price);
    if (!success) {
      alert("❌ Ошибка при покупке. Попробуйте позже.");
      return;
    }
    
    // Добавляем в купленные
    addPurchasedTheme(theme);
    
    // Показываем одноразовое уведомление
    showOneTimeNotification(`✅ Тема "${themeData.label}" активирована!`, 'success');
  }
  
  applyTheme(theme);
  saveTheme(theme);
  paintSelectedTheme(theme);

  setPillLabel(themeBtn, "Цвет: " + themeLabel(theme));

  setChatLink(getSavedLang(), theme);
  setImgLink(getSavedLang(), theme);
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
  
  const purchasedThemes = getPurchasedThemes();
  
  for (const x of THEMES){
    const b = document.createElement("button");
    b.type = "button";
    b.className = "themeItem";
    b.setAttribute("data-theme", x.code);
    
    // Для купленных тем цена не показывается
    const isPurchased = purchasedThemes.includes(x.code);
    const priceText = (x.price > 0 && !isPurchased) ? ` (${x.price} ⭐)` : "";
    
    b.innerHTML = `<span>${x.label}${priceText}</span><span class="check">✓</span>`;
    
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

setLang(getSavedLang());
setTheme(getSavedTheme());

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