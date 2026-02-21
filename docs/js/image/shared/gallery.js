// docs/js/image/shared/gallery.js

import { showToast } from './utils.js';

const GALLERY_STORAGE_KEY = 'image_gallery_v1';

// Получить все изображения из галереи
export function getGallery() {
    try {
        const saved = localStorage.getItem(GALLERY_STORAGE_KEY);
        return saved ? JSON.parse(saved) : [];
    } catch (e) {
        return [];
    }
}

// Добавить изображение в галерею
export function addToGallery(imageData) {
    try {
        const gallery = getGallery();
        gallery.unshift(imageData);
        if (gallery.length > 100) gallery.pop();
        localStorage.setItem(GALLERY_STORAGE_KEY, JSON.stringify(gallery));
        showToast('Сохранено в галерею', 'success');
        return true;
    } catch (e) {
        showToast('Ошибка сохранения', 'error');
        return false;
    }
}

// Удалить изображение из галереи
export function removeFromGallery(imageId) {
    try {
        let gallery = getGallery();
        gallery = gallery.filter(img => img.id !== imageId);
        localStorage.setItem(GALLERY_STORAGE_KEY, JSON.stringify(gallery));
        showToast('Удалено из галереи', 'success');
        return true;
    } catch (e) {
        showToast('Ошибка удаления', 'error');
        return false;
    }
}

// Переключить избранное
export function toggleFavorite(imageId) {
    try {
        const gallery = getGallery();
        const image = gallery.find(img => img.id === imageId);
        if (image) {
            image.favorite = !image.favorite;
            localStorage.setItem(GALLERY_STORAGE_KEY, JSON.stringify(gallery));
            return image.favorite;
        }
        return false;
    } catch (e) {
        return false;
    }
}

// Загрузить галерею в интерфейс
export function loadGallery(filter = 'all', search = '') {
    const gallery = getGallery();
    const grid = document.getElementById('galleryGrid');
    const emptyState = document.getElementById('emptyGallery');
    
    if (!grid) return;
    
    if (gallery.length === 0) {
        grid.innerHTML = '';
        if (emptyState) emptyState.classList.remove('hidden');
        return;
    }
    
    if (emptyState) emptyState.classList.add('hidden');
    
    let filtered = gallery;
    if (filter === 'favorites') {
        filtered = gallery.filter(img => img.favorite);
    }
    
    if (search) {
        filtered = filtered.filter(img => 
            img.prompt?.toLowerCase().includes(search.toLowerCase())
        );
    }
    
    filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    
    grid.innerHTML = filtered.map(img => `
        <div class="gallery-item" data-id="${img.id}">
            <img src="${img.dataUrl}" alt="${img.prompt || 'image'}">
            ${img.favorite ? '<div class="gallery-item-favorite">❤️</div>' : ''}
        </div>
    `).join('');
    
    document.querySelectorAll('.gallery-item').forEach(item => {
        item.addEventListener('click', () => showImageView(item.dataset.id));
    });
}

// Показать изображение в просмотре
function showImageView(imageId) {
    const image = getGallery().find(img => img.id === imageId);
    if (!image) return;
    
    document.getElementById('viewImage').src = image.dataUrl;
    document.getElementById('viewPrompt').textContent = image.prompt || '—';
    document.getElementById('viewDate').textContent = image.createdAt ? new Date(image.createdAt).toLocaleString() : '—';
    document.getElementById('viewCost').textContent = `${image.cost || 0}⭐`;
    
    document.getElementById('viewScreen').classList.remove('hidden');
}

// Инициализация галереи
export function initGallery() {
    const galleryBtn = document.getElementById('galleryBtn');
    const historyBtn = document.getElementById('historyBtn');
    const backFromGalleryBtn = document.getElementById('backFromGalleryBtn');
    const backFromViewBtn = document.getElementById('backFromViewBtn');
    const gallerySearch = document.getElementById('gallerySearch');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const generateFromEmptyBtn = document.getElementById('generateFromEmptyBtn');
    
    if (galleryBtn) {
        galleryBtn.addEventListener('click', () => {
            loadGallery();
            document.getElementById('galleryScreen').classList.remove('hidden');
            document.getElementById('mainScreen').classList.add('hidden');
        });
    }
    
    if (historyBtn) {
        historyBtn.addEventListener('click', () => {
            loadGallery();
            document.getElementById('galleryScreen').classList.remove('hidden');
            document.getElementById('mainScreen').classList.add('hidden');
        });
    }
    
    if (backFromGalleryBtn) {
        backFromGalleryBtn.addEventListener('click', () => {
            document.getElementById('galleryScreen').classList.add('hidden');
            document.getElementById('mainScreen').classList.remove('hidden');
        });
    }
    
    if (backFromViewBtn) {
        backFromViewBtn.addEventListener('click', () => {
            document.getElementById('viewScreen').classList.add('hidden');
            document.getElementById('galleryScreen').classList.remove('hidden');
        });
    }
    
    if (gallerySearch) {
        gallerySearch.addEventListener('input', (e) => {
            const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'all';
            loadGallery(activeTab, e.target.value);
        });
    }
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            tabBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            loadGallery(e.target.dataset.tab, gallerySearch?.value || '');
        });
    });
    
    if (generateFromEmptyBtn) {
        generateFromEmptyBtn.addEventListener('click', () => {
            document.getElementById('galleryScreen').classList.add('hidden');
            document.getElementById('mainScreen').classList.remove('hidden');
        });
    }
}