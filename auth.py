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


def check_login(u, p):
    real_user = get_username()
    real_pass = get_password()

    print("LOGIN DEBUG:", real_user, real_pass)  # 👈 log me dikhega

    if u != real_user:
        set_alert("❌ Invalid username")
        return False

    if p != real_pass:
        set_alert("❌ Wrong password")
        return False

    set_alert("✅ Login successful")
    return True


def generate_code():
    code = str(random.randint(100000, 999999))
    set_otp(code)

    msg = f"OTP: {code}\nValid: 10 minutes"

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
            timeout=5
        )

    set_alert("📩 OTP sent to Telegram")


def reset_password(code, new_pass):
    ok, msg = verify_otp(code)
    if not ok:
        set_alert(msg)
        return False

    set_password(new_pass)
    set_alert("🔐 Password reset successful")
    return True
