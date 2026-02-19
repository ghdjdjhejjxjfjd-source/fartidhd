// docs/js/image-gallery.js

const GALLERY_STORAGE_KEY = 'image_gallery_v1';

export function getGallery() {
    try {
        const saved = localStorage.getItem(GALLERY_STORAGE_KEY);
        return saved ? JSON.parse(saved) : [];
    } catch (e) {
        return [];
    }
}

export function addToGallery(imageData) {
    try {
        const gallery = getGallery();
        gallery.unshift(imageData);
        if (gallery.length > 100) gallery.pop();
        localStorage.setItem(GALLERY_STORAGE_KEY, JSON.stringify(gallery));
        return true;
    } catch (e) {
        return false;
    }
}

export function removeFromGallery(imageId) {
    try {
        let gallery = getGallery();
        gallery = gallery.filter(img => img.id !== imageId);
        localStorage.setItem(GALLERY_STORAGE_KEY, JSON.stringify(gallery));
        return true;
    } catch (e) {
        return false;
    }
}

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