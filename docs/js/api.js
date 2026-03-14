// docs/js/api.js - ИСПРАВЛЕННАЯ ВЕРСИЯ
const API_BASE = "https://fayrat-production.up.railway.app";
const API_CHAT = API_BASE + "/api/chat";
const API_CLEAR_MEMORY = API_BASE + "/api/memory/clear";
const API_BALANCE = API_BASE + "/api/stars/balance";
const API_LIMITS = API_BASE + "/api/user/limits";
const API_STYLE_CHANGE = API_BASE + "/api/user/style/change";
const API_PERSONA = API_BASE + "/api/user/persona";
const API_AI_MODE = API_BASE + "/api/user/ai_mode";

function getLang(){
  return localStorage.getItem("miniapp_lang_v1") || "ru";
}

function getStyle(){
  return localStorage.getItem("ai_style") || "steps";
}

function getPersona(){
  return localStorage.getItem("ai_persona") || "friendly";
}

function getAiMode() {
  return localStorage.getItem("ai_mode") || "fast";
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

export async function askAI(promptText) {
  const user = getTelegramUser();
  const aiMode = getAiMode();

  const payload = {
    text: promptText,  // 👈 Отправляем полный промпт с историей!
    lang: getLang(),
    style: getStyle(),
    persona: getPersona(),
    ai_mode: aiMode,
    tg_user_id: user.tg_user_id,
    tg_username: user.tg_username,
    tg_first_name: user.tg_first_name,
  };

  try {
    const r = await fetch(API_CHAT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (r.status === 402) {
      const data = await r.json();
      if (data.error === "insufficient_stars") {
        throw new Error("❌ Недостаточно звезд. Купите звезды в меню.");
      }
    }

    if (!r.ok) {
      throw new Error("API error " + r.status);
    }

    const data = await r.json();
    return (data.reply || "").trim();
  } catch (e) {
    console.error("Chat error:", e);
    throw e;
  }
}

export async function clearAIMemory() {
  const user = getTelegramUser();

  const r = await fetch(API_CLEAR_MEMORY, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tg_user_id: user.tg_user_id }),
  });

  return r.ok;
}

export async function getStarsBalance() {
  const user = getTelegramUser();
  if (!user.tg_user_id) return 0;
  
  try {
    const r = await fetch(`${API_BALANCE}/${user.tg_user_id}`);
    if (r.ok) {
      const data = await r.json();
      return data.balance || 0;
    }
  } catch (e) {
    console.error("Error fetching balance:", e);
  }
  return 0;
}

export async function getUserLimits() {
  const user = getTelegramUser();
  if (!user.tg_user_id) return null;
  
  try {
    const r = await fetch(`${API_LIMITS}/${user.tg_user_id}`);
    if (r.ok) {
      const data = await r.json();
      return data;
    }
  } catch (e) {
    console.error("Error fetching limits:", e);
  }
  return null;
}

export async function changeStyle(newStyle) {
  const user = getTelegramUser();
  if (!user.tg_user_id) return { success: false, message: "no_user" };
  
  try {
    const r = await fetch(API_STYLE_CHANGE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.tg_user_id,
        style: newStyle
      }),
    });
    
    const data = await r.json();
    
    if (!r.ok) {
      if (data.error === "limit_exceeded") {
        return { success: false, message: data.message || "Лимит изменений исчерпан" };
      }
      return { success: false, message: data.error || "Ошибка сервера" };
    }
    
    localStorage.setItem("ai_style", newStyle);
    return { success: true };
    
  } catch (e) {
    console.error("Change style error:", e);
    return { success: false, message: "Ошибка сети" };
  }
}

export async function changePersona(newPersona) {
  const user = getTelegramUser();
  if (!user.tg_user_id) return { success: false, message: "no_user" };
  
  try {
    const r = await fetch(API_PERSONA, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.tg_user_id,
        persona: newPersona
      }),
    });
    
    const data = await r.json();
    
    if (!r.ok) {
      if (data.error === "limit_exceeded") {
        return { success: false, message: data.message || "Лимит изменений исчерпан" };
      }
      return { success: false, message: data.error || "Ошибка сервера" };
    }
    
    localStorage.setItem("ai_persona", newPersona);
    return { success: true };
    
  } catch (e) {
    console.error("Change persona error:", e);
    return { success: false, message: "Ошибка сети" };
  }
}

export async function changeAiMode(newMode) {
  const user = getTelegramUser();
  if (!user.tg_user_id) return { success: false, message: "no_user" };
  
  if (newMode !== "fast" && newMode !== "quality") {
    return { success: false, message: "Неверный режим" };
  }
  
  try {
    const r = await fetch(API_AI_MODE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.tg_user_id,
        ai_mode: newMode
      }),
    });
    
    const data = await r.json();
    
    if (!r.ok) {
      if (data.error === "limit_exceeded") {
        return { 
          success: false, 
          message: data.message || "Лимит смен режима исчерпан (0/8)"
        };
      }
      
      if (data.message) {
        return { success: false, message: data.message };
      }
      
      return { success: false, message: data.error || "Ошибка сервера" };
    }
    
    if (data.success) {
      localStorage.setItem("ai_mode", newMode);
      return { success: true };
    }
    
    return { success: false, message: "Неизвестная ошибка" };
    
  } catch (e) {
    console.error("Change AI mode error:", e);
    return { success: false, message: "Ошибка сети" };
  }
}

export async function getCurrentMode() {
  const user = getTelegramUser();
  if (!user.tg_user_id) return null;
  
  try {
    const r = await fetch(`${API_AI_MODE}/${user.tg_user_id}`);
    if (r.ok) {
      const data = await r.json();
      if (data.ai_mode) {
        localStorage.setItem("ai_mode", data.ai_mode);
      }
      return data.ai_mode;
    }
  } catch (e) {
    console.error("Error fetching mode:", e);
  }
  return null;
}