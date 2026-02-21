// docs/js/image/modes/img2img.js

import { showToast } from '../shared/utils.js';

export function initImg2Img(container) {
    container.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3>Смена стиля</h3>
            <input type="file" id="fileInput" accept="image/*" style="margin: 10px 0;">
            <textarea id="promptInput" placeholder="Опишите желаемый стиль..." 
                style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 10px;"></textarea>
            <button id="generateBtn" style="padding: 10px 20px; background: #0a84ff; color: white; border: none; border-radius: 10px;">
                Изменить стиль
            </button>
        </div>
    `;
    
    document.getElementById('generateBtn').addEventListener('click', () => {
        const file = document.getElementById('fileInput').files[0];
        const prompt = document.getElementById('promptInput').value;
        
        if (!file) {
            showToast('Выберите изображение', 'error');
            return;
        }
        if (!prompt) {
            showToast('Опишите стиль', 'error');
            return;
        }
        showToast('Генерация...', 'info');
    });
}