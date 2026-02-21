export const MODES = [
    {
        id: 'txt2img',
        name: 'Генерация',
        description: 'Создать изображение по тексту',
        price: 4,
        image: 'https://placehold.co/600x400/3aa0ff/white?text=✏️',
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
        image: 'https://placehold.co/600x400/0a84ff/white?text=🎨',
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
        image: 'https://placehold.co/600x400/2fd6a3/white?text=✂️',
        bgColor: '#2fd6a3',
        icon: '✂️',
        needsFile: true,
        placeholder: 'Дополнительные инструкции...'
    },
    {
        id: 'inpaint',
        name: 'Удалить объект',
        description: 'Стереть ненужные детали',
        price: 6,
        image: 'https://placehold.co/600x400/b98cff/white?text=🧹',
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
        image: 'https://placehold.co/600x400/7fb2ff/white?text=🔍',
        bgColor: '#7fb2ff',
        icon: '🔍',
        needsFile: true,
        placeholder: 'Выберите изображение...'
    }
];