from flask import (
    Flask, render_template, request,
    redirect, session, make_response
)
import os, time, hashlib, requests, uuid

from auth import check_login, is_2fa_enabled
from railway import list_projects
from state import get_alert, set_alert
import config 

app = Flask(__name__)
app.secret_key = "railway-final-auth"

# =====================
# CONFIG
# =====================
MAX_ATTEMPTS = 5
BLOCK_TIME = 60
REMEMBER_DAYS = 7

TG_BOT_TOKEN = TELEGRAM_BOT_TOKEN
TG_CHAT_ID = TELEGRAM_CHAT_ID

LOGIN_ATTEMPTS = {}      # ip -> (count, last_time)
USER_ATTEMPTS = {}       # username -> (count, last_time)
PENDING_2FA = {}         # token -> username
AUDIT_LOGS = []          # simple in-memory logs


# =====================
# HELPERS
# =====================
def send_telegram(msg, buttons=None):
    data = {
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    if buttons:
        data["reply_markup"] = {
            "inline_keyboard": buttons
        }
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            json=data,
            timeout=5
        )
    except:
        pass


def fingerprint(req):
    raw = f"{req.remote_addr}|{req.headers.get('User-Agent')}"
    return hashlib.sha256(raw.encode()).hexdigest()


def log_event(user, status):
    AUDIT_LOGS.append({
        "user": user,
        "ip": request.remote_addr,
        "device": fingerprint(request),
        "status": status,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })


def login_required(fn):
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/")
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


# =====================
# LOGIN
# =====================
@app.route("/", methods=["GET", "POST"])
def login():
    alert = get_alert()
    ip = request.remote_addr
    now = time.time()

    if ip in LOGIN_ATTEMPTS:
        c, t = LOGIN_ATTEMPTS[ip]
        if now - t > BLOCK_TIME:
            del LOGIN_ATTEMPTS[ip]

    if request.method == "POST":
        user = request.form.get("user")
        pwd = request.form.get("pass")
        remember = request.form.get("remember")

        if ip in LOGIN_ATTEMPTS and LOGIN_ATTEMPTS[ip][0] >= MAX_ATTEMPTS:
            set_alert("🚫 Too many attempts. Try later")
            return redirect("/")

        if not check_login(user, pwd):
            LOGIN_ATTEMPTS[ip] = (LOGIN_ATTEMPTS.get(ip, (0, now))[0] + 1, now)
            USER_ATTEMPTS[user] = (USER_ATTEMPTS.get(user, (0, now))[0] + 1, now)

            send_telegram(
                f"🚨 <b>Brute-force detected</b>\nUser: {user}\nIP: {ip}"
            )
            log_event(user, "FAILED")
            set_alert("❌ Wrong username or password")
            return redirect("/")

        # PASSWORD OK
        if is_2fa_enabled(user):
            token = str(uuid.uuid4())
            PENDING_2FA[token] = user

            send_telegram(
                f"🔐 <b>Login request</b>\nUser: {user}\nIP: {ip}",
                buttons=[
                    [
                        {"text": "✅ Approve", "callback_data": f"approve:{token}"},
                        {"text": "❌ Deny", "callback_data": f"deny:{token}"}
                    ]
                ]
            )

            set_alert("📲 Approval sent to Telegram")
            return redirect("/")

        # NO 2FA
        session["admin"] = True
        log_event(user, "SUCCESS")

        resp = make_response(redirect("/dashboard"))
        if remember:
            resp.set_cookie("remember", user, max_age=REMEMBER_DAYS * 86400)
        return resp

    return render_template("login.html", alert=alert)


# =====================
# TELEGRAM CALLBACK
# =====================
@app.route("/tg-callback", methods=["POST"])
def tg_callback():
    data = request.json
    query = data.get("callback_query")
    if not query:
        return "ok"

    action, token = query["data"].split(":")
    user = PENDING_2FA.get(token)

    if not user:
        return "ok"

    if action == "approve":
        session["admin"] = True
        log_event(user, "2FA APPROVED")
        del PENDING_2FA[token]
        send_telegram(f"✅ Login approved for {user}")

    if action == "deny":
        log_event(user, "2FA DENIED")
        del PENDING_2FA[token]
        send_telegram(f"❌ Login denied for {user}")

    return "ok"


# =====================
# DASHBOARD (PROTECTED)
# =====================
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "projects.html",
        projects=list_projects(),
        alert=get_alert()
    )


# =====================
# AUDIT LOGS
# =====================
@app.route("/audit")
@login_required
def audit():
    return render_template("audit.html", logs=AUDIT_LOGS)


# =====================
# LOGOUT
# =====================
@app.route("/logout")
def logout():
    session.clear()
    set_alert("👋 Logged out")
    return redirect("/")


# =====================
# START
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
