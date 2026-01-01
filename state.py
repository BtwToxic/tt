import json
import time
import os

DATA_FILE = "data.json"

LAST_ALERT = None

OTP_CODE = None
OTP_TIME = None
OTP_VALID_SECONDS = 600  # 10 minutes


# =========================
# INIT DATA FILE
# =========================
def _init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(
                {
                    "username": "dev",
                    "password": "dev123"
                },
                f
            )


_init_data()


# =========================
# USER / PASSWORD
# =========================
def _read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_username():
    return _read_data()["username"]


def set_username(u):
    data = _read_data()
    data["username"] = u
    _write_data(data)


def get_password():
    return _read_data()["password"]


def set_password(p):
    data = _read_data()
    data["password"] = p
    _write_data(data)


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

    remaining = OTP_VALID_SECONDS - int(time.time() - OTP_TIME)
    return max(0, remaining)
