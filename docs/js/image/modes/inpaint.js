// docs/js/image/modes/inpaint.js

import { showToast } from '../shared/utils.js';

export function initInpaint(container) {
    container.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3>Удалить объект</h3>
            <input type="file" id="fileInput" accept="image/*" style="margin: 10px 0;">
            <textarea id="promptInput" placeholder="Опишите что нужно удалить..." 
                style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 10px;"></textarea>
            <button id="generateBtn" style="padding: 10px 20px; background: #b98cff; color: white; border: none; border-radius: 10px;">
                Удалить объект
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
            showToast('Опишите что удалить', 'error');
            return;
        }
        showToast('Удаление объекта...', 'info');
    });
}