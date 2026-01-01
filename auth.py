from state import get_username, get_password, set_alert, set_otp, verify_otp
import random
import time
import requests
from flask import request
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def check_login(u, p):
    u = (u or "").strip()
    p = (p or "").strip()

    if u != get_username():
        set_alert("❌ Invalid username")
        return False

    if p != get_password():
        set_alert("❌ Wrong password")
        return False

    set_alert("✅ Login successful")
    return True

def generate_code():
    code = str(random.randint(100000, 999999))
    set_otp(code)

    msg = f"""
🔐 PASSWORD RESET

OTP: {code}
Valid: 10 minutes
Time: {time.ctime()}
"""

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
                timeout=5
            )
        except Exception:
            pass

    set_alert("📩 OTP sent (10 min valid)")


def reset_password(code, new_pass):
    ok, msg = verify_otp(code)
    if not ok:
        set_alert(msg)
        return False

    set_password(new_pass)
    set_alert("🔐 Password reset successful")
    return True
