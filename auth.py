import random
import time
import requests
from flask import request

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from state import (
    get_username,
    get_password,
    set_password,
    set_alert,
    set_otp,
    verify_otp
)

# =========================
# LOGIN CHECK
# =========================
def check_login(u, p):
    real_user = get_username()
    real_pass = get_password()

    # 🔍 DEBUG (Railway logs me dikhega)
    print("LOGIN DEBUG:", u, p, real_user, real_pass)

    if u != real_user:
        set_alert("❌ Invalid username")
        return False

    if p != real_pass:
        set_alert("❌ Wrong password")
        return False

    set_alert("✅ Login successful")
    return True


# =========================
# OTP GENERATION (RESET)
# =========================
def generate_code():
    code = str(random.randint(100000, 999999))
    set_otp(code)

    ip = request.remote_addr or "unknown"
    ua = request.headers.get("User-Agent", "unknown")

    msg = f"""
🔐 TOXIC PASSWORD RESET REQUEST

OTP: {code}
Valid: 10 minutes

IP: {ip}
Device:
{ua}

Time: {time.ctime()}
"""

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": msg
                },
                timeout=5
            )
        except Exception as e:
            print("Telegram error:", e)

    set_alert("📩 OTP sent to Telegram (valid 10 min)")


# =========================
# PASSWORD RESET
# =========================
def reset_password(code, new_pass):
    ok, msg = verify_otp(code)
    if not ok:
        set_alert(msg)
        return False

    set_password(new_pass)
    set_alert("🔐 Password reset successful")
    return True
