// docs/js/image/modes/upscale.js

import { showToast, getBalance, updateBalance, setupKeyboardDismiss, getTelegramUser } from '../shared/utils.js';
import { addToGallery } from '../shared/gallery.js';

let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;
let selectedFile = null;
let originalFileName = null;

const BOT_TOKEN = window.Telegram?.WebApp?.initDataUnsafe?.bot_token || 'YOUR_BOT_TOKEN';
const API_BASE = "https://api.telegram.org/bot";

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
                <div class="placeholder-text">Результат появится здесь</div>
            </div>
            <img class="result-image hidden" id="resultImage" alt="Upscaled image">
            
            <div class="loading-overlay hidden" id="loadingOverlay">
                <div class="spinner"></div>
                <div class="loading-text">Улучшение качества... <span id="loadingTimer">0с</span></div>
            </div>
        </div>

        <button class="generate-btn" id="generateBtn">
            <span class="btn-icon">🔍</span>
            Улучшить качество
            <span class="price-tag" id="generatePrice">3⭐</span>
        </button>

        <div class="result-actions hidden" id="resultActions">
            <div class="action-row">
                <button class="action-btn" id="saveToGalleryBtn" title="Сохранить">💾</button>
                <button class="action-btn" id="sendToBotBtn" title="Отправить в бот">📤</button>
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
    document.getElementById('saveToGalleryBtn').addEventListener('click', saveToGallery);
    document.getElementById('sendToBotBtn').addEventListener('click', sendToBot);
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
    
    // Реальное улучшение качества
    setTimeout(() => {
        try {
            const previewImg = document.getElementById('previewImg');
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = previewImg.naturalWidth * 2;
            canvas.height = previewImg.naturalHeight * 2;
            
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';
            ctx.drawImage(previewImg, 0, 0, canvas.width, canvas.height);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.min(255, Math.max(0, (data[i] - 128) * 1.15 + 128));
                data[i+1] = Math.min(255, Math.max(0, (data[i+1] - 128) * 1.15 + 128));
                data[i+2] = Math.min(255, Math.max(0, (data[i+2] - 128) * 1.15 + 128));
            }
            
            ctx.putImageData(imageData, 0, 0);
            currentImage = canvas.toDataURL('image/jpeg', 0.95);
            
            document.getElementById('resultImage').src = currentImage;
            document.getElementById('resultImage').classList.remove('hidden');
            document.getElementById('previewPlaceholder').classList.add('hidden');
            document.getElementById('resultActions').classList.remove('hidden');
            
            endGeneration();
            updateBalance();
            showToast('✅ Качество улучшено!', 'success');
        } catch (error) {
            console.error('Upscale error:', error);
            showToast('❌ Ошибка улучшения', 'error');
            endGeneration();
        }
    }, 2000);
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

function saveToGallery() {
    if (!currentImage) {
        showToast('❌ Нет изображения для сохранения', 'error');
        return;
    }
    
    try {
        const imageData = {
            id: Date.now().toString(),
            dataUrl: currentImage,
            prompt: `✨ Улучшено: ${originalFileName || 'изображение'}`,
            mode: 'upscale',
            modeName: 'Улучшить качество',
            cost: 3,
            favorite: false,
            createdAt: new Date().toISOString()
        };
        
        const success = addToGallery(imageData);
        
        if (success) {
            showToast('✅ Сохранено в галерею', 'success');
        } else {
            showToast('❌ Ошибка сохранения', 'error');
        }
    } catch (error) {
        console.error('Save error:', error);
        showToast('❌ Ошибка сохранения', 'error');
    }
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
        
        // Создаем FormData для отправки фото
        const formData = new FormData();
        formData.append('chat_id', userId);
        formData.append('photo', blob, `${originalFileName || 'enhanced'}.jpg`);
        formData.append('caption', `✨ Улучшенное качество\n🆔 ID: ${userId}\n📝 Файл: ${originalFileName || 'image'}`);
        
        // Отправляем в Telegram
        const botToken = window.Telegram?.WebApp?.initDataUnsafe?.bot_token;
        if (!botToken) {
            showToast('❌ Токен бота не найден', 'error');
            return;
        }
        
        const telegramResponse = await fetch(`https://api.telegram.org/bot${botToken}/sendPhoto`, {
            method: 'POST',
            body: formData
        });
        
        const result = await telegramResponse.json();
        
        if (result.ok) {
            showToast('✅ Изображение отправлено в бот!', 'success');
            
            // Дополнительно отправляем в мини-приложение
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.sendData(JSON.stringify({
                    type: 'enhanced_image',
                    url: currentImage,
                    filename: `${originalFileName || 'enhanced'}.jpg`
                }));
            }
        } else {
            showToast('❌ Ошибка отправки: ' + (result.description || 'Неизвестная ошибка'), 'error');
            console.error('Telegram API error:', result);
        }
        
    } catch (error) {
        console.error('Send to bot error:', error);
        showToast('❌ Ошибка отправки', 'error');
    }
}

function regenerateImage() {
    generateImage();
}