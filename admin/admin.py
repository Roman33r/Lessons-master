from flask import Blueprint, render_template, request, redirect, url_for, flash, session

admin = Blueprint("admin", __name__, template_folder='templates', static_folder='static')
menu = [{'url': ".index", "title": "Панель"}, {'url': ".logout", "title": "Выйти"}]
@admin.route("/")
def index():
    if not isLogged():
        return redirect(url_for(".login"))

    return render_template("admin/index.html", menu=menu, title = "Главная")

@admin.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form['username'] == 'admin' and request.form['password'] == '12345':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверный логин или пароль")
    return render_template("admin/login.html", title="Войти")

def login_admin():
    session['admin_logged'] = 1

def logout_admin():
    session.pop("admin_logged", None)

def isLogged():
    return True if session.get("admin_logged") else False

@admin.route("/logout")
def logout():
    if not isLogged():
        return redirect(url_for(".login"))
    logout_admin()

    return redirect(url_for(".login"))