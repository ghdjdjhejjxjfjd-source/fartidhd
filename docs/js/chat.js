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

// Функция для принудительной очистки чата (вызывается извне)
export function forceClearChat(controller) {
  if (controller) {
    controller.clearHistory(true);
  }
}

export function createChatController({ chatEl, inputEl, sendBtnEl }) {
  let history = loadHistory();
  let sending = false;
  let currentUserId = tg?.initDataUnsafe?.user?.id || 0;

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

  // Функция для автоматического расширения textarea
  function autoResizeTextarea() {
    if (inputEl && inputEl.tagName === 'TEXTAREA') {
      inputEl.style.height = 'auto';
      inputEl.style.height = (inputEl.scrollHeight) + 'px';
    }
  }

  // Функция для копирования текста
  async function copyText(text, button) {
    try {
      await navigator.clipboard.writeText(text);
      
      const originalSvg = button.innerHTML;
      button.classList.add('copied');
      
      button.innerHTML = `
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
        </svg>
      `;
      
      setTimeout(() => {
        button.classList.remove('copied');
        button.innerHTML = originalSvg;
      }, 2000);
      
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }

  // Функция для шаринга
  function shareText(text) {
    const message = encodeURIComponent(`🤖 InstaGroq AI:\n\n${text}\n\n— via @InstaGroqBot`);
    
    if (tg && tg.openTelegramLink) {
      tg.openTelegramLink(`https://t.me/share/url?url=&text=${message}`);
    } else {
      window.open(`https://t.me/share/url?url=&text=${message}`, '_blank');
    }
  }

  // Функция создания кнопок для сообщения
  function createMessageActions(messageText, messageId) {
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'message-actions';
    actionsDiv.setAttribute('data-message-id', messageId);
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'action-btn copy-btn';
    copyBtn.title = 'Копировать текст';
    copyBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16">
        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
      </svg>
    `;
    copyBtn.onclick = (e) => {
      e.stopPropagation();
      copyText(messageText, copyBtn);
    };
    
    const shareBtn = document.createElement('button');
    shareBtn.className = 'action-btn share-btn';
    shareBtn.title = 'Поделиться';
    shareBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16">
        <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L7.04 9.81C6.5 9.31 5.79 9 5 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
      </svg>
    `;
    shareBtn.onclick = (e) => {
      e.stopPropagation();
      shareText(messageText);
    };
    
    actionsDiv.appendChild(copyBtn);
    actionsDiv.appendChild(shareBtn);
    
    return actionsDiv;
  }

  function add(type, text, persist=true){
    const wrapper = document.createElement('div');
    wrapper.className = `msg-wrapper ${type}`;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `msg ${type}`;
    messageDiv.textContent = text;
    
    wrapper.appendChild(messageDiv);
    
    if (type === 'bot') {
      const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      wrapper.setAttribute('data-message-id', messageId);
      
      const actions = createMessageActions(text, messageId);
      wrapper.appendChild(actions);
      
      let hideTimeout;
      wrapper.addEventListener('mouseenter', () => {
        clearTimeout(hideTimeout);
        actions.classList.add('show');
      });
      
      wrapper.addEventListener('mouseleave', () => {
        hideTimeout = setTimeout(() => {
          if (!actions.matches(':hover')) {
            actions.classList.remove('show');
          }
        }, 300);
      });
      
      actions.addEventListener('mouseenter', () => {
        clearTimeout(hideTimeout);
      });
      
      actions.addEventListener('mouseleave', () => {
        hideTimeout = setTimeout(() => {
          actions.classList.remove('show');
        }, 300);
      });
    }
    
    chatEl.appendChild(wrapper);
    chatEl.scrollTop = chatEl.scrollHeight;

    if (persist) {
      history.push({ role: type === "user" ? "user" : "assistant", text: String(text || "") });
      if (history.length > 200) history = history.slice(-200);
      saveHistory(history);
    }
  }

  function getLang(){
    try{
      const urlLang = getLangFromUrl();
      if (urlLang) {
        return urlLang;
      }
      const stored = localStorage.getItem("miniapp_lang_v1");
      return stored || "ru";
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

  // Функция очистки истории
  async function clearHistory(skipConfirm = false) {
    if (!skipConfirm) {
      const confirmed = await confirmClear();
      if (!confirmed) return false;
    }
    
    history = [];
    saveHistory(history);
    try {
      await clearAIMemory();
    } catch (e) {
      console.error("Failed to clear server memory:", e);
    }
    chatEl.innerHTML = "";
    add("bot", helloText(), true);
    return true;
  }

  // ✅ ПРОСТАЯ ФУНКЦИЯ ПРОВЕРКИ СМЕНЫ РЕЖИМА (С ALERT)
  async function checkModeChange() {
    if (!currentUserId) return;
    
    try {
      const API_BASE = "https://fayrat-production.up.railway.app";
      const res = await fetch(`${API_BASE}/api/user/ai_mode/${currentUserId}`);
      
      if (!res.ok) return;
      
      const data = await res.json();
      
      const currentMode = localStorage.getItem("current_ai_mode");
      if (currentMode && data.ai_mode !== currentMode) {
        // Режим изменился - очищаем чат
        await clearHistory(true);
        localStorage.setItem("current_ai_mode", data.ai_mode);
        // Показываем уведомление
        alert("🔄 Режим изменен. Чат очищен.");
      } else if (!currentMode) {
        localStorage.setItem("current_ai_mode", data.ai_mode);
      }
    } catch (err) {
      console.log("Mode check error:", err);
    }
  }

  function buildPrompt(userText){
    const lang = getLang();
    const persona = getPersona();
    const style = getStyle();
    
    const maxHistory = 20;
    const recentHistory = history.slice(-maxHistory);
    
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

    const langNames = {
      "ru": "Russian",
      "kk": "Kazakh",
      "en": "English",
      "tr": "Turkish",
      "uk": "Ukrainian",
      "fr": "French"
    };
    const targetLang = langNames[lang] || "Russian";

    const styleDesc = {
      "short": "Keep answers VERY short (1-2 sentences).",
      "steps": "Answer step by step, structured.",
      "detail": "Answer in detail but without unnecessary words."
    }[style] || "Answer naturally.";

    const personaDesc = {
      "friendly": "You are FRIENDLY and WARM. Use smileys 🙂 in EVERY message. Ask how they are doing.",
      "fun": "You are FUN and HUMOROUS. Use lots of emojis 😄 😂 in EVERY message. Make jokes and be playful.",
      "strict": "You are STRICT and SERIOUS. NEVER use emojis. Be short and direct. Only facts.",
      "smart": "You are SMART and THOUGHTFUL. Use smart emojis 🧐 🤔 in EVERY message. Give detailed explanations."
    }[persona] || "You are friendly and warm.";

    return `${conversationHistory}
Current user message: ${userText}

IMPORTANT INSTRUCTIONS:
1. Language: Respond ONLY in ${targetLang}
2. Personality: ${personaDesc}
3. Style: ${styleDesc}
4. Remember the entire conversation history above

Response:`;
  }

  async function send(){
    const t = inputEl.value.trim();
    if(!t || sending) return;

    sending = true;
    sendBtnEl.disabled = true;

    add("user", t, true);
    inputEl.value = "";
    
    if (inputEl.tagName === 'TEXTAREA') {
      inputEl.style.height = 'auto';
    }
    
    addTyping();

    try{
      const lang = getLang();
      const persona = getPersona();
      const style = getStyle();
      
      const answer = await askAI(t, lang, persona, style);

      removeTyping();

      const out = (answer || "").trim();
      add("bot", out || "…", true);
      
      await updateMenuBalance();
      
      // Проверяем режим после каждого ответа
      await checkModeChange();
      
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
    
    if (inputEl.tagName === 'TEXTAREA') {
      inputEl.addEventListener('input', autoResizeTextarea);
    }
    
    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });

    chatEl.addEventListener("pointerdown", () => {
      if (document.activeElement === inputEl) inputEl.blur();
    });
    
    // Проверяем режим при загрузке
    setTimeout(checkModeChange, 1000);
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