import random
import requests
import platform
import time
from flask import request

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ADMIN_USER
from state import get_password, set_password, set_alert

RESET_CODE = None

def check_login(u, p):
    if u == ADMIN_USER and p == get_password():
        set_alert("✅ Login successful")
        return True
    return False

def generate_code():
    global RESET_CODE
    RESET_CODE = str(random.randint(100000, 999999))

    ip = request.remote_addr or "unknown"
    device = request.headers.get("User-Agent", "unknown")

    msg = f"""
🔐 PASSWORD RESET REQUEST

Code: {RESET_CODE}

IP: {ip}
Device:
{device}

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

def verify_code(code):
    return code == RESET_CODE

def set_new_password(new_pass):
    set_password(new_pass)
    set_alert("🔐 Password reset successful")
