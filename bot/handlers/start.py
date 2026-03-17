# bot/handlers/start.py
from telegram import Update
from telegram.ext import ContextTypes
import re
from datetime import datetime

from bot.utils import send_fresh_menu
from bot.config import build_start_log, send_log_http
from api import get_access
from payments import add_stars

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    send_log_http(build_start_log(update))
    
    user = update.effective_user
    uid = user.id if user else 0
    if not uid:
        return
    
    # ===== ПРОВЕРКА НА РЕФЕРАЛЬНУЮ ССЫЛКУ =====
    text = update.message.text or ""
    referrer_id = None
    
    # Ищем ref_123456789 в тексте
    match = re.search(r'ref_(\d+)', text)
    if match:
        referrer_id = int(match.group(1))
        print(f"🔗 Реферальная ссылка: пригласил {referrer_id} -> {uid}")
        
        # Проверяем что не сам себя приглашает
        if referrer_id != uid:
            # Проверяем существует ли пользователь в БД
            from api.db import db_connection
            
            with db_connection() as conn:
                cur = conn.cursor()
                
                # Проверяем, новый ли это пользователь
                cur.execute("SELECT user_id FROM access WHERE user_id = ?", (uid,))
                is_new_user = cur.fetchone() is None
                
                if is_new_user:
                    # Проверяем, не был ли этот пользователь уже приглашен
                    cur.execute(
                        "SELECT id FROM referrals WHERE referral_id = ?",
                        (uid,)
                    )
                    already_referred = cur.fetchone()
                    
                    if not already_referred:
                        # Начисляем бонус пригласившему (10 звезд)
                        add_stars(referrer_id, 10, "referral")
                        
                        # Сохраняем информацию о реферале
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur.execute(
                            """
                            INSERT INTO referrals (referrer_id, referral_id, created_at, bonus_given)
                            VALUES (?, ?, ?, 10)
                            """,
                            (referrer_id, uid, now)
                        )
                        
                        print(f"✅ Бонус начислен: {referrer_id} получил 10⭐ за реферала {uid}")
                        
                        # Уведомляем пригласившего
                        try:
                            await context.bot.send_message(
                                chat_id=referrer_id,
                                text=f"🎉 По вашей ссылке зарегистрировался новый пользователь!\n"
                                     f"Вам начислено 10 ⭐"
                            )
                        except:
                            pass
                        
                        # Уведомляем нового пользователя
                        await update.message.reply_text(
                            "🎁 Вы пришли по реферальной ссылке!\n"
                            "Ваш друг получил 10 ⭐ бонуса."
                        )
    
    print(f"🚀 /start от пользователя {uid}")
    
    # Всегда отправляем свежее меню (старое удалится автоматически)
    await send_fresh_menu(context.bot, uid)