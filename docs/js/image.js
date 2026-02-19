// docs/js/image.js

export const MODES = [
    {
        id: 'txt2img',
        name: 'Из текста',
        description: 'Создать изображение по описанию',
        price: 4,
        emoji: '✏️',
        needsFile: false,
        popular: true
    },
    {
        id: 'img2img',
        name: 'Смена стиля',
        description: 'Изменить стиль фото',
        price: 4,
        emoji: '🎨',
        needsFile: true,
        popular: true
    },
    {
        id: 'remove_bg',
        name: 'Удалить фон',
        description: 'Вырезать объект, убрать фон',
        price: 6,
        emoji: '✂️',
        needsFile: true,
        popular: false
    },
    {
        id: 'inpaint',
        name: 'Удалить объект',
        description: 'Стереть ненужные детали',
        price: 6,
        emoji: '🧹',
        needsFile: true,
        popular: false
    },
    {
        id: 'upscale',
        name: 'Улучшить качество',
        description: 'Повысить разрешение до 4K',
        price: 3,
        emoji: '🔍',
        needsFile: true,
        popular: false
    }
];

let currentMode = null;
let selectedFile = null;

export function getModes() {
    return MODES;
}

export function setMode(id) {
    currentMode = MODES.find(m => m.id === id) || null;
    return currentMode;
}

export function getMode() {
    return currentMode;
}

export function setFile(file) {
    selectedFile = file;
}

export function getFile() {
    return selectedFile;
}

export function resetState() {
    currentMode = null;
    selectedFile = null;
}