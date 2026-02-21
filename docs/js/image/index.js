// docs/js/image/index.js
import { MODES } from './modes/data.js';

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
        card.innerHTML = `
            <div style="background: ${mode.bgColor}; padding: 20px; text-align: center; color: white;">
                <div style="font-size: 40px;">${mode.icon}</div>
                <div style="font-size: 18px; font-weight: bold;">${mode.name}</div>
                <div style="margin-top: 10px;">⭐ ${mode.price}</div>
            </div>
        `;
        grid.appendChild(card);
    });
}