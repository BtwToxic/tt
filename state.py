# state.py
import time

ADMIN_PASSWORD = None
LAST_ALERT = None

OTP_CODE = None
OTP_TIME = None
OTP_VALID_SECONDS = 600  # 10 minutes


def set_password(p):
    global ADMIN_PASSWORD
    ADMIN_PASSWORD = p


def get_password():
    return ADMIN_PASSWORD


def set_alert(msg):
    global LAST_ALERT
    LAST_ALERT = msg


def get_alert():
    global LAST_ALERT
    msg = LAST_ALERT
    LAST_ALERT = None
    return msg


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


# =========================
# ✅ OTP EXPIRY (ADDED ONLY)
# =========================
def get_otp_expiry():
    if not OTP_TIME:
        return 0

    remaining = OTP_VALID_SECONDS - int(time.time() - OTP_TIME)
    return max(0, remaining)
