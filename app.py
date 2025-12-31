from flask import Flask, render_template, request, redirect, session
import os

from auth import check_login, generate_code, verify_code, set_new_password
from railway import list_services
from state import get_alert, set_alert

app = Flask(__name__)
app.secret_key = "railway-stable-final"

@app.route("/", methods=["GET", "POST"])
def login():
    alert = get_alert()

    if request.method == "POST":
        if check_login(request.form["user"], request.form["pass"]):
            session["admin"] = True
            return redirect("/dashboard")
        else:
            alert = "❌ Invalid credentials"

    return render_template("login.html", alert=alert)

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/")
    alert = get_alert()
    services = list_services()
    return render_template("dashboard.html", services=services, alert=alert)

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        generate_code()
        set_alert("📩 Reset code sent to Telegram")
        return redirect("/reset")
    return render_template("forgot.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        if verify_code(request.form["code"]):
            set_new_password(request.form["newpass"])
            return redirect("/")
        else:
            set_alert("❌ Invalid reset code")
    return render_template("reset.html")

@app.route("/logout")
def logout():
    session.clear()
    set_alert("👋 Logged out successfully")
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
