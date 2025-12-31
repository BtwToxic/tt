import os
from state import set_password

ADMIN_USER = os.environ.get("ADMIN_USER", "dev")
DEFAULT_PASS = os.environ.get("ADMIN_PASS", "dev123")

# set initial password at boot
set_password(DEFAULT_PASS)

TELEGRAM_BOT_TOKEN = "8366650744:AAHs8DcbhQasZkfdOX35YJDGd6gxcCyWeYQ"
TELEGRAM_CHAT_ID = "-1002843633996"

RAILWAY_API_KEY = "ca071a67-2431-476f-84f1-500f04ce09d9"
RAILWAY_PROJECT_ID = "2848c0cd-1b72-4666-9c8d-a8e6ee06efac"
