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

  // Функция для копирования текста
  async function copyText(text, button) {
    try {
      await navigator.clipboard.writeText(text);
      
      // Меняем иконку на галочку
      const originalIcon = button.innerHTML;
      button.classList.add('copied');
      button.innerHTML = `✓`;
      
      // Через 2 секунды возвращаем обратно
      setTimeout(() => {
        button.classList.remove('copied');
        button.innerHTML = originalIcon;
      }, 2000);
      
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }

  // Функция для шаринга
  function shareText(text) {
    const message = encodeURIComponent(`🤖 InstaGroq AI:\n\n${text}\n\n— via @InstaGroqBot`);
    
    if (tg && tg.openTelegramLink) {
      // Если в Telegram WebApp
      tg.openTelegramLink(`https://t.me/share/url?url=&text=${message}`);
    } else {
      // В браузере
      window.open(`https://t.me/share/url?url=&text=${message}`, '_blank');
    }
  }

  // Функция создания кнопок для сообщения (только иконки)
  function createMessageActions(messageText, messageId) {
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'message-actions';
    actionsDiv.setAttribute('data-message-id', messageId);
    
    // Кнопка копировать (только иконка)
    const copyBtn = document.createElement('button');
    copyBtn.className = 'action-btn copy-btn';
    copyBtn.innerHTML = `📋`;
    copyBtn.title = 'Копировать текст';
    copyBtn.onclick = (e) => {
      e.stopPropagation();
      copyText(messageText, copyBtn);
    };
    
    // Кнопка поделиться (только иконка)
    const shareBtn = document.createElement('button');
    shareBtn.className = 'action-btn share-btn';
    shareBtn.innerHTML = `📤`;
    shareBtn.title = 'Поделиться';
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
    
    // Добавляем кнопки только для сообщений бота
    if (type === 'bot') {
      const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      wrapper.setAttribute('data-message-id', messageId);
      
      const actions = createMessageActions(text, messageId);
      wrapper.appendChild(actions);
      
      // Показываем кнопки при наведении/тапе
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