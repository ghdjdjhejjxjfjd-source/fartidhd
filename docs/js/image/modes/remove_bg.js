// docs/js/image/modes/remove_bg.js

import { showToast, getBalance, updateBalance } from '../shared/utils.js';
import { addToGallery } from '../shared/gallery.js';

let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;
let selectedFile = null;

// Инициализация режима "Удалить фон"
export function initRemoveBg(container) {
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
                <div class="placeholder-icon">✂️</div>
                <div class="placeholder-text">Результат появится здесь</div>
            </div>
            <img class="result-image hidden" id="resultImage" alt="Generated image">
            
            <div class="loading-overlay hidden" id="loadingOverlay">
                <div class="spinner"></div>
                <div class="loading-text">Удаление фона... <span id="loadingTimer">0с</span></div>
            </div>
        </div>

        <div class="prompt-area">
            <textarea 
                id="promptInput" 
                placeholder="Дополнительные инструкции (опционально)..." 
                rows="2"
                maxlength="500"
            ></textarea>
        </div>

        <button class="generate-btn" id="generateBtn">
            <span class="btn-icon">✂️</span>
            Удалить фон
            <span class="price-tag" id="generatePrice">6⭐</span>
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
    
    // Обработчики
    document.getElementById('pickFileBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    document.getElementById('removeFileBtn').addEventListener('click', removeFile);
    document.getElementById('generateBtn').addEventListener('click', generateImage);
    document.getElementById('saveToGalleryBtn').addEventListener('click', saveToGallery);
    document.getElementById('downloadBtn').addEventListener('click', downloadImage);
    document.getElementById('copyPromptBtn').addEventListener('click', copyPrompt);
    document.getElementById('regenerateBtn').addEventListener('click', regenerateImage);
    document.getElementById('enhanceBtn').addEventListener('click', enhanceCurrentImage);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showToast('Пожалуйста, выберите изображение', 'error');
        return;
    }
    
    selectedFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        const previewImg = document.getElementById('previewImg');
        const filePreview = document.getElementById('filePreview');
        
        previewImg.src = e.target.result;
        filePreview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function removeFile() {
    selectedFile = null;
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
    if (balance < 6) {
        showToast('Недостаточно звезд', 'error');
        return;
    }
    
    startGeneration();
    
    // Имитация удаления фона
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
        showToast('Фон удален!', 'success');
    }, 3500);
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
    
    const imageData = {
        id: Date.now().toString(),
        dataUrl: currentImage,
        prompt: document.getElementById('promptInput')?.value || 'Удаление фона',
        mode: 'remove_bg',
        modeName: 'Удалить фон',
        cost: 6,
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
async function enhanceCurrentImage() {
    if (!currentImage) return;
    
    showToast('✨ Улучшаем качество...', 'info');
    
    try {
        const enhancedImage = await enhanceTo4K(currentImage);
        currentImage = enhancedImage;
        document.getElementById('resultImage').src = enhancedImage;
        showToast('✅ Качество улучшено!', 'success');
    } catch (error) {
        showToast('❌ Ошибка улучшения', 'error');
    }
}

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
            
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.min(255, Math.max(0, (data[i] - 128) * 1.1 + 128));
                data[i+1] = Math.min(255, Math.max(0, (data[i+1] - 128) * 1.1 + 128));
                data[i+2] = Math.min(255, Math.max(0, (data[i+2] - 128) * 1.1 + 128));
            }
            
            for (let i = 0; i < data.length; i += 4) {
                const gray = (data[i] + data[i+1] + data[i+2]) / 3;
                data[i] = Math.min(255, gray + (data[i] - gray) * 1.2);
                data[i+1] = Math.min(255, gray + (data[i+1] - gray) * 1.2);
                data[i+2] = Math.min(255, gray + (data[i+2] - gray) * 1.2);
            }
            
            ctx.putImageData(imageData, 0, 0);
            resolve(canvas.toDataURL('image/jpeg', 1.0));
        };
        
        img.onerror = () => resolve(imageUrl);
    });
}