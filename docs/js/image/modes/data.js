// docs/js/image/modes/data.js

export const MODES = [
    {
        id: 'txt2img',
        name: 'Генерация',
        description: 'Создать изображение по тексту',
        price: 4,
        image: 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22200%22%20height%3D%22200%22%20viewBox%3D%220%200%20200%20200%22%3E%3Crect%20width%3D%22200%22%20height%3D%22200%22%20fill%3D%22%233aa0ff%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2230%22%3E✏️%3C%2Ftext%3E%3C%2Fsvg%3E',
        bgColor: '#3aa0ff',
        icon: '✏️',
        needsFile: false,
        placeholder: 'Опишите что хотите увидеть...',
        popular: true
    },
    {
        id: 'img2img',
        name: 'Смена стиля',
        description: 'Изменить стиль фото',
        price: 4,
        image: 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22200%22%20height%3D%22200%22%20viewBox%3D%220%200%20200%20200%22%3E%3Crect%20width%3D%22200%22%20height%3D%22200%22%20fill%3D%22%230a84ff%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2230%22%3E🎨%3C%2Ftext%3E%3C%2Fsvg%3E',
        bgColor: '#0a84ff',
        icon: '🎨',
        needsFile: true,
        placeholder: 'Опишите желаемый стиль...',
        popular: true
    },
    {
        id: 'remove_bg',
        name: 'Удалить фон',
        description: 'Вырезать объект, убрать фон',
        price: 6,
        image: 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22200%22%20height%3D%22200%22%20viewBox%3D%220%200%20200%20200%22%3E%3Crect%20width%3D%22200%22%20height%3D%22200%22%20fill%3D%22%232fd6a3%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2230%22%3E✂️%3C%2Ftext%3E%3C%2Fsvg%3E',
        bgColor: '#2fd6a3',
        icon: '✂️',
        needsFile: true,
        placeholder: 'Дополнительные инструкции (опционально)...',
        popular: false
    },
    {
        id: 'inpaint',
        name: 'Удалить объект',
        description: 'Стереть ненужные детали',
        price: 6,
        image: 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22200%22%20height%3D%22200%22%20viewBox%3D%220%200%20200%20200%22%3E%3Crect%20width%3D%22200%22%20height%3D%22200%22%20fill%3D%22%23b98cff%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2230%22%3E🧹%3C%2Ftext%3E%3C%2Fsvg%3E',
        bgColor: '#b98cff',
        icon: '🧹',
        needsFile: true,
        placeholder: 'Опишите что нужно удалить...',
        popular: false
    },
    {
        id: 'upscale',
        name: 'Улучшить качество',
        description: 'Повысить разрешение до 4K',
        price: 3,
        image: 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22200%22%20height%3D%22200%22%20viewBox%3D%220%200%20200%20200%22%3E%3Crect%20width%3D%22200%22%20height%3D%22200%22%20fill%3D%22%237fb2ff%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2230%22%3E🔍%3C%2Ftext%3E%3C%2Fsvg%3E',
        bgColor: '#7fb2ff',
        icon: '🔍',
        needsFile: true,
        placeholder: 'Выберите изображение для улучшения...',
        popular: false
    }
];