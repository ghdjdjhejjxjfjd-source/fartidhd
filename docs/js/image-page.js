// docs/js/image-page.js
import { MODES, setMode, getMode, setFile, getFile, resetState } from './image.js';
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
        card.innerHTML = `
            <div class="mode-emoji">${mode.emoji}</div>
            <div class="mode-name">${mode.name}</div>
            <div class="mode-desc">${mode.description}</div>
            <div class="mode-price">⭐ ${mode.price}</div>
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
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchGalleryTab(e.target.dataset.tab));
    });
    
    document.getElementById('generateFromEmptyBtn')?.addEventListener('click', () => {
        showScreen(mainScreen);
    });
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
            ${img.favorite ? '<div style="position:absolute; top:8px; right:8px;">❤️</div>' : ''}
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
    if (!prompt) {
        showToast('Введите описание', 'error');
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
        const name = card.querySelector('.mode-name')?.textContent.toLowerCase() || '';
        const desc = card.querySelector('.mode-desc')?.textContent.toLowerCase() || '';
        card.style.display = (name.includes(search) || desc.includes(search)) ? 'flex' : 'none';
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
    return 100;
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