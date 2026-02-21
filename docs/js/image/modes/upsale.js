// docs/js/image/modes/upscale.js

import { showToast } from '../shared/utils.js';

export function initUpscale(container) {
    container.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3>Улучшить качество до 4K</h3>
            <input type="file" id="fileInput" accept="image/*" style="margin: 10px 0;">
            <button id="generateBtn" style="padding: 10px 20px; background: #7fb2ff; color: white; border: none; border-radius: 10px;">
                Улучшить
            </button>
        </div>
    `;
    
    document.getElementById('generateBtn').addEventListener('click', () => {
        const file = document.getElementById('fileInput').files[0];
        if (!file) {
            showToast('Выберите изображение', 'error');
            return;
        }
        showToast('Улучшение качества...', 'info');
    });
}