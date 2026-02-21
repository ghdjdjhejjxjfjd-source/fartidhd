// docs/js/image/modes/upscale.js

import { showToast, getBalance, updateBalance, setupKeyboardDismiss } from '../shared/utils.js';
import { addToGallery } from '../shared/gallery.js';

let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;
let selectedFile = null;
let originalFileName = null;

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
        
        // Сохраняем в галерею
        const success = addToGallery(imageData);
        
        if (success) {
            showToast('✅ Сохранено в галерею', 'success');
            // Скачиваем файл
            downloadImage();
        } else {
            showToast('❌ Ошибка сохранения', 'error');
        }
    } catch (error) {
        console.error('Save error:', error);
        showToast('❌ Ошибка сохранения', 'error');
    }
}

function downloadImage() {
    if (!currentImage) return;
    
    try {
        const link = document.createElement('a');
        const filename = originalFileName 
            ? `${originalFileName}_enhanced.jpg` 
            : `enhanced_${Date.now()}.jpg`;
        
        link.download = filename;
        link.href = currentImage;
        link.click();
        showToast('📥 Файл скачан', 'success');
    } catch (error) {
        console.error('Download error:', error);
        showToast('❌ Ошибка скачивания', 'error');
    }
}

function regenerateImage() {
    generateImage();
}