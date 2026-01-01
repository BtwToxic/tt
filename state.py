import json
import os
import time

# 🔥 Railway-safe writable path
DATA_FILE = "/tmp/data.json"

# ✅ DEFAULT LOGIN (FIRST TIME)
DEFAULT_DATA = {
    "username": "dev",
    "password": "123"
}

LAST_ALERT = None

OTP_CODE = None
OTP_TIME = None
OTP_VALID_SECONDS = 600  # 10 min


# =========================
# INTERNAL HELPERS
# =========================
def _load():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(DEFAULT_DATA, f)

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


# =========================
# AUTH DATA
# =========================
def get_username():
    return _load()["username"]


def get_password():
    return _load()["password"]


def set_password(new_pass):
    data = _load()
    data["password"] = new_pass
    _save(data)


# =========================
# ALERT SYSTEM
# =========================
def set_alert(msg):
    global LAST_ALERT
    LAST_ALERT = msg


def get_alert():
    global LAST_ALERT
    msg = LAST_ALERT
    LAST_ALERT = None
    return msg


# =========================
# OTP SYSTEM
# =========================
def set_otp(code):
    global OTP_CODE, OTP_TIME
    OTP_CODE = code
    OTP_TIME = time.time()


def verify_otp(code):
    global OTP_CODE, OTP_TIME

    if not OTP_CODE or not OTP_TIME:
        return False, "❌ No OTP requested"

    if time.time() - OTP_TIME > OTP_VALID_SECONDS:
        OTP_CODE = None
        OTP_TIME = None
        return False, "⏰ OTP expired (10 min)"

    if code != OTP_CODE:
        return False, "❌ Invalid OTP"

    OTP_CODE = None
    OTP_TIME = None
    return True, "✅ OTP verified"


def get_otp_expiry():
    if not OTP_TIME:
        return 0
    return max(0, OTP_VALID_SECONDS - int(time.time() - OTP_TIME))
