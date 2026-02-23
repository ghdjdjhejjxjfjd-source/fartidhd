import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, Tuple, Optional, List

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from groq_client import ask_groq
from payments import get_balance, add_stars, spend_stars, get_packages

# ✅ Импортируем стабильность
try:
    from stability_client import generate_image, generate_image_from_image
    STABILITY_AVAILABLE = True
except ImportError:
    STABILITY_AVAILABLE = False
    print("⚠️ Stability AI not available - stability_client.py not found")
except Exception as e:
    STABILITY_AVAILABLE = False
    print(f"⚠️ Stability AI import error: {e}")

api = Flask(__name__)
CORS(api, origins=["https://fayrat11.github.io", "https://*.github.io"])

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()

# Группа для логов: сначала TARGET_GROUP_ID, потом LOG_GROUP_ID
GROUP_ID_RAW = (os.getenv("TARGET_GROUP_ID") or os.getenv("LOG_GROUP_ID") or "0").strip()
try:
    GROUP_ID = int(GROUP_ID_RAW)
except Exception:
    GROUP_ID = 0

# --- SQLite (простая база прав) ---
DB_PATH = os.getenv("ACCESS_DB_PATH") or "access.db"


def db_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def db_init():
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS access (
            user_id INTEGER PRIMARY KEY,
            is_free INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            updated_at TEXT,
            last_menu_chat_id INTEGER,
            last_menu_message_id INTEGER,
            use_mini_app INTEGER DEFAULT 1,
            persona TEXT DEFAULT 'friendly',
            lang TEXT DEFAULT 'ru'
        )
        """
    )
    # ✅ память чата
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,               -- "user" | "assistant"
            text TEXT NOT NULL,
            created_at TEXT
        )
        """
    )
    con.commit()
    con.close()


db_init()


def _ensure_columns():
    """На случай если таблица была создана раньше без колонок меню."""
    con = db_conn()
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE access ADD COLUMN last_menu_chat_id INTEGER")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN last_menu_message_id INTEGER")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN use_mini_app INTEGER DEFAULT 1")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN persona TEXT DEFAULT 'friendly'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE access ADD COLUMN lang TEXT DEFAULT 'ru'")
    except Exception:
        pass
    con.commit()
    con.close()


_ensure_columns()


# =========================
# ACCESS (как было)
# =========================
def set_free(user_id: int, value: bool) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO access (user_id, is_free, is_blocked, updated_at)
        VALUES (?, ?, COALESCE((SELECT is_blocked FROM access WHERE user_id=?), 0), ?)
        ON CONFLICT(user_id) DO UPDATE SET
            is_free=excluded.is_free,
            updated_at=excluded.updated_at
        """,
        (user_id, 1 if value else 0, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    con.commit()
    con.close()


def set_blocked(user_id: int, value: bool) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO access (user_id, is_free, is_blocked, updated_at)
        VALUES (?, COALESCE((SELECT is_free FROM access WHERE user_id=?), 0), ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            is_blocked=excluded.is_blocked,
            updated_at=excluded.updated_at
        """,
        (user_id, user_id, 1 if value else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    con.commit()
    con.close()


def get_access(user_id: int) -> Dict[str, Any]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT is_free, is_blocked, updated_at, last_menu_chat_id, last_menu_message_id, use_mini_app, persona, lang FROM access WHERE user_id=?",
        (user_id,),
    )
    row = cur.fetchone()
    con.close()
    if not row:
        return {
            "user_id": user_id,
            "is_free": False,
            "is_blocked": False,
            "updated_at": None,
            "last_menu_chat_id": None,
            "last_menu_message_id": None,
            "use_mini_app": True,
            "persona": "friendly",
            "lang": "ru",
        }
    return {
        "user_id": user_id,
        "is_free": bool(row[0]),
        "is_blocked": bool(row[1]),
        "updated_at": row[2],
        "last_menu_chat_id": row[3],
        "last_menu_message_id": row[4],
        "use_mini_app": bool(row[5]) if row[5] is not None else True,
        "persona": row[6] if row[6] else "friendly",
        "lang": row[7] if row[7] else "ru",
    }


