// docs/js/chat.js
import { askAI, getStarsBalance, clearAIMemory } from "./api.js";
import { tg } from "./telegram.js";

export const STORAGE_KEY = "chat_history_v1";

// Функция для получения языка из URL
function getLangFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  const lang = urlParams.get('lang');
  if (lang) {
    try {
      localStorage.setItem("miniapp_lang_v1", lang);
      console.log("Language from URL saved:", lang);
    } catch(e) {}
    return lang;
  }
  return null;
}

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
      // Увеличил лимит истории до 200 сообщений для лучшей памяти
      if (history.length > 200) history = history.slice(-200);
      saveHistory(history);
    }
  }

  function getLang(){
    try{
      const urlLang = getLangFromUrl();
      if (urlLang) {
        console.log("Using language from URL:", urlLang);
        return urlLang;
      }
      
      const stored = localStorage.getItem("miniapp_lang_v1");
      console.log("Using language from localStorage:", stored);
      return stored || "ru";
    }catch(e){
      console.error("Error getting language:", e);
      return "ru";
    }
  }

  function getPersona(){
    return localStorage.getItem("ai_persona") || "friendly";
  }

  function getStyle(){
    return localStorage.getItem("ai_style") || "steps";
  }

  // Обновленный helloText только для нужных языков
  function helloText(){
    const lang = getLang();
    console.log("Hello text language:", lang);
    
    const hellos = {
      "ru": "👋 Привет! Напиши что-нибудь — я на связи.",
      "kk": "👋 Сәлем! Бірдеңе жаз — мен осындамын.",
      "en": "👋 Hi! Write something — I'm here.",
      "tr": "👋 Merhaba! Bir şey yaz — buradayım.",
      "uk": "👋 Привіт! Напиши щось — я на зв'язку.",
      "fr": "👋 Salut ! Écris quelque chose — je suis là."
    };
    
    return hellos[lang] || hellos["ru"];
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

  // Улучшенная функция для построения промпта с полной историей
  function buildPrompt(userText){
    const lang = getLang();
    const persona = getPersona();
    const style = getStyle();
    
    // Берем до 50 последних сообщений для лучшего контекста
    const maxHistory = 50;
    const recentHistory = history.slice(-maxHistory);
    
    // Формируем полную историю разговора
    let conversationHistory = "";
    if (recentHistory.length > 0) {
      conversationHistory = "Previous conversation:\n";
      recentHistory.forEach(msg => {
        const role = msg.role === "user" ? "User" : "Assistant";
        conversationHistory += `${role}: ${msg.text}\n`;
      });
    } else {
      conversationHistory = "No previous conversation.\n";
    }

    // Язык для ответа
    const langNames = {
      "ru": "Russian",
      "kk": "Kazakh",
      "en": "English",
      "tr": "Turkish",
      "uk": "Ukrainian",
      "fr": "French"
    };
    const targetLang = langNames[lang] || "Russian";

    // Стиль ответа
    const styleDesc = {
      "short": "Keep answers VERY short (1-2 sentences).",
      "steps": "Answer step by step, structured.",
      "detail": "Answer in detail but without unnecessary words."
    }[style] || "Answer naturally.";

    // Характер с усиленными инструкциями
    const personaDesc = {
      "friendly": "You are FRIENDLY and WARM. Use smileys 🙂 in EVERY message. Ask how they are doing. Be consistently friendly throughout the entire conversation.",
      "fun": "You are FUN and HUMOROUS. Use lots of emojis 😄 😂 in EVERY message. Make jokes and be playful in EVERY response. Never be serious or boring.",
      "strict": "You are STRICT and SERIOUS. NEVER use emojis. Be short and direct in EVERY message. Only facts, no emotions. Be consistently strict.",
      "smart": "You are SMART and THOUGHTFUL. Use smart emojis 🧐 🤔 in EVERY message. Give detailed explanations. Be consistently intelligent."
    }[persona] || "You are friendly and warm.";

    return `${conversationHistory}
Current user message: ${userText}

IMPORTANT INSTRUCTIONS:
1. Language: Respond ONLY in ${targetLang}
2. Personality: ${personaDesc}
3. Style: ${styleDesc}
4. Remember the entire conversation history above
5. Be consistent with your personality in this response

Response:`;
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
      const lang = getLang();
      const persona = getPersona();
      const style = getStyle();
      
      console.log("Sending with lang:", lang, "persona:", persona, "style:", style);
      
      // Передаем параметры в askAI
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
      console.log("Server memory cleared");
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