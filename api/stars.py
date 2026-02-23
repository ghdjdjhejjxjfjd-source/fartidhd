from flask import jsonify, request
from payments import get_balance, add_stars, spend_stars, get_packages

from .config import api

# =========================
# STARS ENDPOINTS
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