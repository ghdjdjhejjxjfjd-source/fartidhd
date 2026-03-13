// docs/js/chat.js - ИСПРАВЛЕННАЯ ВЕРСИЯ (кнопка блокируется при ошибках интернета)
import { askAI, getStarsBalance, clearAIMemory, changeStyle, changePersona, getUserLimits, changeAiMode, getCurrentMode } from "./api.js";
import { tg } from "./telegram.js";

const API_BASE = "https://fayrat-production.up.railway.app";

export const STORAGE_KEY = "chat_history_v1";
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;
const MAX_HISTORY = 100;
const MAX_STORAGE_SIZE = 4 * 1024 * 1024;

// Функция для показа загрузки на кнопке
function setButtonLoading(button, isLoading) {
  if (!button) return;
  
  if (isLoading) {
    button.disabled = true;
    button.innerHTML = '<span class="spinner-small"></span>';
    document.body.classList.add('saving');
  } else {
    button.disabled = false;
    button.innerHTML = window.t?.save || "💾 Сохранить";
    document.body.classList.remove('saving');
  }
}

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
    if (list.length > MAX_HISTORY) {
      list = list.slice(-MAX_HISTORY);
    }
    
    const json = JSON.stringify(list);
    if (json.length > MAX_STORAGE_SIZE) {
      list = list.slice(-50);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } else {
      localStorage.setItem(STORAGE_KEY, json);
    }
  } catch(e){
    if (e.name === 'QuotaExceededError') {
      localStorage.removeItem(STORAGE_KEY);
    }
  }
}

export function forceClearChat(controller) {
  if (controller) {
    controller.clearHistory(true);
  }
}

async function waitForInternet(retries = MAX_RETRIES) {
  for (let i = 0; i < retries; i++) {
    if (navigator.onLine) return true;
    await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
  }
  return false;
}

