// Простейший тест
console.log('🔥 ТЕСТ: скрипт загружен');

// Ждем загрузки страницы
window.addEventListener('load', function() {
    console.log('🔥 Страница загружена');
    
    // Ищем контейнер
    const grid = document.getElementById('modesGrid');
    console.log('🔥 modesGrid:', grid);
    
    if (grid) {
        // Создаем одну тестовую карточку
        const testCard = document.createElement('div');
        testCard.textContent = 'ТЕСТОВАЯ КАРТОЧКА';
        testCard.style.cssText = `
            background: red;
            color: white;
            padding: 20px;
            margin: 10px;
            border-radius: 10px;
            text-align: center;
            font-size: 20px;
        `;
        grid.appendChild(testCard);
        console.log('🔥 Карточка добавлена');
    }
});