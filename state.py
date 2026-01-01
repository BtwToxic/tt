import json
import time
import os

DATA_FILE = "data.json"
LAST_ALERT = ""

OTP_CODE = None
OTP_TIME = None
OTP_VALID_SECONDS = 600


def _load():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def get_username():
    return _load()["username"]


def get_password():
    return _load()["password"]


def set_password(p):
    data = _load()
    data["password"] = p
    _save(data)


def set_alert(msg):
    global LAST_ALERT
    LAST_ALERT = msg or ""


def get_alert():
    global LAST_ALERT
    msg = LAST_ALERT
    LAST_ALERT = ""
    return msg


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
