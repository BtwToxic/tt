import random
import time
import requests
from flask import request

from config import ADMIN_USER, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from state import (
    get_password,
    set_password,
    set_alert,
    set_otp,
    verify_otp
)

# =========================
# EXISTING LOGIN
# =========================
def check_login(u, p):
    if u != ADMIN_USER:
        set_alert("❌ Invalid username")
        return False

    if p != get_password():
        set_alert("❌ Wrong password")
        return False

    set_alert("✅ Login successful")
    return True


# =========================
# 🔐 2FA FLAG (ADDED)
# =========================
def is_2fa_enabled(username):
    """
    Enable / disable 2FA per user.
    Currently only ADMIN_USER has 2FA.
    """
    return username == ADMIN_USER


# =========================
# OTP GENERATION (RESET)
# =========================
def generate_code():
    code = str(random.randint(100000, 999999))
    set_otp(code)

    ip = request.remote_addr or "unknown"
    ua = request.headers.get("User-Agent", "unknown")

    msg = f"""
🔐 PASSWORD RESET REQUEST

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
