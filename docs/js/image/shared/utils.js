// docs/js/image/shared/utils.js

// Показать уведомление
export function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}

// Получить пользователя Telegram
export function getTelegramUser() {
    const tg = window.Telegram?.WebApp;
    if (!tg || !tg.initDataUnsafe?.user) return { tg_user_id: 0 };
    return { tg_user_id: tg.initDataUnsafe.user.id };
}

// Получить баланс звезд
export async function getBalance() {
    try {
        const user = getTelegramUser();
        const response = await fetch(`/api/stars/balance/${user.tg_user_id}`);
        const data = await response.json();
        return data.balance || 0;
    } catch {
        return 100;
    }
}

// Обновить баланс в интерфейсе
export function updateBalance() {
    getBalance().then(balance => {
        const badge = document.getElementById('balanceBadge');
        if (badge) badge.textContent = `⭐ ${balance}`;
    });
}

// Переключение экранов
export function showScreen(screens, screenToShow) {
    screens.forEach(s => {
        if (s) s.classList.add('hidden');
    });
    if (screenToShow) screenToShow.classList.remove('hidden');
}

// Закрытие клавиатуры при тапе
export function setupKeyboardDismiss(element) {
    if (!element) return;
    
    element.addEventListener('mousedown', (e) => {
        if (e.target === element) {
            document.activeElement?.blur();
        }
    });
    
    element.addEventListener('touchstart', (e) => {
        if (e.target === element) {
            document.activeElement?.blur();
        }
    });
}