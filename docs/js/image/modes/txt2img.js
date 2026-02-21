// docs/js/image/modes/txt2img.js

import { showToast, getBalance, updateBalance, setupKeyboardDismiss } from '../shared/utils.js';
import { addToGallery } from '../shared/gallery.js';

let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;

export function initTxt2Img(container) {
    container.innerHTML = `
        <div class="result-area" id="resultArea">
            <div class="preview-placeholder" id="previewPlaceholder">
                <div class="placeholder-icon">🖼️</div>
                <div class="placeholder-text">Изображение появится здесь</div>
            </div>
            <img class="result-image hidden" id="resultImage" alt="Generated image">
            
            <div class="loading-overlay hidden" id="loadingOverlay">
                <div class="spinner"></div>
                <div class="loading-text">Генерация... <span id="loadingTimer">0с</span></div>
            </div>
        </div>

        <div class="prompt-area">
            <textarea 
                id="promptInput" 
                placeholder="Опишите что хотите увидеть..." 
                rows="3"
                maxlength="1000"
            ></textarea>
        </div>

        <button class="generate-btn" id="generateBtn">
            <span class="btn-icon">✨</span>
            Сгенерировать
            <span class="price-tag" id="generatePrice">4⭐</span>
        </button>

        <div class="result-actions hidden" id="resultActions">
            <div class="action-row">
                <button class="action-btn" id="saveToGalleryBtn" title="Сохранить">💾</button>
                <button class="action-btn" id="regenerateBtn" title="Заново">🔄</button>
            </div>
        </div>
    `;
    
    // Настройка закрытия клавиатуры
    const chatArea = document.querySelector('.wrap');
    if (chatArea) {
        setupKeyboardDismiss(chatArea);
    }
    
    document.getElementById('generateBtn').addEventListener('click', generateImage);
    document.getElementById('saveToGalleryBtn').addEventListener('click', saveToGallery);
    document.getElementById('regenerateBtn').addEventListener('click', regenerateImage);
}

async function generateImage() {
    if (isGenerating) return;
    
    const prompt = document.getElementById('promptInput')?.value.trim();
    
    if (!prompt) {
        showToast('Введите описание', 'error');
        return;
    }
    
    const balance = await getBalance();
    if (balance < 4) {
        showToast('Недостаточно звезд', 'error');
        return;
    }
    
    startGeneration();
    
    setTimeout(() => {
        const mockImage = `https://picsum.photos/1024/1024?random=${Date.now()}`;
        currentImage = mockImage;
        
        const resultImg = document.getElementById('resultImage');
        const placeholder = document.getElementById('previewPlaceholder');
        const actions = document.getElementById('resultActions');
        
        resultImg.src = mockImage;
        resultImg.classList.remove('hidden');
        placeholder.classList.add('hidden');
        actions.classList.remove('hidden');
        
        endGeneration();
        updateBalance();
        showToast('Готово!', 'success');
    }, 3000);
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
    if (!currentImage) return;
    
    const prompt = document.getElementById('promptInput')?.value || 'Сгенерировано';
    
    const imageData = {
        id: Date.now().toString(),
        dataUrl: currentImage,
        prompt: prompt,
        mode: 'txt2img',
        modeName: 'Генерация',
        cost: 4,
        favorite: false,
        createdAt: new Date().toISOString()
    };
    
    addToGallery(imageData);
    downloadImage();
}

function downloadImage() {
    if (!currentImage) return;
    
    const link = document.createElement('a');
    link.download = `generated_${Date.now()}.jpg`;
    link.href = currentImage;
    link.click();
    showToast('Файл сохранен!', 'success');
}

function regenerateImage() {
    generateImage();
}