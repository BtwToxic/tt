from flask import Flask, render_template, request, redirect, session
from auth import check_login, generate_code, verify_code, set_new_password
from railway import list_services

app = Flask(__name__)
app.secret_key = "simple-secret"

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if check_login(request.form["user"], request.form["pass"]):
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/")
    services = list_services()
    return render_template("dashboard.html", services=services)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/forgot", methods=["GET","POST"])
def forgot():
    if request.method == "POST":
        generate_code()
        return redirect("/reset")
    return render_template("forgot.html")

@app.route("/reset", methods=["GET","POST"])
def reset():
    if request.method == "POST":
        if verify_code(request.form["code"]):
            set_new_password(request.form["newpass"])
            return redirect("/")
    return render_template("reset.html")

app.run(host="0.0.0.0", port=5000)
