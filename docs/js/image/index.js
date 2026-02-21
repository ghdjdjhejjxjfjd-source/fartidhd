import { MODES } from './modes/data.js';
import { initTxt2Img } from './modes/txt2img.js';
import { initImg2Img } from './modes/img2img.js';
import { initRemoveBg } from './modes/remove_bg.js';
import { initInpaint } from './modes/inpaint.js';
import { initUpscale } from './modes/upscale.js';
import { initGallery } from './shared/gallery.js';
import { showToast, updateBalance, showScreen } from './shared/utils.js';

const tg = window.Telegram?.WebApp;
let currentTheme = localStorage.getItem('miniapp_theme_v1') || 'blue';

const mainScreen = document.getElementById('mainScreen');
const generationScreen = document.getElementById('generationScreen');
const galleryScreen = document.getElementById('galleryScreen');
const viewScreen = document.getElementById('viewScreen');

document.addEventListener('DOMContentLoaded', () => {
    console.log("✅ Image module loaded");
    initTheme();
    loadModes();
    updateBalance();
    setupEventListeners();
    initGallery();
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
                <img src="${mode.image}" alt="${mode.name}" loading="lazy">
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
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => selectMode(mode));
        grid.appendChild(card);
    });
    
    console.log(`✅ Loaded ${MODES.length} modes`);
}

function selectMode(mode) {
    document.getElementById('currentModeTitle').textContent = mode.name;
    document.getElementById('currentModePrice').textContent = `${mode.price}⭐`;
    
    const modeIcon = document.getElementById('currentModeIcon');
    if (modeIcon) {
        modeIcon.textContent = mode.icon;
    }
    
    const generationContent = document.getElementById('generationContent');
    generationContent.innerHTML = '';
    
    switch(mode.id) {
        case 'txt2img':
            initTxt2Img(generationContent);
            break;
        case 'img2img':
            initImg2Img(generationContent);
            break;
        case 'remove_bg':
            initRemoveBg(generationContent);
            break;
        case 'inpaint':
            initInpaint(generationContent);
            break;
        case 'upscale':
            initUpscale(generationContent);
            break;
    }
    
    showScreen([mainScreen, galleryScreen, viewScreen], generationScreen);
}

function setupEventListeners() {
    document.getElementById('backBtn')?.addEventListener('click', () => {
        showScreen([generationScreen, galleryScreen, viewScreen], mainScreen);
    });
    
    document.getElementById('backFromGenBtn')?.addEventListener('click', () => {
        showScreen([generationScreen, galleryScreen, viewScreen], mainScreen);
    });
    
    document.getElementById('backFromGalleryBtn')?.addEventListener('click', () => {
        showScreen([mainScreen, generationScreen, viewScreen], galleryScreen);
    });
    
    document.getElementById('backFromViewBtn')?.addEventListener('click', () => {
        showScreen([mainScreen, generationScreen, galleryScreen], viewScreen);
    });
    
    document.getElementById('searchModes')?.addEventListener('input', filterModes);
}

function filterModes(e) {
    const search = e.target.value.toLowerCase();
    document.querySelectorAll('.mode-card').forEach(card => {
        const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
        const desc = card.querySelector('.mode-card-description')?.textContent.toLowerCase() || '';
        card.style.display = (title.includes(search) || desc.includes(search)) ? 'flex' : 'none';
    });
}

export { showScreen };