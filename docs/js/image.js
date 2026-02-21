// docs/js/image.js

export const MODES = [
    {
        id: 'txt2img',
        name: 'Генерация',
        description: 'Создать изображение по тексту',
        price: 4,
        image: './assets/modes/txt2img.jpg',
        bgColor: '#3aa0ff',
        icon: '✏️',
        needsFile: false,
        placeholder: 'Опишите что хотите увидеть...'
    },
    {
        id: 'img2img',
        name: 'Смена стиля',
        description: 'Изменить стиль фото',
        price: 4,
        image: './assets/modes/img2img.jpg',
        bgColor: '#0a84ff',
        icon: '🎨',
        needsFile: true,
        placeholder: 'Опишите желаемый стиль...'
    },
    {
        id: 'remove_bg',
        name: 'Удалить фон',
        description: 'Вырезать объект, убрать фон',
        price: 6,
        image: './assets/modes/remove_bg.jpg',
        bgColor: '#2fd6a3',
        icon: '✂️',
        needsFile: true,
        placeholder: 'Дополнительные инструкции (опционально)...'
    },
    {
        id: 'inpaint',
        name: 'Удалить объект',
        description: 'Стереть ненужные детали',
        price: 6,
        image: './assets/modes/inpaint.jpg',
        bgColor: '#b98cff',
        icon: '🧹',
        needsFile: true,
        placeholder: 'Опишите что нужно удалить...'
    },
    {
        id: 'upscale',
        name: 'Улучшить качество',
        description: 'Повысить разрешение до 4K',
        price: 3,
        image: './assets/modes/upscale.jpg',
        bgColor: '#7fb2ff',
        icon: '🔍',
        needsFile: true,
        placeholder: 'Дополнительные настройки (опционально)...'
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

export function getModeById(id) {
    return MODES.find(m => m.id === id) || null;
}