export function createChatController({ chatEl, inputEl, sendBtnEl }) {
  let history = loadHistory();
  
  let sending = false;
  let currentUserId = tg?.initDataUnsafe?.user?.id || 0;
  let isReloading = false;
  let reloadTimer = null;
  
  let currentLimits = {
    groq_persona: 0,
    groq_style: 0,
    openai_style: 0,
    groq_persona_max: 5,
    groq_style_max: 5,
    openai_style_max: 7,
    ai_mode_changes: 0
  };
  
  let tempStyle = null;
  let tempPersona = null;
  let tempAiMode = null;
  let hasUnsavedChanges = false;
  let currentAiMode = 'fast';
  let isLoadingLimits = false;
  let settingsOpen = false;

  const TYPING_ID = "typing-indicator";

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

  function autoResizeTextarea() {
    if (inputEl && inputEl.tagName === 'TEXTAREA') {
      inputEl.style.height = 'auto';
      inputEl.style.height = (inputEl.scrollHeight) + 'px';
    }
  }

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

  function shareText(text) {
    const message = encodeURIComponent(`🤖 InstaGroq AI:\n\n${text}\n\n— via @InstaGroqBot`);
    
    if (tg && tg.openTelegramLink) {
      tg.openTelegramLink(`https://t.me/share/url?url=&text=${message}`);
    } else {
      window.open(`https://t.me/share/url?url=&text=${message}`, '_blank');
    }
  }

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

  function getAiModeFromStorage() {
    return localStorage.getItem("ai_mode") || "fast";
  }

  function renderFromHistory(){
    chatEl.innerHTML = "";
    
    if (!history || history.length === 0){
      add("bot", helloText(), true);
    } else {
      for (const m of history){
        if (!m || !m.text) continue;
        add(m.role === "user" ? "user" : "bot", m.text, false);
      }
    }
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  async function clearHistory(skipConfirm = false) {
    if (isReloading) return false;
    
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

  async function fetchLimits() {
    if (!currentUserId || isLoadingLimits) return;
    
    isLoadingLimits = true;
    
    try {
      const data = await getUserLimits();
      if (!data) return;
      
      currentAiMode = data.ai_mode;
      currentLimits = {
        groq_persona: data.limits.groq_persona || 0,
        groq_style: data.limits.groq_style || 0,
        openai_style: data.limits.openai_style || 0,
        groq_persona_max: data.limits.groq_persona_max || 5,
        groq_style_max: data.limits.groq_style_max || 5,
        openai_style_max: data.limits.openai_style_max || 7,
        ai_mode_changes: data.limits.ai_mode_changes || 0
      };
      
      if (settingsOpen) {
        updateLimitsDisplay();
        updateSaveButton();
        updateUnsavedIndicator();
      }
      
    } catch (err) {
      console.log("Fetch limits error:", err);
    } finally {
      isLoadingLimits = false;
    }
  }

  function updateLimitsDisplay() {
    const personaLimitSpan = document.getElementById('persona-limit');
    if (personaLimitSpan) {
      if (currentAiMode === 'fast') {
        const used = currentLimits.groq_persona;
        const max = currentLimits.groq_persona_max;
        const remaining = max - used;
        personaLimitSpan.textContent = `📊 Осталось изменений характера: ${remaining}/${max}`;
        personaLimitSpan.style.color = remaining <= 0 ? '#ff4444' : '#666';
      } else {
        personaLimitSpan.textContent = `🔒 Изменение характера недоступно`;
        personaLimitSpan.style.color = '#666';
      }
    }
    
    const styleLimitSpan = document.getElementById('style-limit');
    if (styleLimitSpan) {
      let used, max;
      if (currentAiMode === 'fast') {
        used = currentLimits.groq_style;
        max = currentLimits.groq_style_max;
      } else {
        used = currentLimits.openai_style;
        max = currentLimits.openai_style_max;
      }
      const remaining = max - used;
      styleLimitSpan.textContent = `📊 Осталось изменений стиля: ${remaining}/${max}`;
      styleLimitSpan.style.color = remaining <= 0 ? '#ff4444' : '#666';
    }

    const aiModeLimitSpan = document.getElementById('aiMode-limit');
    if (aiModeLimitSpan) {
      const remaining = 8 - (currentLimits.ai_mode_changes || 0);
      aiModeLimitSpan.textContent = `📊 Осталось смен режима: ${remaining}/8`;
      aiModeLimitSpan.style.color = remaining <= 0 ? '#ff4444' : '#666';
    }
  }

  function updateSaveButton() {
    const saveBtn = document.getElementById('saveSettingsBtn');
    if (!saveBtn) return;
    
    // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА - если лимиты исчерпаны, кнопка не активна
    let canSave = hasUnsavedChanges;
    
    if (tempAiMode && currentLimits.ai_mode_changes >= 8) {
      canSave = false;
    }
    
    if (tempStyle) {
      if (currentAiMode === 'fast' && currentLimits.groq_style >= 5) {
        canSave = false;
      }
      if (currentAiMode === 'quality' && currentLimits.openai_style >= 7) {
        canSave = false;
      }
    }
    
    if (tempPersona && currentAiMode === 'fast' && currentLimits.groq_persona >= 5) {
      canSave = false;
    }
    
    saveBtn.disabled = !canSave;
  }

  function updateUnsavedIndicator() {
    const indicator = document.getElementById('unsaved-indicator');
    if (indicator) {
      indicator.style.display = hasUnsavedChanges ? 'block' : 'none';
    }
  }

  function handleStyleChange(newStyle) {
    const originalStyle = getStyle();
    
    if (newStyle === originalStyle && !tempStyle) {
      tempStyle = null;
    } else {
      tempStyle = newStyle;
    }
    
    hasUnsavedChanges = (tempStyle !== null) || (tempPersona !== null) || (tempAiMode !== null);
    updateSaveButton();
    updateUnsavedIndicator();
  }

  function handlePersonaChange(newPersona) {
    if (currentAiMode !== 'fast') {
      alert('Изменение характера недоступно в этом режиме');
      document.getElementById('personaSel').value = getPersona();
      return;
    }
    
    const originalPersona = getPersona();
    
    if (newPersona === originalPersona && !tempPersona) {
      tempPersona = null;
    } else {
      tempPersona = newPersona;
    }
    
    hasUnsavedChanges = (tempStyle !== null) || (tempPersona !== null) || (tempAiMode !== null);
    updateSaveButton();
    updateUnsavedIndicator();
  }

  function handleAiModeChange(newMode) {
    const originalMode = getAiModeFromStorage();
    
    if (newMode === originalMode && !tempAiMode) {
      tempAiMode = null;
    } else {
      tempAiMode = newMode;
    }
    
    hasUnsavedChanges = (tempStyle !== null) || (tempPersona !== null) || (tempAiMode !== null);
    updateSaveButton();
    updateUnsavedIndicator();
  }

  // ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ СОХРАНЕНИЯ ==========
  async function saveSettings() {
    if (!hasUnsavedChanges) return;
    
    const originalMode = getAiModeFromStorage();
    const originalStyle = getStyle();
    const originalPersona = getPersona();
    
    // ✅ ПРОВЕРКА ЛИМИТОВ ПЕРЕД СОХРАНЕНИЕМ
    if (tempAiMode) {
      const modeChanges = currentLimits.ai_mode_changes || 0;
      if (modeChanges >= 8) {
        add("bot", "❌ Лимит смен режима исчерпан (0/8). Попробуйте завтра.", true);
        document.getElementById('aiModeSel').value = originalMode;
        tempAiMode = null;
        hasUnsavedChanges = (tempStyle !== null) || (tempPersona !== null);
        updateSaveButton();
        updateUnsavedIndicator();
        closeSettings();
        return;
      }
    }
    
    if (tempStyle) {
      let styleChanges, styleMax;
      if (currentAiMode === 'fast') {
        styleChanges = currentLimits.groq_style || 0;
        styleMax = 5;
      } else {
        styleChanges = currentLimits.openai_style || 0;
        styleMax = 7;
      }
      
      if (styleChanges >= styleMax) {
        add("bot", `❌ Лимит изменений стиля исчерпан (0/${styleMax}). Попробуйте завтра.`, true);
        document.getElementById('styleSel').value = originalStyle;
        tempStyle = null;
        hasUnsavedChanges = (tempAiMode !== null) || (tempPersona !== null);
        updateSaveButton();
        updateUnsavedIndicator();
        closeSettings();
        return;
      }
    }
    
    if (tempPersona && currentAiMode === 'fast') {
      const personaChanges = currentLimits.groq_persona || 0;
      if (personaChanges >= 5) {
        add("bot", "❌ Лимит изменений характера исчерпан (0/5). Попробуйте завтра.", true);
        document.getElementById('personaSel').value = originalPersona;
        tempPersona = null;
        hasUnsavedChanges = (tempAiMode !== null) || (tempStyle !== null);
        updateSaveButton();
        updateUnsavedIndicator();
        closeSettings();
        return;
      }
    }
    
    // Если дошли до сюда - лимиты не превышены, можно сохранять
    if (tempAiMode) {
      const confirmMsg = "⚠️ Смена режима ИИ очистит историю чата. Продолжить?";
      let confirmed;
      
      if (tg && typeof tg.showConfirm === "function") {
        confirmed = await new Promise((resolve) => tg.showConfirm(confirmMsg, (ok) => resolve(ok)));
      } else {
        confirmed = window.confirm(confirmMsg);
      }
      
      if (!confirmed) {
        document.getElementById('aiModeSel').value = originalMode;
        tempAiMode = null;
        hasUnsavedChanges = (tempStyle !== null) || (tempPersona !== null);
        updateSaveButton();
        updateUnsavedIndicator();
        return;
      }
    }
    
    const saveBtn = document.getElementById('saveSettingsBtn');
    setButtonLoading(saveBtn, true);
    
    let success = true;
    let errorMsg = "";
    
    // Сначала пробуем сменить режим ИИ
    if (tempAiMode) {
      const result = await changeAiMode(tempAiMode);
      
      if (result && result.success) {
        // Успешно - сохраняем и очищаем
        localStorage.setItem("ai_mode", tempAiMode);
        currentAiMode = tempAiMode;
        
        try {
          await clearAIMemory();
          history = [];
          saveHistory(history);
          chatEl.innerHTML = "";
          add("bot", "🧹 Режим изменен, история очищена", true);
        } catch (e) {
          console.error("Failed to clear memory:", e);
        }
      } else {
        // Ошибка - лимит исчерпан или другая проблема
        success = false;
        errorMsg = result?.message || "Ошибка смены режима";
        
        // Возвращаем select к исходному значению
        document.getElementById('aiModeSel').value = originalMode;
        tempAiMode = null;
        
        // Показываем сообщение об ошибке
        add("bot", `❌ ${errorMsg}`, true);
        
        // Закрываем настройки и выходим
        setButtonLoading(saveBtn, false);
        hasUnsavedChanges = (tempStyle !== null) || (tempPersona !== null);
        updateSaveButton();
        updateUnsavedIndicator();
        closeSettings();
        return;
      }
    }
    
    // Если режим сменился успешно (или не менялся), пробуем сменить стиль
    if (tempStyle && success) {
      const result = await changeStyle(tempStyle);
      if (result && result.success) {
        localStorage.setItem("ai_style", tempStyle);
      } else {
        success = false;
        errorMsg = result?.message || "Ошибка смены стиля";
        document.getElementById('styleSel').value = originalStyle;
      }
    }
    
    // Если стиль сменился успешно (или не менялся), пробуем сменить характер
    if (tempPersona && currentAiMode === 'fast' && success) {
      const result = await changePersona(tempPersona);
      if (result && result.success) {
        localStorage.setItem("ai_persona", tempPersona);
      } else {
        success = false;
        errorMsg = result?.message || "Ошибка смены характера";
        document.getElementById('personaSel').value = originalPersona;
      }
    }
    
    setButtonLoading(saveBtn, false);
    
    if (success) {
      // Все изменения успешны
      tempStyle = null;
      tempPersona = null;
      tempAiMode = null;
      hasUnsavedChanges = false;
      
      await fetchLimits();
      updateSaveButton();
      updateUnsavedIndicator();
      closeSettings();
    } else {
      // Если была ошибка, показываем её
      add("bot", `❌ ${errorMsg}`, true);
      closeSettings();
    }
  }

  function cancelSettings() {
    const personaSelect = document.getElementById('personaSel');
    const styleSelect = document.getElementById('styleSel');
    const aiModeSelect = document.getElementById('aiModeSel');
    
    if (personaSelect) personaSelect.value = getPersona();
    if (styleSelect) styleSelect.value = getStyle();
    if (aiModeSelect) aiModeSelect.value = getAiModeFromStorage();
    
    tempStyle = null;
    tempPersona = null;
    tempAiMode = null;
    hasUnsavedChanges = false;
    
    updateSaveButton();
    updateUnsavedIndicator();
    closeSettings();
  }

  function closeSettings() {
    const overlay = document.getElementById('overlay');
    if (overlay) {
      overlay.style.display = 'none';
      settingsOpen = false;
    }
  }

  function openSettings() {
    const overlay = document.getElementById('overlay');
    if (overlay) {
      settingsOpen = true;
      
      const personaSelect = document.getElementById('personaSel');
      const styleSelect = document.getElementById('styleSel');
      const aiModeSelect = document.getElementById('aiModeSel');
      
      if (personaSelect) personaSelect.value = getPersona();
      if (styleSelect) styleSelect.value = getStyle();
      if (aiModeSelect) aiModeSelect.value = getAiModeFromStorage();
      
      tempStyle = null;
      tempPersona = null;
      tempAiMode = null;
      hasUnsavedChanges = false;
      
      fetchLimits().then(() => {
        updateSaveButton();
        updateUnsavedIndicator();
      });
      
      overlay.style.display = 'flex';
      inputEl?.blur();
    }
  }

  function buildPrompt(userText){
    const lang = getLang();
    const persona = tempPersona || getPersona();
    const style = tempStyle || getStyle();
    
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
      "ru": "Russian", "kk": "Kazakh", "en": "English",
      "tr": "Turkish", "uk": "Ukrainian", "fr": "French"
    };
    const targetLang = langNames[lang] || "Russian";

    const styleDesc = {
      "short": "Keep answers VERY short (1-2 sentences).",
      "steps": "Answer step by step, structured.",
      "detail": "Answer in detail but without unnecessary words."
    }[style] || "Answer naturally.";

    const personaDesc = {
      "friendly": "You are FRIENDLY and WARM. Use smileys 🙂 in EVERY message.",
      "fun": "You are FUN and HUMOROUS. Use lots of emojis 😄 😂 in EVERY message.",
      "strict": "You are STRICT and SERIOUS. NEVER use emojis. Be short and direct.",
      "smart": "You are SMART and THOUGHTFUL. Use smart emojis 🧐 🤔 in EVERY message."
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

  // ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ ОТПРАВКИ (кнопка блокируется при ошибках интернета) ==========
  async function send() {
    const t = inputEl.value.trim();
    if (!t || sending || isReloading) return;

    // БЛОКИРУЕМ КНОПКУ СРАЗУ
    sending = true;
    sendBtnEl.disabled = true;

    // ПРОВЕРКА ИНТЕРНЕТА ПЕРЕД ОТПРАВКОЙ
    if (!navigator.onLine) {
      add("bot", "📡 Нет интернет-соединения. Проверьте подключение.", true);
      sending = false;
      sendBtnEl.disabled = false;
      return;
    }

    // Добавляем сообщение пользователя
    add("user", t, true);
    inputEl.value = "";
    if (inputEl.tagName === 'TEXTAREA') inputEl.style.height = 'auto';
    
    addTyping();

    // ТАЙМАУТ ДЛЯ АНИМАЦИИ ПЕЧАТАНИЯ (15 секунд)
    const typingTimeout = setTimeout(() => {
      removeTyping();
      add("bot", "⏱️ Превышено время ожидания. Проверьте интернет и попробуйте снова.", true);
      // ⚠️ НЕ РАЗБЛОКИРУЕМ КНОПКУ ПРИ ТАЙМАУТЕ
      // sending остается true, кнопка disabled
    }, 15000);

    let lastError = null;
    let success = false;

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      try {
        const hasInternet = await waitForInternet(1);
        if (!hasInternet) throw new Error("no_internet");

        const answer = await askAI(t);
        
        clearTimeout(typingTimeout); // Очищаем таймаут
        removeTyping();
        add("bot", answer || "…", true);
        await updateMenuBalance();
        success = true;
        break;
        
      } catch (e) {
        lastError = e;
        console.log(`Attempt ${attempt} failed:`, e);
        
        if (!navigator.onLine || e.message === "no_internet") {
          clearTimeout(typingTimeout);
          removeTyping();
          add("bot", "📡 Интернет пропал. Проверьте подключение.", true);
          // ⚠️ НЕ РАЗБЛОКИРУЕМ КНОПКУ ПРИ ПОТЕРЕ ИНТЕРНЕТА
          // sending остается true, кнопка disabled
          return;
        }
        
        if (attempt < MAX_RETRIES) {
          // Пересоздаем анимацию если нужно
          removeTyping();
          addTyping();
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * attempt));
        }
      }
    }

    clearTimeout(typingTimeout); // Очищаем таймаут
    removeTyping();
    
    if (!success) {
      const errorMessage = lastError?.message || "";
      const errorStatus = lastError?.status || "";
      
      if (errorMessage.includes("insufficient_stars") || 
          errorMessage.includes("402") || 
          errorMessage.includes("Insufficient stars") ||
          errorStatus === 402) {
        add("bot", "❌ Недостаточно звезд. Купите в меню: ⭐ Купить звезды", true);
        // Разблокируем при ошибке звезд
        sending = false;
        sendBtnEl.disabled = false;
      } else if (errorMessage.includes("Failed to fetch") || errorMessage.includes("network")) {
        add("bot", "📡 Проблема с сетью. Проверьте интернет.", true);
        // ⚠️ НЕ РАЗБЛОКИРУЕМ ПРИ СЕТЕВЫХ ОШИБКАХ
        // sending остается true, кнопка disabled
      } else {
        add("bot", "❌ Ошибка сервера. Попробуйте позже.", true);
        // Разблокируем при других ошибках
        sending = false;
        sendBtnEl.disabled = false;
      }
    } else {
      // Успешно отправили - разблокируем
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

  async function syncModeWithServer() {
    if (!currentUserId) return;
    
    try {
      const serverMode = await getCurrentMode();
      if (!serverMode) return;
      
      const localMode = getAiModeFromStorage();
      
      if (serverMode !== localMode) {
        console.log(`🔄 Mode mismatch: server=${serverMode}, local=${localMode}, fixing...`);
        localStorage.setItem("ai_mode", serverMode);
        currentAiMode = serverMode;
        
        const aiModeSelect = document.getElementById('aiModeSel');
        if (aiModeSelect) aiModeSelect.value = serverMode;
        
        add("bot", `🔄 Режим ИИ синхронизирован: ${serverMode === 'fast' ? '🚀 Быстрый' : '💎 Качественный'}`, true);
      }
    } catch (err) {
      console.error("Failed to sync mode:", err);
    }
  }

  async function updatePersonaLock() {
    if (!currentUserId) return;
    
    try {
      const res = await fetch(`${API_BASE}/api/user/ai_mode/${currentUserId}`);
      if (!res.ok) return;
      
      const data = await res.json();
      currentAiMode = data.ai_mode;
      
      const personaSelect = document.getElementById('personaSel');
      if (!personaSelect) return;
      
      const oldLock = document.getElementById('persona-lock-icon');
      if (oldLock) oldLock.remove();
      
      if (data.ai_mode === "quality") {
        personaSelect.disabled = true;
        personaSelect.style.opacity = '0.6';
        
        const lockSpan = document.createElement('span');
        lockSpan.id = 'persona-lock-icon';
        lockSpan.innerHTML = '🔒';
        lockSpan.style.marginRight = '8px';
        lockSpan.style.fontSize = '18px';
        personaSelect.parentNode.insertBefore(lockSpan, personaSelect);
      } else {
        personaSelect.disabled = false;
        personaSelect.style.opacity = '1';
      }
      
      if (settingsOpen) await fetchLimits();
      
    } catch (err) {
      console.log("Persona lock update error:", err);
    }
  }

  function setupNetworkListeners() {
    window.addEventListener('online', () => {
      add("bot", "📡 Интернет соединение восстановлено!", true);
      // При восстановлении интернета разблокируем кнопку, если не идет отправка
      if (!sending) {
        sendBtnEl.disabled = false;
      }
    });
    
    window.addEventListener('offline', () => {
      // При пропадании интернета блокируем кнопку
      sendBtnEl.disabled = true;
    });
  }

  function bindUI() {
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

    // Запрещаем мультитач (2+ пальца)
    chatEl.addEventListener("touchstart", (e) => {
      if (e.touches.length > 1) {
        e.preventDefault();
      }
    }, { passive: false });

    // Запрещаем жесты масштабирования
    document.addEventListener('gesturestart', (e) => {
      e.preventDefault();
    }, { passive: false });

    document.addEventListener('gesturechange', (e) => {
      e.preventDefault();
    }, { passive: false });

    document.addEventListener('gestureend', (e) => {
      e.preventDefault();
    }, { passive: false });

    // Запрещаем двойной тап (быстро 2 касания)
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) {
        e.preventDefault();
      }
      lastTouchEnd = now;
    }, { passive: false });

    // Запрещаем двойной клик мышью
    document.addEventListener('dblclick', (e) => {
      e.preventDefault();
    }, { passive: false });

    // Один тап для закрытия клавиатуры (НЕ ломает скролл)
    chatEl.addEventListener("pointerdown", () => {
      if (document.activeElement === inputEl) {
        inputEl.blur();
      }
    });

    const gearBtn = document.getElementById('gearBtn');
    if (gearBtn) gearBtn.addEventListener('click', openSettings);
    
    const saveBtn = document.getElementById('saveSettingsBtn');
    if (saveBtn) saveBtn.addEventListener('click', saveSettings);
    
    const cancelBtn = document.getElementById('cancelSettingsBtn');
    if (cancelBtn) cancelBtn.addEventListener('click', cancelSettings);
    
    const closeBtn = document.getElementById('closeSettings');
    if (closeBtn) closeBtn.addEventListener('click', cancelSettings);
    
    const personaSelect = document.getElementById('personaSel');
    if (personaSelect) {
      personaSelect.addEventListener('change', (e) => {
        handlePersonaChange(e.target.value);
      });
    }
    
    const styleSelect = document.getElementById('styleSel');
    if (styleSelect) {
      styleSelect.addEventListener('change', (e) => {
        handleStyleChange(e.target.value);
      });
    }
    
    const aiModeSelect = document.getElementById('aiModeSel');
    if (aiModeSelect) {
      aiModeSelect.addEventListener('change', (e) => {
        handleAiModeChange(e.target.value);
      });
    }
    
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', async () => {
        const success = await clearHistory(false);
        if (success) closeSettings();
      });
    }
    
    const overlay = document.getElementById('overlay');
    if (overlay) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          if (hasUnsavedChanges) {
            if (confirm('У вас есть несохраненные изменения. Закрыть без сохранения?')) {
              cancelSettings();
            }
          } else {
            closeSettings();
          }
        }
      });
    }
    
    setupNetworkListeners();
    
    if (!navigator.onLine) {
      sendBtnEl.disabled = true;
    }
    
    syncModeWithServer();
    renderFromHistory();
  }

  async function confirmClear() {
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
    syncModeWithServer,
  };
}