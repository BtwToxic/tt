import os
import time
from flask import Flask, render_template, request, redirect, session

from auth import check_login, generate_code, reset_password
from railway import list_projects
from state import get_alert, get_otp_expiry

app = Flask(__name__)
app.secret_key = "final-auth"

MAX_LOGIN_ATTEMPTS = 3
BLOCK_TIME = 60


def is_blocked():
    until = session.get("blocked_until")
    if not until:
        return False, 0
    left = int(until - time.time())
    if left <= 0:
        session.clear()
        return False, 0
    return True, left


@app.before_request
def protect():
    if request.path == "/projects" and not session.get("admin"):
        return redirect("/")


@app.route("/", methods=["GET", "POST"])
def login():
    blocked, sec = is_blocked()
    if blocked:
        return render_template("login.html", alert=f"🚫 Blocked {sec}s")

    if request.method == "POST":
        u = (request.form.get("user") or "").strip()
        p = (request.form.get("pass") or "").strip()

        ok = check_login(u, p)
        alert = get_alert()

        if ok:
            session["admin"] = True
            session.pop("attempts", None)
            return redirect("/projects")

        session["attempts"] = session.get("attempts", 0) + 1
        if session["attempts"] >= MAX_LOGIN_ATTEMPTS:
            session["blocked_until"] = time.time() + BLOCK_TIME
            alert = f"🚫 Blocked {BLOCK_TIME}s"

        return render_template("login.html", alert=alert)

    return render_template("login.html", alert=get_alert())


@app.route("/projects")
def projects():
    return render_template(
        "projects.html",
        projects=list_projects(),
        alert=get_alert()
    )


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        generate_code()
        return redirect("/reset")
    return render_template("forgot.html", alert=get_alert())


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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