def set_last_menu(user_id: int, chat_id: int, message_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO access (user_id, is_free, is_blocked, updated_at, last_menu_chat_id, last_menu_message_id)
        VALUES (?, COALESCE((SELECT is_free FROM access WHERE user_id=?), 0),
                COALESCE((SELECT is_blocked FROM access WHERE user_id=?), 0),
                ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            last_menu_chat_id=excluded.last_menu_chat_id,
            last_menu_message_id=excluded.last_menu_message_id,
            updated_at=excluded.updated_at
        """,
        (
            user_id,
            user_id,
            user_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            chat_id,
            message_id,
        ),
    )
    con.commit()
    con.close()


def clear_last_menu(user_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        UPDATE access
        SET last_menu_chat_id=NULL, last_menu_message_id=NULL, updated_at=?
        WHERE user_id=?
        """,
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
    )
    con.commit()
    con.close()


def get_last_menu(user_id: int) -> Tuple[Optional[int], Optional[int]]:
    a = get_access(user_id)
    return a.get("last_menu_chat_id"), a.get("last_menu_message_id")


# =========================
# ✅ НОВЫЕ ФУНКЦИИ ДЛЯ РЕЖИМА, ХАРАКТЕРА И ЯЗЫКА
# =========================

def get_use_mini_app(user_id: int) -> bool:
    """Получить режим работы (True - Mini App, False - встроенный)"""
    a = get_access(user_id)
    return a.get("use_mini_app", True)


def set_use_mini_app(user_id: int, value: bool) -> None:
    """Установить режим работы"""
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        UPDATE access
        SET use_mini_app = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (1 if value else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
    )
    if cur.rowcount == 0:
        # Если записи нет, создаем
        cur.execute(
            """
            INSERT INTO access (user_id, use_mini_app, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, 1 if value else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
    con.commit()
    con.close()


def get_user_persona(user_id: int) -> str:
    """Получить характер ИИ пользователя"""
    a = get_access(user_id)
    return a.get("persona", "friendly")


def set_user_persona(user_id: int, persona: str) -> None:
    """Установить характер ИИ"""
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        UPDATE access
        SET persona = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (persona, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
    )
    if cur.rowcount == 0:
        # Если записи нет, создаем
        cur.execute(
            """
            INSERT INTO access (user_id, persona, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, persona, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
    con.commit()
    con.close()


def get_user_lang(user_id: int) -> str:
    """Получить язык пользователя"""
    a = get_access(user_id)
    return a.get("lang", "ru")


def set_user_lang(user_id: int, lang: str) -> None:
    """Установить язык пользователя"""
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        UPDATE access
        SET lang = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (lang, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
    )
    if cur.rowcount == 0:
        cur.execute(
            """
            INSERT INTO access (user_id, lang, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, lang, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
    con.commit()
    con.close()


# =========================
# LOG (как было)
# =========================
def send_log_to_group(text: str) -> Tuple[bool, str]:
    if not BOT_TOKEN:
        return False, "BOT_TOKEN is empty"
    if not GROUP_ID:
        return False, "TARGET_GROUP_ID/LOG_GROUP_ID is empty or invalid"

    if len(text) > 3900:
        text = text[:3900] + "\n…(truncated)"

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": GROUP_ID, "text": text},
            timeout=12,
        )
        return r.ok, r.text
    except Exception as e:
        return False, f"requests error: {e}"


def extract_last_user_message(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if "Conversation:" in s or "\nUser:" in s or s.startswith("You are "):
        idx = s.rfind("User:")
        if idx != -1:
            s2 = s[idx + len("User:") :].strip()
            cut = s2.find("\nAssistant:")
            if cut != -1:
                s2 = s2[:cut].strip()
            return s2
    return s


# =========================
# ✅ MEMORY
# =========================
def mem_add(user_id: int, role: str, text: str) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO chat_memory (user_id, role, text, created_at) VALUES (?, ?, ?, ?)",
        (user_id, role, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    con.commit()
    con.close()


def mem_get(user_id: int, limit: int = 24) -> List[Dict[str, str]]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        SELECT role, text
        FROM chat_memory
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cur.fetchall()
    con.close()
    rows.reverse()  # в правильный порядок (старые -> новые)
    out = []
    for r in rows:
        out.append({"role": r[0], "text": r[1]})
    return out


def mem_clear(user_id: int) -> None:
    con = db_conn()
    cur = con.cursor()
    cur.execute("DELETE FROM chat_memory WHERE user_id=?", (user_id,))
    con.commit()
    con.close()
    print(f"🧹 Memory cleared for user {user_id}")


def build_memory_prompt(history: List[Dict[str, str]], user_text: str) -> str:
    lines = []
    lines.append("Conversation:")
    if history:
        for m in history:
            role = "User" if m.get("role") == "user" else "Assistant"
            lines.append(f"{role}: {m.get('text','')}")
    else:
        lines.append("(empty)")
    lines.append("")
    lines.append(f"User: {user_text}")
    lines.append("Assistant:")
    return "\n".join(lines)


# =========================
# ROUTES
# =========================
@api.get("/")
def root():
    return "ok"


@api.get("/health")
def health():
    return "ok"


@api.get("/api/test-log")
def test_log():
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ok, info = send_log_to_group(f"✅ TEST LOG\n🕒 {time_str}")
    return jsonify(
        {
            "ok": ok,
            "group_id": GROUP_ID,
            "has_bot_token": bool(BOT_TOKEN),
            "telegram_response": info,
        }
    ), (200 if ok else 500)


@api.get("/api/access/<int:user_id>")
def api_access(user_id: int):
    return jsonify(get_access(user_id))


# ✅ очистка памяти по кнопке "Очистить"
@api.post("/api/memory/clear")
def api_memory_clear():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    tg_user_id = data.get("tg_user_id") or 0
    try:
        tg_user_id_int = int(tg_user_id)
    except Exception:
        tg_user_id_int = 0

    if not tg_user_id_int:
        return jsonify({"error": "bad_user_id"}), 400

    # Очищаем память без проверок
    mem_clear(tg_user_id_int)
    return jsonify({"ok": True, "message": "Memory cleared"})


@api.post("/api/chat")
def api_chat():
    data: Dict[str, Any] = request.get_json(silent=True) or {}

    raw_text = (data.get("text") or "").strip()
    if not raw_text:
        return jsonify({"error": "empty"}), 400

    text = extract_last_user_message(raw_text)

    tg_user_id = data.get("tg_user_id") or data.get("telegram_user_id") or 0
    try:
        tg_user_id_int = int(tg_user_id)
    except Exception:
        tg_user_id_int = 0

    tg_username = data.get("tg_username") or data.get("username") or "—"
    tg_first_name = data.get("tg_first_name") or data.get("first_name") or "—"

    # --- ACCESS CHECK ---
    if tg_user_id_int:
        a = get_access(tg_user_id_int)
        if a["is_blocked"]:
            return jsonify({"error": "blocked"}), 403
        
        # ✅ Проверяем баланс звезд
        balance = get_balance(tg_user_id_int)
        
        # Стоимость одного запроса - 1 звезда
        COST_PER_MESSAGE = 1
        
        if balance < COST_PER_MESSAGE and not a["is_free"]:
            return jsonify({"error": "insufficient_stars"}), 402
            
        # Если пользователь не FREE - списываем звезды
        if not a["is_free"]:
            spend_stars(tg_user_id_int, COST_PER_MESSAGE)
            
    else:
        return jsonify({"error": "payment_required"}), 402

    lang = data.get("lang") or get_user_lang(tg_user_id_int) or "ru"
    style = data.get("style") or "steps"
    
    # ✅ Используем сохраненный характер пользователя
    persona = data.get("persona")
    if tg_user_id_int and not persona:
        persona = get_user_persona(tg_user_id_int)
    else:
        persona = persona or "friendly"

    # ✅ берём историю + строим промпт с памятью
    history = mem_get(tg_user_id_int, limit=24)
    prompt_with_memory = build_memory_prompt(history, text)

    # ✅ сохраняем user сообщение в память ДО ответа
    mem_add(tg_user_id_int, "user", text)

    try:
        reply = ask_groq(prompt_with_memory, lang=lang, style=style, persona=persona)
    except Exception as e:
        send_log_to_group(f"❌ Ошибка /api/chat: {e}")
        return jsonify({"error": str(e)}), 500

    # ✅ сохраняем ответ в память
    mem_add(tg_user_id_int, "assistant", reply)

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    send_log_to_group(
        f"🕒 {time_str}\n"
        f"👤 {tg_first_name} (@{tg_username})\n"
        f"🆔 {tg_user_id_int}\n"
        f"💬 {text}\n\n"
        f"🤖 {reply}"
    )

    return jsonify({"reply": reply})


# =========================
# ✅ STARS ENDPOINTS
# =========================

@api.get("/api/stars/balance/<int:user_id>")
def api_stars_balance(user_id: int):
    """Получить баланс звезд"""
    return jsonify({
        "user_id": user_id,
        "balance": get_balance(user_id),
    })


@api.get("/api/stars/packages")
def api_stars_packages():
    """Получить список пакетов"""
    return jsonify({
        "packages": get_packages(),
        "currency": "USD",
    })


@api.post("/api/stars/add_test")
def api_stars_add_test():
    """Тестовое добавление звезд (для админов)"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    amount = data.get("amount", 100)
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    add_stars(user_id, amount, "test")
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "added": amount,
        "new_balance": get_balance(user_id),
    })


# =========================
# ✅ SPEND STARS ENDPOINT
# =========================
@api.post("/api/stars/spend")
def api_stars_spend():
    """Списать звезды за покупку темы"""
    data = request.get_json() or {}
    tg_user_id = data.get("tg_user_id")
    amount = data.get("amount", 0)
    
    if not tg_user_id or not amount:
        return jsonify({"error": "missing data"}), 400
    
    try:
        tg_user_id_int = int(tg_user_id)
        amount_int = int(amount)
        
        success = spend_stars(tg_user_id_int, amount_int)
        
        if success:
            return jsonify({
                "success": True,
                "new_balance": get_balance(tg_user_id_int)
            })
        else:
            return jsonify({"error": "insufficient_funds"}), 402
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ✅ SEND PHOTO TO TELEGRAM
# =========================
@api.post("/api/send-photo")
def api_send_photo():
    """Отправить фото пользователю в Telegram"""
    try:
        user_id = request.form.get('user_id')
        image_file = request.files.get('image')
        filename = request.form.get('filename', 'image.jpg')
        
        if not user_id or not image_file:
            return jsonify({"error": "Missing data"}), 400
            
        # Читаем файл
        image_data = image_file.read()
        
        # Отправляем через Telegram Bot API
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            return jsonify({"error": "BOT_TOKEN not configured"}), 500
            
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        
        files = {
            'photo': (filename, image_data, 'image/jpeg')
        }
        data = {
            'chat_id': user_id,
            'caption': f'✨ Улучшенное изображение\nОтправлено из Mini App'
        }
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            error_data = response.json()
            return jsonify({
                "error": "Telegram API error", 
                "details": error_data
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ✅ IMAGE GENERATION ENDPOINT
# =========================
@api.post("/api/image")
def api_image():
    """Генерация изображения через Stability AI"""
    
    # Проверка доступности Stability AI
    if not STABILITY_AVAILABLE:
        return jsonify({"error": "image_generation_not_available"}), 503
    
    # Получаем данные из формы (поддерживает файлы)
    tg_user_id = request.form.get("tg_user_id") or 0
    prompt = (request.form.get("prompt") or "").strip()
    mode = (request.form.get("mode") or "txt2img").strip().lower()
    
    try:
        tg_user_id_int = int(tg_user_id)
    except Exception:
        tg_user_id_int = 0
    
    # --- ACCESS CHECK ---
    if tg_user_id_int:
        a = get_access(tg_user_id_int)
        if a["is_blocked"]:
            return jsonify({"error": "blocked"}), 403
        if not a["is_free"]:
            return jsonify({"error": "payment_required"}), 402
    else:
        return jsonify({"error": "payment_required"}), 402
    
    # Проверка промпта
    if not prompt and mode == "txt2img":
        return jsonify({"error": "empty_prompt"}), 400
    
    # Получаем файл если есть
    image_file = request.files.get("image")
    image_data = None
    if image_file:
        image_data = image_file.read()
    
    # Проверка режима
    if mode in ["img2img", "remove_bg", "inpaint"] and not image_data:
        return jsonify({"error": "image_required_for_this_mode"}), 400
    
    # Получаем дополнительные параметры
    negative_prompt = request.form.get("negative_prompt") or None
    try:
        steps = int(request.form.get("steps") or 30)
        cfg_scale = float(request.form.get("cfg_scale") or 7.0)
        width = int(request.form.get("width") or 1024)
        height = int(request.form.get("height") or 1024)
        strength = float(request.form.get("strength") or 0.7)
    except ValueError:
        steps, cfg_scale, width, height, strength = 30, 7.0, 1024, 1024, 0.7
    
    # Ограничения для безопасности
    steps = min(max(steps, 10), 50)
    cfg_scale = min(max(cfg_scale, 1.0), 20.0)
    width = min(max(width, 256), 2048)
    height = min(max(height, 256), 2048)
    strength = min(max(strength, 0.1), 0.9)
    
    try:
        # Генерация в зависимости от режима
        if mode == "txt2img":
            # Текст -> изображение
            image_base64 = generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                steps=steps,
                cfg_scale=cfg_scale,
                width=width,
                height=height,
            )
        
        elif mode == "img2img" and image_data:
            # Изображение -> изображение (смена стиля)
            image_base64 = generate_image_from_image(
                prompt=prompt,
                init_image=image_data,
                strength=strength,
                steps=steps,
                cfg_scale=cfg_scale,
            )
        
        elif mode == "remove_bg" and image_data:
            # Удаление фона (упрощенная версия)
            enhanced_prompt = f"{prompt}, professional product photo, clean white background, no background, isolated object"
            image_base64 = generate_image_from_image(
                prompt=enhanced_prompt,
                init_image=image_data,
                strength=0.6,
                steps=35,
                cfg_scale=8.0,
            )
        
        elif mode == "inpaint" and image_data:
            # Удаление объекта (упрощенная версия)
            enhanced_prompt = f"{prompt}, remove specified object, clean removal, seamless edit"
            image_base64 = generate_image_from_image(
                prompt=enhanced_prompt,
                init_image=image_data,
                strength=0.8,
                steps=40,
                cfg_scale=7.5,
            )
        
        elif mode == "upscale" and image_data:
            # Улучшение качества (упрощенная версия)
            enhanced_prompt = f"{prompt}, high resolution, 8k, detailed, sharp focus, professional photography"
            image_base64 = generate_image_from_image(
                prompt=enhanced_prompt,
                init_image=image_data,
                strength=0.5,
                steps=25,
                cfg_scale=6.0,
            )
        
        else:
            return jsonify({"error": "unsupported_mode"}), 400
        
        if not image_base64:
            return jsonify({"error": "generation_failed"}), 500
        
        # Логируем успешную генерацию
        tg_username = request.form.get("tg_username") or "—"
        tg_first_name = request.form.get("tg_first_name") or "—"
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        send_log_to_group(
            f"🖼 Изображение сгенерировано\n"
            f"🕒 {time_str}\n"
            f"👤 {tg_first_name} (@{tg_username})\n"
            f"🆔 {tg_user_id_int}\n"
            f"📝 Режим: {mode}\n"
            f"💬 Промпт: {prompt[:80]}..."
        )
        
        return jsonify({
            "success": True,
            "image_base64": image_base64,
            "prompt": prompt,
            "mode": mode,
            "width": width,
            "height": height,
            "steps": steps,
        })
        
    except Exception as e:
        # Логируем ошибку
        error_msg = str(e)
        send_log_to_group(f"❌ Ошибка генерации изображения\n🆔 {tg_user_id_int}\n📝 {prompt[:50]}...\n💥 {error_msg}")
        
        # Безопасный ответ с ошибкой
        if "API key" in error_msg:
            return jsonify({"error": "invalid_api_key"}), 500
        elif "credit" in error_msg.lower() or "balance" in error_msg.lower():
            return jsonify({"error": "insufficient_balance"}), 402
        elif "timeout" in error_msg.lower():
            return jsonify({"error": "generation_timeout"}), 504
        else:
            return jsonify({"error": "generation_failed", "detail": error_msg[:100]}), 500


# =========================
# ✅ НОВЫЕ ЭНДПОИНТЫ ДЛЯ РЕЖИМА, ХАРАКТЕРА И ЯЗЫКА
# =========================

@api.get("/api/user/mode/<int:user_id>")
def api_user_mode(user_id: int):
    """Получить режим работы пользователя"""
    return jsonify({
        "user_id": user_id,
        "use_mini_app": get_use_mini_app(user_id)
    })


@api.post("/api/user/mode")
def api_set_user_mode():
    """Установить режим работы"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    use_mini_app = data.get("use_mini_app")
    
    if not user_id or use_mini_app is None:
        return jsonify({"error": "user_id and use_mini_app required"}), 400
    
    set_use_mini_app(user_id, use_mini_app)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "use_mini_app": use_mini_app
    })


@api.get("/api/user/persona/<int:user_id>")
def api_user_persona(user_id: int):
    """Получить характер ИИ пользователя"""
    return jsonify({
        "user_id": user_id,
        "persona": get_user_persona(user_id)
    })


@api.post("/api/user/persona")
def api_set_user_persona():
    """Установить характер ИИ"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    persona = data.get("persona")
    
    if not user_id or not persona:
        return jsonify({"error": "user_id and persona required"}), 400
    
    valid_personas = ["friendly", "fun", "smart", "strict"]
    if persona not in valid_personas:
        return jsonify({"error": f"persona must be one of {valid_personas}"}), 400
    
    set_user_persona(user_id, persona)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "persona": persona
    })


@api.get("/api/user/lang/<int:user_id>")
def api_user_lang(user_id: int):
    """Получить язык пользователя"""
    return jsonify({
        "user_id": user_id,
        "lang": get_user_lang(user_id)
    })


@api.post("/api/user/lang")
def api_set_user_lang():
    """Установить язык пользователя"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    lang = data.get("lang")
    
    if not user_id or not lang:
        return jsonify({"error": "user_id and lang required"}), 400
    
    valid_langs = ["ru", "en", "kk", "tr", "uk", "fr"]
    if lang not in valid_langs:
        return jsonify({"error": f"lang must be one of {valid_langs}"}), 400
    
    set_user_lang(user_id, lang)
    return jsonify({
        "success": True,
        "user_id": user_id,
        "lang": lang
    })