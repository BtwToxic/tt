from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from dotenv import load_dotenv
import os

from railway import list_services, start_service, stop_service, redeploy

load_dotenv()

app = Flask(__name__)
app.secret_key = "railway-admin-panel"

login = LoginManager(app)
login.login_view = "login"

ADMIN_USER = "dev
ADMIN_PASS = "dev@123"
PROJECT_ID = os.getenv("ID")

class Admin(UserMixin):
    id = 1

@login.user_loader
def load_user(uid):
    return Admin()

@app.route("/admin", methods=["GET","POST"])
def login_page():
    if request.method == "POST":
        if (
            request.form["username"] == ADMIN_USER and
            request.form["password"] == ADMIN_PASS
        ):
            login_user(Admin())
            return redirect("/admin/dashboard")
    return render_template("login.html")

@app.route("/admin/dashboard")
@login_required
def dashboard():
    data = list_services(PROJECT_ID)
    services = data["data"]["project"]["services"]["edges"]
    return render_template("dashboard.html", services=services)

@app.route("/admin/action", methods=["POST"])
@login_required
def action():
    sid = request.form["service_id"]
    act = request.form["action"]

    if act == "start":
        start_service(sid)
    elif act == "stop":
        stop_service(sid)
    elif act == "redeploy":
        redeploy(sid)

    return redirect("/admin/dashboard")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/admin")
