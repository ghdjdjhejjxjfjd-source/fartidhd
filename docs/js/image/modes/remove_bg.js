// docs/js/image/modes/remove_bg.js

import { showToast } from '../shared/utils.js';

export function initRemoveBg(container) {
    container.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3>Удалить фон</h3>
            <input type="file" id="fileInput" accept="image/*" style="margin: 10px 0;">
            <button id="generateBtn" style="padding: 10px 20px; background: #2fd6a3; color: white; border: none; border-radius: 10px;">
                Удалить фон
            </button>
        </div>
    `;
    
    document.getElementById('generateBtn').addEventListener('click', () => {
        const file = document.getElementById('fileInput').files[0];
        if (!file) {
            showToast('Выберите изображение', 'error');
            return;
        }
        showToast('Удаление фона...', 'info');
    });
}