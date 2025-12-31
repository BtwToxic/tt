from flask import Flask, render_template, request, redirect, session
import os

from auth import check_login, generate_code, reset_password
from railway import list_projects
from state import get_alert, set_alert

app = Flask(__name__)
app.secret_key = "railway-final-auth"

@app.route("/", methods=["GET", "POST"])
def login():
    alert = get_alert()

    if request.method == "POST":
        if check_login(
            request.form.get("user"),
            request.form.get("pass")
        ):
            session["admin"] = True
            set_alert("✅ Login successful")
            return redirect("/projects")
        else:
            # 🔥 YE LINE MISSING THI
            set_alert("❌ Wrong username or password")
            return redirect("/")

    return render_template("login.html", alert=alert)

@app.route("/projects")
def projects():
    if not session.get("admin"):
        return redirect("/")
    alert = get_alert()
    projects = list_projects()
    return render_template("projects.html", projects=projects, alert=alert)

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        generate_code()
        set_alert("📩 OTP sent successfully")
        return redirect("/reset")
    return render_template("forgot.html", alert=get_alert())

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        if reset_password(
            request.form.get("code"),
            request.form.get("newpass")
        ):
            set_alert("🔐 Password reset successful")
            return redirect("/")
        else:
            set_alert("❌ Invalid or expired code")
            return redirect("/reset")

    return render_template("reset.html", alert=get_alert())

@app.route("/logout")
def logout():
    session.clear()
    set_alert("👋 Logged out successfully")
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
