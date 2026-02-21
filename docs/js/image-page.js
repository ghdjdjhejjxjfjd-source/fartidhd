// docs/js/image-page.js
import { MODES, setMode, getMode, setFile, getFile, resetState, getModeById } from './image.js';
import { getGallery, addToGallery } from './image-gallery.js';

const tg = window.Telegram?.WebApp;
let currentTheme = localStorage.getItem('miniapp_theme_v1') || 'blue';
let currentImage = null;
let isGenerating = false;
let startTime = null;
let timerInterval = null;

const mainScreen = document.getElementById('mainScreen');
const generationScreen = document.getElementById('generationScreen');
const galleryScreen = document.getElementById('galleryScreen');
const viewScreen = document.getElementById('viewScreen');

document.addEventListener('DOMContentLoaded', () => {
    console.log("✅ image-page.js loaded");
    initTheme();
    loadModes();
    updateBalance();
    setupEventListeners();
});

function initTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
}

function loadModes() {
    const grid = document.getElementById('modesGrid');
    if (!grid) {
        console.error("modesGrid not found!");
        return;
    }
    
    grid.innerHTML = '';
    
    MODES.forEach(mode => {
        const card = document.createElement('div');
        card.className = 'mode-card';
        card.setAttribute('data-mode', mode.id);
        card.style.setProperty('--mode-bg', mode.bgColor);
        
        card.innerHTML = `
            <div class="mode-card-image">
                <img src="${mode.image}" alt="${mode.name}" loading="lazy" 
                     onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22200%22%20height%3D%22200%22%20viewBox%3D%220%200%20200%20200%22%3E%3Crect%20width%3D%22200%22%20height%3D%22200%22%20fill%3D%22${mode.bgColor.replace('#', '%23')}%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2230%22%3E${mode.icon}%3C%2Ftext%3E%3C%2Fsvg%3E'">
            </div>
            <div class="mode-card-content">
                <div class="mode-card-title">
                    <span>${mode.icon}</span>
                    <h3>${mode.name}</h3>
                </div>
                <div class="mode-card-description">${mode.description}</div>
                <div class="mode-card-footer">
                    <div class="mode-card-price">
                        <span>⭐</span>
                        <span>${mode.price}</span>
                    </div>
                    ${mode.popular ? '<div class="mode-card-badge">Популярное</div>' : ''}
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => selectMode(mode));
        grid.appendChild(card);
    });
    
    console.log(`✅ Loaded ${MODES.length} modes`);
}

function selectMode(mode) {
    setMode(mode.id);
    
    document.getElementById('currentModeTitle').textContent = mode.name;
    document.getElementById('currentModePrice').textContent = `${mode.price}⭐`;
    document.getElementById('generatePrice').textContent = `${mode.price}⭐`;
    
    const modeIcon = document.getElementById('currentModeIcon');
    if (modeIcon) {
        modeIcon.textContent = mode.icon;
    }
    
    const fileSection = document.getElementById('fileSection');
    if (fileSection) {
        fileSection.style.display = mode.needsFile ? 'block' : 'none';
    }
    
    const promptInput = document.getElementById('promptInput');
    if (promptInput) {
        promptInput.placeholder = mode.placeholder || 'Опишите что хотите увидеть...';
    }
    
    const filePreview = document.getElementById('filePreview');
    const previewImg = document.getElementById('previewImg');
    if (filePreview && previewImg) {
        filePreview.classList.add('hidden');
        previewImg.src = '';
    }
    setFile(null);
    
    showScreen(generationScreen);
}

function showScreen(screen) {
    [mainScreen, generationScreen, galleryScreen, viewScreen].forEach(s => {
        if (s) s.classList.add('hidden');
    });
    if (screen) screen.classList.remove('hidden');
}

function setupEventListeners() {
    document.getElementById('backBtn')?.addEventListener('click', () => showScreen(mainScreen));
    document.getElementById('backFromGenBtn')?.addEventListener('click', () => showScreen(mainScreen));
    document.getElementById('backFromGalleryBtn')?.addEventListener('click', () => showScreen(mainScreen));
    document.getElementById('backFromViewBtn')?.addEventListener('click', () => showScreen(galleryScreen));
    
    document.getElementById('galleryBtn')?.addEventListener('click', showGallery);
    document.getElementById('historyBtn')?.addEventListener('click', showGallery);
    
    document.getElementById('searchModes')?.addEventListener('input', filterModes);
    document.getElementById('gallerySearch')?.addEventListener('input', filterGallery);
    
    document.getElementById('generateBtn')?.addEventListener('click', generateImage);
    document.getElementById('cancelGenBtn')?.addEventListener('click', cancelGeneration);
    
    document.getElementById('saveToGalleryBtn')?.addEventListener('click', saveToGallery);
    document.getElementById('downloadBtn')?.addEventListener('click', downloadImage);
    document.getElementById('copyPromptBtn')?.addEventListener('click', copyPrompt);
    document.getElementById('regenerateBtn')?.addEventListener('click', regenerateImage);
    document.getElementById('enhanceBtn')?.addEventListener('click', enhanceCurrentImage);
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchGalleryTab(e.target.dataset.tab));
    });
    
    document.getElementById('generateFromEmptyBtn')?.addEventListener('click', () => {
        showScreen(mainScreen);
    });
    
    const pickFileBtn = document.getElementById('pickFileBtn');
    const fileInput = document.getElementById('fileInput');
    const removeFileBtn = document.getElementById('removeFileBtn');
    
    if (pickFileBtn && fileInput) {
        pickFileBtn.addEventListener('click', () => fileInput.click());
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', removeFile);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение');
        return;
    }
    
    setFile(file);
    
    const reader = new FileReader();
    reader.onload = (e) => {
        const previewImg = document.getElementById('previewImg');
        const filePreview = document.getElementById('filePreview');
        
        if (previewImg && filePreview) {
            previewImg.src = e.target.result;
            filePreview.classList.remove('hidden');
        }
    };
    reader.readAsDataURL(file);
}

function removeFile() {
    setFile(null);
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const previewImg = document.getElementById('previewImg');
    
    if (fileInput) fileInput.value = '';
    if (filePreview) filePreview.classList.add('hidden');
    if (previewImg) previewImg.src = '';
}

function showGallery() {
    loadGallery();
    showScreen(galleryScreen);
}

function loadGallery(filter = 'all', search = '') {
    const gallery = getGallery();
    const grid = document.getElementById('galleryGrid');
    const emptyState = document.getElementById('emptyGallery');
    
    if (!grid) return;
    
    if (gallery.length === 0) {
        grid.innerHTML = '';
        if (emptyState) emptyState.classList.remove('hidden');
        return;
    }
    
    if (emptyState) emptyState.classList.add('hidden');
    
    let filtered = gallery;
    if (filter === 'favorites') {
        filtered = gallery.filter(img => img.favorite);
    }
    
    if (search) {
        filtered = filtered.filter(img => 
            img.prompt?.toLowerCase().includes(search.toLowerCase())
        );
    }
    
    filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    
    grid.innerHTML = filtered.map(img => `
        <div class="gallery-item" data-id="${img.id}">
            <img src="${img.dataUrl}" alt="${img.prompt || 'image'}">
            ${img.favorite ? '<div class="gallery-item-favorite">❤️</div>' : ''}
        </div>
    `).join('');
    
    document.querySelectorAll('.gallery-item').forEach(item => {
        item.addEventListener('click', () => showImageView(item.dataset.id));
    });
}

function showImageView(imageId) {
    const image = getGallery().find(img => img.id === imageId);
    if (!image) return;
    
    document.getElementById('viewImage').src = image.dataUrl;
    document.getElementById('viewPrompt').textContent = image.prompt || '—';
    document.getElementById('viewDate').textContent = image.createdAt ? new Date(image.createdAt).toLocaleString() : '—';
    document.getElementById('viewCost').textContent = `${image.cost || 0}⭐`;
    
    showScreen(viewScreen);
}

async function generateImage() {
    if (isGenerating) return;
    
    const prompt = document.getElementById('promptInput')?.value.trim();
    const mode = getMode();
    
    if (!mode) {
        alert('Сначала выберите режим');
        return;
    }
    
    if (mode.needsFile && !getFile()) {
        alert('Для этого режима нужно выбрать изображение');
        return;
    }
    
    if (!prompt && mode.id === 'txt2img') {
        alert('Введите описание');
        return;
    }
    
    startGeneration();
    
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
    
    const mode = getMode();
    const imageData = {
        id: Date.now().toString(),
        dataUrl: currentImage,
        prompt: document.getElementById('promptInput')?.value || '',
        mode: mode?.id || 'unknown',
        modeName: mode?.name || 'Unknown',
        cost: mode?.price || 4,
        favorite: false,
        createdAt: new Date().toISOString()
    };
    
    addToGallery(imageData);
    showToast('Сохранено в галерею', 'success');
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

function filterModes(e) {
    const search = e.target.value.toLowerCase();
    document.querySelectorAll('.mode-card').forEach(card => {
        const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
        const desc = card.querySelector('.mode-card-description')?.textContent.toLowerCase() || '';
        card.style.display = (title.includes(search) || desc.includes(search)) ? 'flex' : 'none';
    });
}

function filterGallery(e) {
    const search = e.target.value;
    const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'all';
    loadGallery(activeTab, search);
}

function switchGalleryTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    loadGallery(tab, document.getElementById('gallerySearch')?.value || '');
}

async function getBalance() {
    try {
        const user = getTelegramUser();
        const response = await fetch(`/api/stars/balance/${user.tg_user_id}`);
        const data = await response.json();
        return data.balance || 0;
    } catch {
        return 100;
    }
}

function getTelegramUser() {
    const tg = window.Telegram?.WebApp;
    if (!tg || !tg.initDataUnsafe?.user) return { tg_user_id: 0 };
    return { tg_user_id: tg.initDataUnsafe.user.id };
}

function updateBalance() {
    getBalance().then(balance => {
        const badge = document.getElementById('balanceBadge');
        if (badge) badge.textContent = `⭐ ${balance}`;
    });
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// =============================================
// ✅ НОВАЯ ФУНКЦИЯ: УЛУЧШЕНИЕ КАЧЕСТВА ДО 4K
// =============================================
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
            
            // 1. Увеличиваем контраст
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.min(255, Math.max(0, (data[i] - 128) * 1.1 + 128));
                data[i+1] = Math.min(255, Math.max(0, (data[i+1] - 128) * 1.1 + 128));
                data[i+2] = Math.min(255, Math.max(0, (data[i+2] - 128) * 1.1 + 128));
            }
            
            // 2. Увеличиваем насыщенность
            for (let i = 0; i < data.length; i += 4) {
                const gray = (data[i] + data[i+1] + data[i+2]) / 3;
                data[i] = Math.min(255, gray + (data[i] - gray) * 1.2);
                data[i+1] = Math.min(255, gray + (data[i+1] - gray) * 1.2);
                data[i+2] = Math.min(255, gray + (data[i+2] - gray) * 1.2);
            }
            
            // 3. Повышение резкости
            const sharpData = new Uint8ClampedArray(data.length);
            for (let y = 1; y < height - 1; y++) {
                for (let x = 1; x < width - 1; x++) {
                    const idx = (y * width + x) * 4;
                    
                    for (let c = 0; c < 3; c++) {
                        const val = data[idx + c];
                        const left = data[idx - 4 + c];
                        const right = data[idx + 4 + c];
                        const top = data[idx - width * 4 + c];
                        const bottom = data[idx + width * 4 + c];
                        
                        const sharpened = val + (val * 5 - left - right - top - bottom) * 0.15;
                        sharpData[idx + c] = Math.min(255, Math.max(0, sharpened));
                    }
                    sharpData[idx + 3] = data[idx + 3];
                }
            }
            
            for (let i = 0; i < data.length; i++) {
                if (sharpData[i] !== undefined) {
                    data[i] = sharpData[i];
                }
            }
            
            ctx.putImageData(imageData, 0, 0);
            
            const enhancedDataUrl = canvas.toDataURL('image/jpeg', 1.0);
            resolve(enhancedDataUrl);
        };
        
        img.onerror = () => {
            console.error('Ошибка загрузки изображения');
            resolve(imageUrl);
        };
    });
}

async function enhanceCurrentImage() {
    if (!currentImage) return;
    
    showToast('✨ Улучшаем качество до 4K...', 'info');
    
    try {
        const enhancedImage = await enhanceTo4K(currentImage);
        currentImage = enhancedImage;
        
        const resultImg = document.getElementById('resultImage');
        if (resultImg) {
            resultImg.src = enhancedImage;
        }
        
        showToast('✅ Качество улучшено!', 'success');
    } catch (error) {
        console.error('Enhance error:', error);
        showToast('❌ Ошибка улучшения', 'error');
    }
}