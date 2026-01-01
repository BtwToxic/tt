import os
import time
from flask import Flask, render_template, request, redirect, session

from auth import check_login, generate_code, reset_password
from railway import list_projects
from state import get_alert, set_alert, get_otp_expiry

app = Flask(__name__)
app.secret_key = "railway-final-auth"

# =========================
# CONFIG
# =========================
MAX_LOGIN_ATTEMPTS = 3
BLOCK_TIME = 60  # seconds


# =========================
# BLOCK HELPER
# =========================
def is_blocked():
    blocked_until = session.get("blocked_until")
    if not blocked_until:
        return False, 0

    remaining = int(blocked_until - time.time())
    if remaining <= 0:
        session.pop("blocked_until", None)
        session.pop("attempts", None)
        return False, 0

    return True, remaining


# =========================
# GLOBAL PROTECTION
# =========================
@app.before_request
def protect_routes():
    protected_routes = ["/projects"]

    if request.path in protected_routes:
        if not session.get("admin"):
            return redirect("/")


# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    # ---- BLOCK CHECK ----
    blocked, remaining = is_blocked()
    if blocked:
        set_alert(f"🚫 You are blocked for {remaining}s")
        return render_template("login.html", alert=get_alert())

    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("pass")

        ok = check_login(user, password)

        if ok:
            session["admin"] = True
            session.pop("attempts", None)
            session.pop("blocked_until", None)
            return redirect("/projects")

        # ---- FAILED LOGIN ----
        session["attempts"] = session.get("attempts", 0) + 1
        left = MAX_LOGIN_ATTEMPTS - session["attempts"]

        # ⚠️ IMPORTANT: existing alert ko overwrite NAHI karna
        existing_alert = get_alert()

        if left <= 0:
            session["blocked_until"] = time.time() + BLOCK_TIME
            set_alert(f"🚫 You are blocked for {BLOCK_TIME}s")
        else:
            if existing_alert:
                set_alert(f"{existing_alert} · {left} attempts left")
            else:
                set_alert(f"❌ Wrong credentials ({left} attempts left)")

    return render_template("login.html", alert=get_alert())


# =========================
# PROJECTS (PROTECTED)
# =========================
@app.route("/projects")
def projects():
    if not session.get("admin"):
        return redirect("/")

    try:
        projects = list_projects()
        if not projects:
            projects = []
            set_alert("⚠️ Failed to load projects")
    except Exception:
        projects = []
        set_alert("⚠️ Error loading projects")

    return render_template(
        "projects.html",
        projects=projects,
        alert=get_alert()
    )


# =========================
# FORGOT PASSWORD
# =========================
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        generate_code()
        return redirect("/reset")

    return render_template(
        "forgot.html",
        alert=get_alert()
    )


# =========================
# RESET PASSWORD (OTP)
# =========================
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        reset_password(
            request.form.get("code"),
            request.form.get("newpass")
        )
        return redirect("/")

    return render_template(
        "reset.html",
        alert=get_alert(),
        otp_expiry=get_otp_expiry()
    )


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    set_alert("👋 Logged out successfully")
    return redirect("/")


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
