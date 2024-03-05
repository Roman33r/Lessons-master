import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, session, redirect, url_for
from usefull.FDataBase import FDataBase
from usefull.UserLogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user


app = Flask(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'test.db')))
app.config["SECRET_KEY"] = "hoirjghojropgjehueEFGEOKOPje"

dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id,dbase)

def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource("sql_db.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin =  UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('index'))
        flash("Неверные данные - логин или пароль")
    return render_template("login.html",menu=dbase.getMenu(), title = "Авторизация")



@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        # session.pop('_flashes',None)
        if len(request.form['name']) > 4 \
                and len(request.form['email'])>4 \
                and len(request.form['psw'])>4 \
                and request.form['psw'] == request.form['psw2']:

            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'],request.form['email'],hash)
            if res:
                flash("Вы успешно зарегистрированы","success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД","error")
        else:
            flash("Неверно заполнены поля","error")

    return render_template("register.html",menu=dbase.getMenu(), title = "Регистрация")

# Routes
@app.route("/")
def index():
    return render_template("index.html", menu=dbase.getMenu(), posts=dbase.getPostAnonce())


@app.route("/add_post", methods=["GET", "POST"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash("Ошибка добавления", category="error")
            else:
                flash("Успешно добавлено", category="success")
        else:
            flash("Ошибка добавления , проверьте ваши данные", category="error")

    return render_template("add_post.html", menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template("post.html", menu=dbase.getMenu(), title=title, post=post)


def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db


@app.errorhandler(404)
def pageNotFound(error):
    return render_template("page404.html", title="Страница не найдена")


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()


if __name__ == "__main__":
    app.run(debug=True)
