// docs/js/chat.js
import { askAI, getStarsBalance, clearAIMemory } from "./api.js";
import { tg } from "./telegram.js";

export const STORAGE_KEY = "chat_history_v1";

export function loadHistory(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  }catch(e){
    return [];
  }
}

export function saveHistory(list){
  try{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }catch(e){}
}

export function createChatController({ chatEl, inputEl, sendBtnEl }) {
  let history = loadHistory();
  let sending = false;

  const TYPING_ID = "typing-indicator";

  function removeTyping(){
    const el = document.getElementById(TYPING_ID);
    if (el) el.remove();
  }

  function addTyping(){
    removeTyping();
    const d = document.createElement("div");
    d.id = TYPING_ID;
    d.className = "msg bot typing";
    d.innerHTML = `<span class="typing-dots"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>`;
    chatEl.appendChild(d);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  function add(type, text, persist=true){
    const d = document.createElement("div");
    d.className = "msg " + type;
    d.textContent = text;
    chatEl.appendChild(d);
    chatEl.scrollTop = chatEl.scrollHeight;

    if (persist) {
      history.push({ role: type === "user" ? "user" : "assistant", text: String(text || "") });
      if (history.length > 120) history = history.slice(-120);
      saveHistory(history);
    }
  }

  function getLang(){
    try{
      return localStorage.getItem("miniapp_lang_v1") || "ru";
    }catch(e){
      return "ru";
    }
  }

  function getPersona(){
    return localStorage.getItem("ai_persona") || "friendly";
  }

  function getStyle(){
    return localStorage.getItem("ai_style") || "steps";
  }

  function helloText(){
    const lang = getLang();
    if (lang === "en") return "👋 Hi! Write something — I'm here.";
    if (lang === "kk") return "👋 Сәлем! Бірдеңе жаз — мен осындамын.";
    if (lang === "ky") return "👋 Салам! Бир нерсе жаз — мен бул жактамын.";
    if (lang === "tr") return "👋 Merhaba! Bir şey yaz — buradayım.";
    if (lang === "uz") return "👋 Salom! Biror narsa yoz — men shu yerdaman.";
    if (lang === "uk") return "👋 Привіт! Напиши щось — я на зв'язку.";
    if (lang === "de") return "👋 Hallo! Schreib etwas — ich bin da.";
    if (lang === "es") return "👋 ¡Hola! Escribe algo — estoy aquí.";
    if (lang === "fr") return "👋 Salut ! Écris quelque chose — je suis là.";
    return "👋 Привет! Напиши что-нибудь — я на связи.";
  }

  function renderFromHistory(){
    chatEl.innerHTML = "";
    if (!history.length){
      add("bot", helloText(), true);
      return;
    }
    for (const m of history){
      if (!m || !m.text) continue;
      add(m.role === "user" ? "user" : "bot", m.text, false);
    }
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  async function send(){
    const t = inputEl.value.trim();
    if(!t || sending) return;

    sending = true;
    sendBtnEl.disabled = true;

    add("user", t, true);
    inputEl.value = "";
    addTyping();

    try{
      // Получаем настройки
      const lang = getLang();
      const persona = getPersona();
      const style = getStyle();
      
      // Отправляем запрос с явным указанием языка
      const answer = await askAI(t, lang, persona, style);

      removeTyping();

      const out = (answer || "").trim();
      add("bot", out || "…", true);
      
      await updateMenuBalance();
      
    } catch(e){
      removeTyping();
      
      if (e.message.includes("Недостаточно звезд")) {
        add("bot", "❌ " + e.message + "\n\nКупите звезды в меню: нажмите ⭐ в главном меню.", true);
      } else {
        add("bot", "❌ Ошибка: " + (e?.message || e), true);
        console.error("Chat error:", e);
      }
    } finally{
      sending = false;
      sendBtnEl.disabled = false;
    }
  }

  async function updateMenuBalance() {
    try {
      const balance = await getStarsBalance();
      window.dispatchEvent(new CustomEvent('balanceUpdated', { detail: { balance } }));
    } catch (e) {
      console.error("Failed to update balance", e);
    }
  }

  function bindUI(){
    sendBtnEl.addEventListener("click", send);
    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });

    chatEl.addEventListener("pointerdown", () => {
      if (document.activeElement === inputEl) inputEl.blur();
    });
  }

  async function clearHistory(){
    history = [];
    saveHistory(history);
    try {
      await clearAIMemory();
    } catch (e) {
      console.error("Failed to clear server memory:", e);
    }
    chatEl.innerHTML = "";
    add("bot", helloText(), true);
  }

  async function confirmClear(){
    const msg = "Вы уверены, что хотите очистить чат?";
    if (tg && typeof tg.showConfirm === "function") {
      return await new Promise((resolve) => tg.showConfirm(msg, (ok) => resolve(Boolean(ok))));
    }
    return window.confirm(msg);
  }

  return {
    renderFromHistory,
    bindUI,
    send,
    clearHistory,
    confirmClear,
  };
}