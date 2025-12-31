import json, random, requests

cfg = json.load(open("config.json"))

RESET_CODE = None

def check_login(u, p):
    return u == cfg["admin_user"] and p == cfg["admin_pass"]

def generate_code():
    global RESET_CODE
    RESET_CODE = str(random.randint(100000, 999999))
    send_telegram(RESET_CODE)

def verify_code(code):
    return code == RESET_CODE

def set_new_password(new_pass):
    cfg["admin_pass"] = new_pass
    json.dump(cfg, open("config.json", "w"), indent=2)

def send_telegram(code):
    url = f"https://api.telegram.org/bot{cfg['telegram_bot_token']}/sendMessage"
    requests.post(url, data={
        "chat_id": cfg["telegram_chat_id"],
        "text": f"🔐 Password reset code:\n\n{code}"
    })
