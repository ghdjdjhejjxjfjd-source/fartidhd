import os
import base64
import requests

PIXIAN_API_KEY = os.getenv("PIXIAN_API_KEY", "").strip()
PIXIAN_URL = "https://api.pixian.ai/api/v1/remove-background"

def remove_background_pixian(image_bytes: bytes) -> str:
    """
    Удаление фона через Pixian.ai
    Возвращает base64 PNG с прозрачным фоном
    """
    if not PIXIAN_API_KEY:
        raise RuntimeError("PIXIAN_API_KEY не задан")

    try:
        response = requests.post(
            PIXIAN_URL,
            auth=(PIXIAN_API_KEY, ""),  # API ключ как username, пароль пустой
            files={"image": ("image.jpg", image_bytes)},
            data={"format": "png"},
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(f"Ошибка Pixian: {response.status_code} — {response.text}")

        # Возвращаем base64
        image_base64 = base64.b64encode(response.content).decode("utf-8")
        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        raise RuntimeError(f"Pixian error: {e}")