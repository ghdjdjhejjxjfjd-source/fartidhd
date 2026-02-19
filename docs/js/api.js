// docs/js/api.js

const API_BASE = "https://fayrat-production.up.railway.app";
const API_CHAT = API_BASE + "/api/chat";
const API_CLEAR_MEMORY = API_BASE + "/api/memory/clear";
const API_BALANCE = API_BASE + "/api/stars/balance";

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

export async function askAI(promptText, lang = "ru", persona = "friendly", style = "steps") {
  const user = getTelegramUser();

  const payload = {
    text: promptText,
    lang: lang,              // Явно передаем язык
    style: style,
    persona: persona,
    tg_user_id: user.tg_user_id,
    tg_username: user.tg_username,
    tg_first_name: user.tg_first_name,
  };

  console.log("Sending to API with lang:", lang);  // Для отладки
  console.log("Full payload:", payload);

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
      const errorText = await r.text();
      console.error("API Error Response:", errorText);
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
  if (!user.tg_user_id) return false;
  
  try {
    const r = await fetch(API_CLEAR_MEMORY, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tg_user_id: user.tg_user_id }),
    });
    return r.ok;
  } catch (e) {
    console.error("Clear memory error:", e);
    return false;
  }
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