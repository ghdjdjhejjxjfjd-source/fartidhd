// docs/js/image/modes/remove_bg.js

import { showToast, getBalance, updateBalance, setupKeyboardDismiss } from '../shared/utils.js';
import { addToGallery } from '../shared/gallery.js';

let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;
let selectedFile = null;
let originalFileName = null;

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

        <button class="generate-btn" id="generateBtn">
            <span class="btn-icon">✂️</span>
            Удалить фон
            <span class="price-tag" id="generatePrice">6⭐</span>
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
    if (balance < 6) {
        showToast('Недостаточно звезд', 'error');
        return;
    }
    
    startGeneration();
    
    setTimeout(() => {
        const mockImage = `https://picsum.photos/1024/1024?random=${Date.now()}`;
        currentImage = mockImage;
        
        document.getElementById('resultImage').src = mockImage;
        document.getElementById('resultImage').classList.remove('hidden');
        document.getElementById('previewPlaceholder').classList.add('hidden');
        document.getElementById('resultActions').classList.remove('hidden');
        
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
        prompt: 'Удаление фона',
        mode: 'remove_bg',
        modeName: 'Удалить фон',
        cost: 6,
        favorite: false,
        createdAt: new Date().toISOString()
    };
    
    addToGallery(imageData);
    downloadImage();
}

function downloadImage() {
    if (!currentImage) return;
    
    const link = document.createElement('a');
    const filename = originalFileName 
        ? `${originalFileName}_nobg.jpg` 
        : `nobg_${Date.now()}.jpg`;
    
    link.download = filename;
    link.href = currentImage;
    link.click();
    showToast('Файл сохранен!', 'success');
}

function regenerateImage() {
    generateImage();
}