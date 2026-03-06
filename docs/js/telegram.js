export const tg = window.Telegram?.WebApp || null;

export function applyViewportHeight() {
  if (tg && typeof tg.viewportHeight === "number") {
    document.documentElement.style.setProperty("--vh", tg.viewportHeight + "px");
  } else {
    document.documentElement.style.setProperty("--vh", window.innerHeight + "px");
  }
}

// Инициализация темы Telegram
export function initTelegramTheme(callback) {
  if (!tg) return;
  
  // Слушаем изменения темы
  tg.onEvent('themeChanged', () => {
    const newTheme = getThemeFromTelegram();
    document.documentElement.setAttribute("data-theme", newTheme);
    try {
      localStorage.setItem("miniapp_theme_v1", newTheme);
    } catch(e) {}
    
    if (callback) callback(newTheme);
  });
}

// Получение темы на основе Telegram
export function getThemeFromTelegram() {
  if (!tg) {
    try { return localStorage.getItem("miniapp_theme_v1") || "blue"; } 
    catch(e) { return "blue"; }
  }
  
  const saved = (() => { try { return localStorage.getItem("miniapp_theme_v1"); } catch(e) { return null; } })();
  
  // ЛОГИКА:
  // Светлая тема телефона → light
  // Темная тема телефона → сохраненная цветная тема
  if (tg.colorScheme === 'light') {
    return "light";
  } else {
    return saved || "blue";
  }
}

export function initTelegramViewport(chatEl = null) {
  if (tg) {
    tg.ready();
    tg.expand();
  }

  applyViewportHeight();

  const onChange = () => {
    applyViewportHeight();
    if (chatEl) requestAnimationFrame(() => (chatEl.scrollTop = chatEl.scrollHeight));
  };

  if (tg && tg.onEvent) {
    tg.onEvent("viewportChanged", onChange);
  } else {
    window.addEventListener("resize", onChange);
  }
}