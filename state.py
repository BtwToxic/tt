import time

ADMIN_PASSWORD = None
LAST_ALERT = None

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
