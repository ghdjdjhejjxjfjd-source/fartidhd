// docs/js/image/index.js

import { MODES } from './modes/data.js';
import { initTxt2Img } from './modes/txt2img.js';
import { initImg2Img } from './modes/img2img.js';
import { initRemoveBg } from './modes/remove_bg.js';
import { initInpaint } from './modes/inpaint.js';
import { initUpscale } from './modes/upscale.js';
import { showScreen } from './shared/utils.js';

const mainScreen = document.getElementById('mainScreen');
const generationScreen = document.getElementById('generationScreen');

document.addEventListener('DOMContentLoaded', () => {
    console.log("✅ Image module loaded");
    loadModes();
});

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
        
        card.innerHTML = `
            <div style="background: ${mode.bgColor}; padding: 20px; text-align: center; color: white; border-radius: 12px;">
                <div style="font-size: 40px;">${mode.icon}</div>
                <div style="font-size: 18px; font-weight: bold;">${mode.name}</div>
                <div style="margin-top: 10px;">⭐ ${mode.price}</div>
            </div>
        `;
        
        card.addEventListener('click', () => selectMode(mode));
        grid.appendChild(card);
    });
    
    console.log(`✅ Loaded ${MODES.length} modes`);
}

function selectMode(mode) {
    // Обновляем заголовок
    document.getElementById('currentModeTitle').textContent = mode.name;
    document.getElementById('currentModePrice').textContent = `${mode.price}⭐`;
    
    const modeIcon = document.getElementById('currentModeIcon');
    if (modeIcon) {
        modeIcon.textContent = mode.icon;
    }
    
    // Очищаем и загружаем соответствующий режим
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
    
    // Показываем экран генерации
    showScreen([mainScreen], generationScreen);
}

// Экспортируем для использования в других модулях
export { showScreen };