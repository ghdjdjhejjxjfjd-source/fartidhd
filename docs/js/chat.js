// docs/js/chat.js
import { askAI, getStarsBalance, clearAIMemory, changeStyle, changePersona } from "./api.js";
import { tg } from "./telegram.js";

export const STORAGE_KEY = "chat_history_v1";

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

export function forceClearChat(controller) {
  if (controller) {
    controller.clearHistory(true);
  }
}

export function createChatController({ chatEl, inputEl, sendBtnEl }) {
  let history = loadHistory();
  let sending = false;
  let currentUserId = tg?.initDataUnsafe?.user?.id || 0;
  let isReloading = false;
  let reloadTimer = null;
  
  // Текущие лимиты с сервера
  let currentLimits = {
    groq_persona: 0,
    groq_style: 0,
    openai_style: 0,
    groq_persona_max: 5,
    groq_style_max: 5,
    openai_style_max: 7
  };
  
  // Временные значения (несохраненные изменения)
  let tempStyle = null;
  let tempPersona = null;
  let hasUnsavedChanges = false;
  let currentAiMode = 'fast';

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

  // ✅ Функция для получения лимитов с сервера
  async function fetchLimits() {
    if (!currentUserId) return;
    
    try {
      const API_BASE = "https://fayrat-production.up.railway.app";
      const res = await fetch(`${API_BASE}/api/user/limits/${currentUserId}`);
      
      if (!res.ok) return;
      
      const data = await res.json();
      console.log("Limits data:", data);
      
      currentAiMode = data.ai_mode;
      currentLimits = {
        groq_persona: data.limits.groq_persona || 0,
        groq_style: data.limits.groq_styles || 0,
        openai_style: data.limits.openai_styles || 0,
        groq_persona_max: data.limits.groq_persona_max || 5,
        groq_style_max: data.limits.groq_styles_max || 5,
        openai_style_max: data.limits.openai_styles_max || 7
      };
      
      // Сбрасываем временные изменения
      tempStyle = null;
      tempPersona = null;
      hasUnsavedChanges = false;
      
      // Обновляем отображение
      updateLimitsDisplay();
      updateSaveButton();
      updateUnsavedIndicator();
      
    } catch (err) {
      console.log("Fetch limits error:", err);
    }
  }

  // ✅ Функция для обновления отображения лимитов
  function updateLimitsDisplay() {
    // Обновляем лимиты для характера
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
    
    // Обновляем лимиты для стиля
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
  }

  // ✅ Функция для обновления состояния кнопки сохранения
  function updateSaveButton() {
    const saveBtn = document.getElementById('saveSettingsBtn');
    if (!saveBtn) return;
    
    // Проверяем можно ли сохранить
    let canSave = hasUnsavedChanges;
    
    if (canSave && currentAiMode === 'fast') {
      // Для Groq проверяем лимиты
      if (tempPersona && currentLimits.groq_persona >= currentLimits.groq_persona_max) {
        canSave = false;
      }
      if (tempStyle && currentLimits.groq_style >= currentLimits.groq_style_max) {
        canSave = false;
      }
    } else if (canSave && currentAiMode === 'quality') {
      // Для OpenAI проверяем только стиль
      if (tempStyle && currentLimits.openai_style >= currentLimits.openai_style_max) {
        canSave = false;
      }
      // Характер для OpenAI всегда заблокирован
      if (tempPersona) {
        canSave = false;
      }
    }
    
    saveBtn.disabled = !canSave;
  }

  // ✅ Функция для обновления индикатора несохраненных изменений
  function updateUnsavedIndicator() {
    const indicator = document.getElementById('unsaved-indicator');
    if (indicator) {
      indicator.style.display = hasUnsavedChanges ? 'block' : 'none';
    }
  }

  // ✅ Обработчик изменения стиля (временное)
  function handleStyleChange(newStyle) {
    const originalStyle = getStyle();
    
    if (newStyle === originalStyle) {
      // Если выбрали текущее значение - ничего не меняем
      return;
    }
    
    tempStyle = newStyle;
    hasUnsavedChanges = true;
    
    // Временно показываем уменьшенный счетчик
    const styleLimitSpan = document.getElementById('style-limit');
    if (styleLimitSpan) {
      let used, max;
      if (currentAiMode === 'fast') {
        used = currentLimits.groq_style + (tempStyle ? 1 : 0);
        max = currentLimits.groq_style_max;
      } else {
        used = currentLimits.openai_style + (tempStyle ? 1 : 0);
        max = currentLimits.openai_style_max;
      }
      const remaining = max - used;
      styleLimitSpan.textContent = `📊 Останется после сохранения: ${remaining}/${max}`;
      styleLimitSpan.style.color = remaining < 0 ? '#ff4444' : '#ffaa00';
    }
    
    updateSaveButton();
    updateUnsavedIndicator();
  }

  // ✅ Обработчик изменения характера (временное)
  function handlePersonaChange(newPersona) {
    const originalPersona = getPersona();
    
    if (newPersona === originalPersona) {
      return;
    }
    
    if (currentAiMode !== 'fast') {
      // Для OpenAI характер недоступен
      alert('Изменение характера недоступно в этом режиме');
      document.getElementById('personaSel').value = getPersona();
      return;
    }
    
    tempPersona = newPersona;
    hasUnsavedChanges = true;
    
    // Временно показываем уменьшенный счетчик
    const personaLimitSpan = document.getElementById('persona-limit');
    if (personaLimitSpan) {
      const used = currentLimits.groq_persona + (tempPersona ? 1 : 0);
      const max = currentLimits.groq_persona_max;
      const remaining = max - used;
      personaLimitSpan.textContent = `📊 Останется после сохранения: ${remaining}/${max}`;
      personaLimitSpan.style.color = remaining < 0 ? '#ff4444' : '#ffaa00';
    }
    
    updateSaveButton();
    updateUnsavedIndicator();
  }

  // ✅ Функция сохранения изменений
  async function saveSettings() {
    if (!hasUnsavedChanges) return;
    
    let success = true;
    
    // Сохраняем стиль если он был изменен
    if (tempStyle) {
      const result = await changeStyle(tempStyle);
      if (!result) {
        success = false;
      }
    }
    
    // Сохраняем характер если он был изменен (только для Groq)
    if (tempPersona && currentAiMode === 'fast') {
      const result = await changePersona(tempPersona);
      if (!result) {
        success = false;
      }
    }
    
    if (success) {
      // Обновляем локальное хранилище
      if (tempStyle) {
        localStorage.setItem("ai_style", tempStyle);
      }
      if (tempPersona && currentAiMode === 'fast') {
        localStorage.setItem("ai_persona", tempPersona);
      }
      
      // Сбрасываем временные изменения
      tempStyle = null;
      tempPersona = null;
      hasUnsavedChanges = false;
      
      // Обновляем лимиты с сервера
      await fetchLimits();
      
      // Показываем сообщение об успехе
      alert('✅ Настройки сохранены');
      
      // Закрываем окно настроек
      closeSettings();
    } else {
      alert('❌ Не удалось сохранить некоторые настройки');
    }
  }

  // ✅ Функция отмены изменений
  function cancelSettings() {
    // Возвращаем исходные значения в select'ах
    const personaSelect = document.getElementById('personaSel');
    const styleSelect = document.getElementById('styleSel');
    
    if (personaSelect) {
      personaSelect.value = getPersona();
    }
    if (styleSelect) {
      styleSelect.value = getStyle();
    }
    
    // Сбрасываем временные изменения
    tempStyle = null;
    tempPersona = null;
    hasUnsavedChanges = false;
    
    // Обновляем отображение лимитов
    updateLimitsDisplay();
    updateSaveButton();
    updateUnsavedIndicator();
    
    // Закрываем окно настроек
    closeSettings();
  }

  // ✅ Функция закрытия настроек
  function closeSettings() {
    const overlay = document.getElementById('overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  }

  // ✅ Функция открытия настроек
  function openSettings() {
    const overlay = document.getElementById('overlay');
    if (overlay) {
      // Загружаем свежие лимиты
      fetchLimits();
      
      // Устанавливаем текущие значения
      const personaSelect = document.getElementById('personaSel');
      const styleSelect = document.getElementById('styleSel');
      
      if (personaSelect) {
        personaSelect.value = getPersona();
      }
      if (styleSelect) {
        styleSelect.value = getStyle();
      }
      
      // Сбрасываем временные изменения
      tempStyle = null;
      tempPersona = null;
      hasUnsavedChanges = false;
      
      overlay.style.display = 'flex';
      inputEl?.blur();
    }
  }

  function buildPrompt(userText){
    const lang = getLang();
    // Используем временные значения если есть, иначе сохраненные
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
    if(!t || sending || isReloading) return;

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
      const persona = tempPersona || getPersona();
      const style = tempStyle || getStyle();
      
      const answer = await askAI(t, lang, persona, style);

      removeTyping();

      const out = (answer || "").trim();
      add("bot", out || "…", true);
      
      await updateMenuBalance();
      
      if (!isReloading) {
        await checkModeChange();
      }
      
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

  // ✅ Функция для блокировки/разблокировки выбора характера
  async function updatePersonaLock() {
    if (!currentUserId) return;
    
    try {
      const API_BASE = "https://fayrat-production.up.railway.app";
      const res = await fetch(`${API_BASE}/api/user/ai_mode/${currentUserId}`);
      
      if (!res.ok) return;
      
      const data = await res.json();
      const isOpenAI = data.ai_mode === "quality";
      currentAiMode = data.ai_mode;
      
      const personaSelect = document.getElementById('personaSel');
      
      if (!personaSelect) return;
      
      // Удаляем старый замок если есть
      const oldLock = document.getElementById('persona-lock-icon');
      if (oldLock) oldLock.remove();
      
      if (isOpenAI) {
        // Блокируем для OpenAI
        personaSelect.disabled = true;
        personaSelect.style.opacity = '0.6';
        
        // Добавляем замок перед select
        const lockSpan = document.createElement('span');
        lockSpan.id = 'persona-lock-icon';
        lockSpan.innerHTML = '🔒';
        lockSpan.style.marginRight = '8px';
        lockSpan.style.fontSize = '18px';
        personaSelect.parentNode.insertBefore(lockSpan, personaSelect);
      } else {
        // Разблокируем для Groq
        personaSelect.disabled = false;
        personaSelect.style.opacity = '1';
      }
      
      // Обновляем лимиты
      await fetchLimits();
      
    } catch (err) {
      console.log("Persona lock update error:", err);
    }
  }

  async function checkModeChange() {
    if (!currentUserId || isReloading) return;
    
    try {
      const API_BASE = "https://fayrat-production.up.railway.app";
      const res = await fetch(`${API_BASE}/api/user/ai_mode/${currentUserId}`);
      
      if (!res.ok) return;
      
      const data = await res.json();
      
      const currentMode = localStorage.getItem("current_ai_mode");
      if (currentMode && data.ai_mode !== currentMode) {
        // Режим изменился - отменяем все ожидающие отправки
        if (sending) {
          setTimeout(() => checkModeChange(), 500);
          return;
        }
        
        if (reloadTimer) {
          clearTimeout(reloadTimer);
        }
        
        isReloading = true;
        
        localStorage.removeItem(STORAGE_KEY);
        localStorage.setItem("current_ai_mode", data.ai_mode);
        
        try {
          await clearAIMemory();
        } catch (e) {}
        
        alert("🔄 Режим изменен. Страница обновится...");
        
        reloadTimer = setTimeout(() => {
          window.location.reload();
        }, 1500);
        
      } else if (!currentMode) {
        localStorage.setItem("current_ai_mode", data.ai_mode);
        await updatePersonaLock();
      } else {
        await updatePersonaLock();
      }
    } catch (err) {
      console.log("Mode check error:", err);
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
    
    // Кнопка открытия настроек
    const gearBtn = document.getElementById('gearBtn');
    if (gearBtn) {
      gearBtn.addEventListener('click', openSettings);
    }
    
    // Кнопка сохранения
    const saveBtn = document.getElementById('saveSettingsBtn');
    if (saveBtn) {
      saveBtn.addEventListener('click', saveSettings);
    }
    
    // Кнопка отмены
    const cancelBtn = document.getElementById('cancelSettingsBtn');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', cancelSettings);
    }
    
    // Кнопка закрытия (старая)
    const closeBtn = document.getElementById('closeSettings');
    if (closeBtn) {
      closeBtn.addEventListener('click', cancelSettings);
    }
    
    // Обработчики для select'ов (теперь временные)
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
    
    // Очистка чата
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', async () => {
        const success = await clearHistory(false);
        if (success) {
          closeSettings();
        }
      });
    }
    
    // Закрытие по клику вне окна
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
    
    setTimeout(checkModeChange, 1000);
    setInterval(checkModeChange, 3000);
    
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && !isReloading) {
        checkModeChange();
      }
    });
    
    // Загружаем лимиты при старте
    setTimeout(fetchLimits, 1500);
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