// docs/js/image/modes/upscale.js

import { showToast, getBalance, updateBalance, setupKeyboardDismiss, getTelegramUser } from '../shared/utils.js';

let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;
let selectedFile = null;
let originalFileName = null;

const API_BASE = "https://fayrat-production.up.railway.app";

// Загружаем Pica для высококачественного увеличения
const pica = new Pica();

export function initUpscale(container) {
    container.innerHTML = `
        <div class="file-section">
            <input type="file" id="fileInput" accept="image/*" hidden>
            <button class="file-btn" id="pickFileBtn">
                <span class="btn-icon">📁</span>
                Выбрать изображение
            </button>
            <div class="file-preview hidden" id="filePreview">
                <img id="previewImg" alt="Preview">
                <button class="remove-file" id="removeFileBtn">✕</button>
            </div>
        </div>

        <div class="result-area" id="resultArea">
            <div class="preview-placeholder" id="previewPlaceholder">
                <div class="placeholder-icon">🔍</div>
                <div class="placeholder-text">Результат 4K появится здесь</div>
            </div>
            <img class="result-image hidden" id="resultImage" alt="4K image">
            
            <div class="loading-overlay hidden" id="loadingOverlay">
                <div class="spinner"></div>
                <div class="loading-text">Улучшение до 4K... <span id="loadingTimer">0с</span></div>
            </div>
        </div>

        <button class="generate-btn" id="generateBtn">
            <span class="btn-icon">🔍</span>
            Улучшить до 4K
            <span class="price-tag" id="generatePrice">3⭐</span>
        </button>

        <div class="result-actions hidden" id="resultActions">
            <div class="action-row">
                <button class="action-btn" id="saveToBotBtn" title="Сохранить в бот">💾</button>
                <button class="action-btn" id="regenerateBtn" title="Заново">🔄</button>
            </div>
        </div>
    `;
    
    // Настройка закрытия клавиатуры
    const chatArea = document.querySelector('.wrap');
    if (chatArea) {
        setupKeyboardDismiss(chatArea);
    }
    
    document.getElementById('pickFileBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    document.getElementById('removeFileBtn').addEventListener('click', removeFile);
    document.getElementById('generateBtn').addEventListener('click', generateImage);
    document.getElementById('saveToBotBtn').addEventListener('click', sendToBot);
    document.getElementById('regenerateBtn').addEventListener('click', regenerateImage);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showToast('Пожалуйста, выберите изображение', 'error');
        return;
    }
    
    selectedFile = file;
    originalFileName = file.name.replace(/\.[^/.]+$/, "");
    
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('filePreview').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function removeFile() {
    selectedFile = null;
    originalFileName = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('filePreview').classList.add('hidden');
    document.getElementById('previewImg').src = '';
}

async function generateImage() {
    if (isGenerating) return;
    
    if (!selectedFile) {
        showToast('Выберите изображение', 'error');
        return;
    }
    
    const balance = await getBalance();
    if (balance < 3) {
        showToast('Недостаточно звезд', 'error');
        return;
    }
    
    startGeneration();
    
    try {
        const previewImg = document.getElementById('previewImg');
        
        // Создаем canvas для 4K (3840x2160 или пропорционально)
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Рассчитываем размеры для 4K с сохранением пропорций
        const maxWidth = 3840;
        const maxHeight = 2160;
        
        let width = previewImg.naturalWidth;
        let height = previewImg.naturalHeight;
        
        if (width > height) {
            if (width > maxWidth) {
                height = Math.round(height * (maxWidth / width));
                width = maxWidth;
            }
        } else {
            if (height > maxHeight) {
                width = Math.round(width * (maxHeight / height));
                height = maxHeight;
            }
        }
        
        // Ограничиваем минимальный размер
        width = Math.max(width, previewImg.naturalWidth);
        height = Math.max(height, previewImg.naturalHeight);
        
        canvas.width = width;
        canvas.height = height;
        
        // Используем Pica для максимально качественного увеличения
        await pica.resize(previewImg, canvas, {
            quality: 3,  // Максимальное качество
            alpha: true,
            unsharpAmount: 0, // Без дополнительной резкости
            unsharpRadius: 0,
            unsharpThreshold: 0
        });
        
        // Сохраняем с максимальным качеством
        currentImage = canvas.toDataURL('image/jpeg', 1.0);
        
        document.getElementById('resultImage').src = currentImage;
        document.getElementById('resultImage').classList.remove('hidden');
        document.getElementById('previewPlaceholder').classList.add('hidden');
        document.getElementById('resultActions').classList.remove('hidden');
        
        endGeneration();
        updateBalance();
        showToast('✅ Изображение улучшено до 4K', 'success');
    } catch (error) {
        console.error('Upscale error:', error);
        showToast('❌ Ошибка улучшения', 'error');
        endGeneration();
    }
}

function startGeneration() {
    isGenerating = true;
    startTime = Date.now();
    document.getElementById('loadingOverlay').classList.remove('hidden');
    document.getElementById('generateBtn').disabled = true;
    
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const timer = document.getElementById('loadingTimer');
        if (timer) timer.textContent = `${elapsed}с`;
    }, 1000);
}

function endGeneration() {
    isGenerating = false;
    document.getElementById('loadingOverlay').classList.add('hidden');
    document.getElementById('generateBtn').disabled = false;
    clearInterval(timerInterval);
}

async function sendToBot() {
    if (!currentImage) {
        showToast('❌ Нет изображения для отправки', 'error');
        return;
    }
    
    showToast('📤 Отправка в бот...', 'info');
    
    try {
        // Конвертируем dataURL в Blob
        const response = await fetch(currentImage);
        const blob = await response.blob();
        
        // Получаем user_id из Telegram
        const user = getTelegramUser();
        const userId = user.tg_user_id;
        
        if (!userId) {
            showToast('❌ Не удалось получить ID пользователя', 'error');
            return;
        }
        
        // Создаем FormData для отправки
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('image', blob, `${originalFileName || '4k'}.jpg`);
        formData.append('filename', `${originalFileName || '4k'}.jpg`);
        
        // Отправляем на ваш сервер
        const serverResponse = await fetch(`${API_BASE}/api/send-photo`, {
            method: 'POST',
            body: formData
        });
        
        const result = await serverResponse.json();
        
        if (result.success) {
            showToast('✅ 4K изображение отправлено в Telegram!', 'success');
        } else {
            showToast('❌ Ошибка отправки: ' + (result.error || 'Неизвестная ошибка'), 'error');
        }
        
    } catch (error) {
        console.error('Send to bot error:', error);
        showToast('❌ Ошибка отправки', 'error');
    }
}

function regenerateImage() {
    generateImage();
}