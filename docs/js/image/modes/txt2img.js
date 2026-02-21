// docs/js/image/modes/txt2img.js

import { showToast, getBalance, updateBalance } from '../shared/utils.js';
import { addToGallery } from '../shared/gallery.js';

let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;

// Инициализация режима "Генерация из текста"
export function initTxt2Img(container) {
    // Очищаем контейнер
    container.innerHTML = '';
    
    // Создаем HTML для режима
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
                <button class="cancel-btn" id="cancelGenBtn">✖ Отмена</button>
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
                <button class="action-btn" id="saveToGalleryBtn">
                    <span class="btn-icon">💾</span> Сохранить
                </button>
                <button class="action-btn" id="downloadBtn">
                    <span class="btn-icon">📥</span> Скачать
                </button>
                <button class="action-btn" id="enhanceBtn">
                    <span class="btn-icon">✨</span> 4K
                </button>
            </div>
            <div class="action-row">
                <button class="action-btn" id="copyPromptBtn">
                    <span class="btn-icon">📋</span> Копировать
                </button>
                <button class="action-btn" id="regenerateBtn">
                    <span class="btn-icon">🔄</span> Заново
                </button>
            </div>
        </div>
    `;
    
    // Добавляем обработчики событий
    document.getElementById('generateBtn').addEventListener('click', generateImage);
    document.getElementById('cancelGenBtn').addEventListener('click', cancelGeneration);
    document.getElementById('saveToGalleryBtn').addEventListener('click', saveToGallery);
    document.getElementById('downloadBtn').addEventListener('click', downloadImage);
    document.getElementById('copyPromptBtn').addEventListener('click', copyPrompt);
    document.getElementById('regenerateBtn').addEventListener('click', regenerateImage);
    document.getElementById('enhanceBtn').addEventListener('click', enhanceCurrentImage);
}

// Генерация изображения
async function generateImage() {
    if (isGenerating) return;
    
    const prompt = document.getElementById('promptInput')?.value.trim();
    
    if (!prompt) {
        showToast('Введите описание', 'error');
        return;
    }
    
    // Проверка баланса
    const balance = await getBalance();
    if (balance < 4) {
        showToast('Недостаточно звезд', 'error');
        return;
    }
    
    startGeneration();
    
    // Имитация генерации (заменить на реальный API)
    setTimeout(() => {
        const mockImage = `https://picsum.photos/1024/1024?random=${Date.now()}`;
        currentImage = mockImage;
        
        const resultImg = document.getElementById('resultImage');
        const placeholder = document.getElementById('previewPlaceholder');
        const actions = document.getElementById('resultActions');
        
        if (resultImg) {
            resultImg.src = mockImage;
            resultImg.classList.remove('hidden');
        }
        if (placeholder) placeholder.classList.add('hidden');
        if (actions) actions.classList.remove('hidden');
        
        endGeneration();
        updateBalance();
        showToast('Готово!', 'success');
    }, 3000);
}

function startGeneration() {
    isGenerating = true;
    startTime = Date.now();
    const overlay = document.getElementById('loadingOverlay');
    const btn = document.getElementById('generateBtn');
    
    if (overlay) overlay.classList.remove('hidden');
    if (btn) btn.disabled = true;
    
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const timer = document.getElementById('loadingTimer');
        if (timer) timer.textContent = `${elapsed}с`;
    }, 1000);
}

function endGeneration() {
    isGenerating = false;
    const overlay = document.getElementById('loadingOverlay');
    const btn = document.getElementById('generateBtn');
    
    if (overlay) overlay.classList.add('hidden');
    if (btn) btn.disabled = false;
    
    clearInterval(timerInterval);
}

function cancelGeneration() {
    endGeneration();
    showToast('Отменено', 'info');
}

function saveToGallery() {
    if (!currentImage) return;
    
    const imageData = {
        id: Date.now().toString(),
        dataUrl: currentImage,
        prompt: document.getElementById('promptInput')?.value || '',
        mode: 'txt2img',
        modeName: 'Генерация',
        cost: 4,
        favorite: false,
        createdAt: new Date().toISOString()
    };
    
    addToGallery(imageData);
}

function downloadImage() {
    if (!currentImage) return;
    const link = document.createElement('a');
    link.download = `image-${Date.now()}.png`;
    link.href = currentImage;
    link.click();
    showToast('Скачивание...', 'success');
}

function copyPrompt() {
    const prompt = document.getElementById('promptInput')?.value;
    if (prompt) {
        navigator.clipboard?.writeText(prompt);
        showToast('Промпт скопирован', 'success');
    }
}

function regenerateImage() {
    generateImage();
}

// Улучшение качества
function enhanceTo4K(imageUrl) {
    return new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = "Anonymous";
        img.src = imageUrl;
        
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d', { alpha: false });
            
            canvas.width = img.width;
            canvas.height = img.height;
            
            ctx.drawImage(img, 0, 0);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            const width = canvas.width;
            const height = canvas.height;
            
            // Увеличиваем контраст
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.min(255, Math.max(0, (data[i] - 128) * 1.1 + 128));
                data[i+1] = Math.min(255, Math.max(0, (data[i+1] - 128) * 1.1 + 128));
                data[i+2] = Math.min(255, Math.max(0, (data[i+2] - 128) * 1.1 + 128));
            }
            
            // Увеличиваем насыщенность
            for (let i = 0; i < data.length; i += 4) {
                const gray = (data[i] + data[i+1] + data[i+2]) / 3;
                data[i] = Math.min(255, gray + (data[i] - gray) * 1.2);
                data[i+1] = Math.min(255, gray + (data[i+1] - gray) * 1.2);
                data[i+2] = Math.min(255, gray + (data[i+2] - gray) * 1.2);
            }
            
            ctx.putImageData(imageData, 0, 0);
            
            const enhancedDataUrl = canvas.toDataURL('image/jpeg', 1.0);
            resolve(enhancedDataUrl);
        };
        
        img.onerror = () => resolve(imageUrl);
    });
}

async function enhanceCurrentImage() {
    if (!currentImage) return;
    
    showToast('✨ Улучшаем качество...', 'info');
    
    try {
        const enhancedImage = await enhanceTo4K(currentImage);
        currentImage = enhancedImage;
        
        const resultImg = document.getElementById('resultImage');
        if (resultImg) {
            resultImg.src = enhancedImage;
        }
        
        showToast('✅ Качество улучшено!', 'success');
    } catch (error) {
        showToast('❌ Ошибка улучшения', 'error');
    }
}