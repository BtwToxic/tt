import json
import time
import os

DATA_FILE = "data.json"

LAST_ALERT = None
OTP_CODE = None
OTP_TIME = None
OTP_VALID_SECONDS = 600


# =========================
# INIT JSON
# =========================
def _init():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(
                {
                    "username": "dev",
                    "password": "123"
                },
                f
            )

_init()


def _read():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _write(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# USER / PASS
# =========================
def get_username():
    return _read()["username"]


def get_password():
    return _read()["password"]


def set_password(p):
    data = _read()
    data["password"] = p
    _write(data)


# =========================
# ALERTS
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
# OTP
# =========================
def set_otp(code):
    global OTP_CODE, OTP_TIME
    OTP_CODE = code
    OTP_TIME = time.time()


def verify_otp(code):
    global OTP_CODE, OTP_TIME

    if not OTP_CODE:
        return False, "❌ No OTP requested"

    if time.time() - OTP_TIME > OTP_VALID_SECONDS:
        OTP_CODE = None
        return False, "⏰ OTP expired"

    if code != OTP_CODE:
        return False, "❌ Invalid OTP"

    OTP_CODE = None
    return True, "✅ OTP verified"


def get_otp_expiry():
    if not OTP_TIME:
        return 0
    return max(0, OTP_VALID_SECONDS - int(time.time() - OTP_TIME))
