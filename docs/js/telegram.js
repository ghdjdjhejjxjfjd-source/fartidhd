// docs/js/telegram.js - ИСПРАВЛЕННАЯ ВЕРСИЯ ДЛЯ 100% ЗАКРЫТИЯ
export const tg = window.Telegram?.WebApp || null;

// Функция для ПОЛНОГО закрытия Mini App
export function closeMiniApp() {
  if (tg) {
    try {
      // Показываем всплывающее окно с подтверждением
      tg.showPopup({
        title: 'Выход',
        message: 'Закрыть приложение?',
        buttons: [
          { id: 'close', type: 'default', text: '✅ Да' },
          { id: 'cancel', type: 'cancel', text: '❌ Нет' }
        ]
      }, (buttonId) => {
        if (buttonId === 'close') {
          // ПОЛНОЕ закрытие Mini App
          tg.close();
        }
      });
    } catch (e) {
      // Если showPopup не работает - закрываем сразу
      tg.close();
    }
  } else {
    // Fallback для браузера
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.close();
    }
  }
}

// Функция для обработки кнопки "Назад"
export function initBackButton(chatEl = null) {
  if (!tg) return;
  
  // Показываем стандартную кнопку "Назад"
  tg.BackButton.show();
  
  // Убираем старые обработчики
  tg.BackButton.offClick();
  
  // Добавляем новый обработчик
  tg.BackButton.onClick(() => {
    closeMiniApp();
  });
  
  // Если есть чат, добавляем прокрутку
  if (chatEl) {
    const onViewportChanged = () => {
      requestAnimationFrame(() => {
        chatEl.scrollTop = chatEl.scrollHeight;
      });
    };
    tg.onEvent('viewportChanged', onViewportChanged);
  }
}

export function applyViewportHeight() {
  if (tg && typeof tg.viewportHeight === "number") {
    document.documentElement.style.setProperty("--vh", tg.viewportHeight + "px");
  } else {
    document.documentElement.style.setProperty("--vh", window.innerHeight + "px");
  }
}

export function initTelegramViewport(chatEl = null) {
  if (tg) {
    tg.ready();
    tg.expand();
    
    // Инициализируем кнопку "Назад"
    initBackButton(chatEl);
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

// Функция для безопасного перехода
export function navigateTo(url) {
  if (tg) {
    tg.close();  // Закрываем текущее окно
    setTimeout(() => {
      window.location.href = url;
    }, 100);
  } else {
    window.location.href = url;
  }
}

// Функция для показа подтверждения
export function showConfirm(message, callback) {
  if (tg && tg.showConfirm) {
    tg.showConfirm(message, callback);
  } else {
    callback(window.confirm(message));
  }
}

// Функция для показа попапа
export function showPopup(params, callback) {
  if (tg && tg.showPopup) {
    tg.showPopup(params, callback);
  } else {
    alert(params.message);
    if (callback) callback('ok');
  }
}