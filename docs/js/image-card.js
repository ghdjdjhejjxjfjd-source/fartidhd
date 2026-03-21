// docs/js/image-card.js
const API_BASE = "https://ghdjdjhejjxjfjd-source.github.io/fartidhd/";

// ===== TELEGRAM =====
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

// ===== ПЕРЕМЕННЫЕ =====
let currentFile = null;
let currentResultBlob = null;

// ===== ПОЛУЧЕНИЕ ЯЗЫКА =====
function getLang() {
  const urlParams = new URLSearchParams(window.location.search);
  const lang = urlParams.get('lang');
  if (lang) {
    try { localStorage.setItem("miniapp_lang_v1", lang); } catch(e) {}
    return lang;
  }
  try { return localStorage.getItem("miniapp_lang_v1") || "ru"; } 
  catch(e) { return "ru"; }
}

// ===== ПОЛУЧЕНИЕ ТЕМЫ =====
function getTheme() {
  const urlParams = new URLSearchParams(window.location.search);
  const theme = urlParams.get('theme');
  if (theme) {
    try { localStorage.setItem("miniapp_theme_v1", theme); } catch(e) {}
    return theme;
  }
  try { return localStorage.getItem("miniapp_theme_v1") || "blue"; } 
  catch(e) { return "blue"; }
}

// ===== ПОЛУЧЕНИЕ ПЛАТФОРМЫ =====
function getPlatform() {
  const urlParams = new URLSearchParams(window.location.search);
  const platform = urlParams.get('platform');
  if (platform) {
    try { localStorage.setItem("miniapp_platform_v1", platform); } catch(e) {}
    return platform;
  }
  try { return localStorage.getItem("miniapp_platform_v1") || "ios"; } 
  catch(e) { return "ios"; }
}

// ===== ПРИМЕНЕНИЕ ПЛАТФОРМЫ =====
function applyPlatform(platform) {
  if (platform === 'android') {
    document.documentElement.classList.add('android-mode');
  } else {
    document.documentElement.classList.remove('android-mode');
  }
}

// ===== ПОЛУЧЕНИЕ ПОЛЬЗОВАТЕЛЯ =====
function getUser() {
  if (!tg || !tg.initDataUnsafe?.user) return null;
  return tg.initDataUnsafe.user;
}

// ===== ПОКАЗ ЗАГРУЗКИ =====
function showLoading(show, text = "Генерация...") {
  let loader = document.getElementById('loading');
  if (!loader) {
    loader = document.createElement('div');
    loader.id = 'loading';
    loader.className = 'loading';
    loader.innerHTML = `
      <div class="spinner"></div>
      <div class="loading-text" id="loadingText">${text}</div>
    `;
    document.body.appendChild(loader);
  }
  const loadingText = document.getElementById('loadingText');
  if (loadingText) loadingText.textContent = text;
  loader.style.display = show ? 'flex' : 'none';
}

// ===== ОСНОВНАЯ ФУНКЦИЯ ГЕНЕРАЦИИ =====
async function generateImage(prompt, mode = "txt2img", imageFile = null) {
  const user = getUser();
  if (!user) {
    alert("Ошибка: не удалось получить данные пользователя");
    return null;
  }

  showLoading(true, "Генерация...");

  try {
    const formData = new FormData();
    formData.append('tg_user_id', user.id);
    formData.append('tg_username', user.username || '');
    formData.append('tg_first_name', user.first_name || '');
    formData.append('prompt', prompt);
    formData.append('mode', mode);

    if (imageFile) {
      formData.append('image', imageFile);
    }

    const response = await fetch(`${API_BASE}/api/image`, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      if (data.error === 'insufficient_stars') {
        throw new Error('Недостаточно звезд');
      } else {
        throw new Error(data.message || 'Ошибка генерации');
      }
    }

    return data.image_base64;

  } catch (error) {
    alert('Ошибка: ' + error.message);
    return null;
  } finally {
    showLoading(false);
  }
}

// ===== СОХРАНЕНИЕ ИЗОБРАЖЕНИЯ =====
async function saveImage(base64Data, filename = 'image.png') {
  const blob = await fetch(base64Data).then(res => res.blob());
  
  if (tg && tg.sendData) {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      tg.sendData(JSON.stringify({
        type: 'photo',
        file: base64,
        filename: filename
      }));
    };
    reader.readAsDataURL(blob);
  } else {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }
}

// ===== ИНИЦИАЛИЗАЦИЯ =====
document.addEventListener('DOMContentLoaded', () => {
  const theme = getTheme();
  const platform = getPlatform();
  
  document.documentElement.setAttribute('data-theme', theme);
  applyPlatform(platform);
  
  // Добавляем стили для загрузки
  const style = document.createElement('style');
  style.textContent = `
    .loading {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.8);
      backdrop-filter: blur(10px);
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .spinner {
      width: 50px;
      height: 50px;
      border: 3px solid rgba(255,255,255,0.1);
      border-top-color: var(--accent1, #3a8cff);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 20px;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .loading-text {
      color: white;
      font-size: 16px;
    }
  `;
  document.head.appendChild(style);
});