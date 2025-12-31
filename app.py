from flask import Flask, render_template, request, redirect, session
import os
import time

from auth import check_login, generate_code, reset_password
from railway import list_projects
from state import get_alert, set_alert

app = Flask(__name__)
app.secret_key = "railway-final-auth"

# ==========================
# RATE LIMIT CONFIG
# ==========================
MAX_ATTEMPTS = 3
BLOCK_TIME = 60  # seconds

LOGIN_STATE = {}  
# ip -> {
#   "attempts": int,
#   "blocked_until": timestamp
# }


# ==========================
# LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():
    ip = request.remote_addr or "unknown"
    now = time.time()
    alert = get_alert()

    state = LOGIN_STATE.get(ip, {
        "attempts": 0,
        "blocked_until": 0
    })

    # 🔓 unblock after time
    if state["blocked_until"] and now > state["blocked_until"]:
        state = {"attempts": 0, "blocked_until": 0}
        LOGIN_STATE[ip] = state

    # 🚫 still blocked
    if state["blocked_until"] > now:
        remaining = int(state["blocked_until"] - now)
        set_alert(f"🚫 You are blocked for {remaining}s")
        return render_template("login.html", alert=get_alert())

    if request.method == "POST":
        ok = check_login(
            request.form.get("user"),
            request.form.get("pass")
        )

        if ok:
            session["admin"] = True
            LOGIN_STATE[ip] = {"attempts": 0, "blocked_until": 0}
            return redirect("/projects")

        # ❌ wrong login
        state["attempts"] += 1
        attempts_left = MAX_ATTEMPTS - state["attempts"]

        if attempts_left <= 0:
            state["blocked_until"] = now + BLOCK_TIME
            set_alert("🚫 Too many attempts. Blocked for 1 minute")
        else:
            set_alert(f"❌ Wrong credentials | Attempts left: {attempts_left}")

        LOGIN_STATE[ip] = state
        return redirect("/")

    return render_template("login.html", alert=alert)


# ==========================
# PROJECTS (PROTECTED)
# ==========================
@app.route("/projects")
def projects():
    if not session.get("admin"):
        return redirect("/")
    return render_template(
        "projects.html",
        projects=list_projects(),
        alert=get_alert()
    )


# ==========================
# FORGOT PASSWORD
# ==========================
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        generate_code()
        return redirect("/reset")
    return render_template("forgot.html", alert=get_alert())


# ==========================
# RESET PASSWORD
# ==========================
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        reset_password(
            request.form.get("code"),
            request.form.get("newpass")
        )
        return redirect("/")
    return render_template("reset.html", alert=get_alert())


# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    set_alert("👋 Logged out successfully")
    return redirect("/")


# ==========================
# START
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
