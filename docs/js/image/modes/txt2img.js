// docs/js/image/modes/txt2img.js

import { showToast } from '../shared/utils.js';

export function initTxt2Img(container) {
    container.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3>Генерация из текста</h3>
            <textarea id="promptInput" placeholder="Опишите что хотите увидеть..." 
                style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 10px;"></textarea>
            <button id="generateBtn" style="padding: 10px 20px; background: #3aa0ff; color: white; border: none; border-radius: 10px;">
                Сгенерировать
            </button>
        </div>
    `;
    
    document.getElementById('generateBtn').addEventListener('click', () => {
        const prompt = document.getElementById('promptInput').value;
        if (!prompt) {
            showToast('Введите описание', 'error');
            return;
        }
        showToast('Генерация...', 'info');
    });
}