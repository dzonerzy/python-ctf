from flask import render_template, request, redirect, jsonify
from flask import session
#from app import session
from flask_login import login_user, login_required, current_user, logout_user
from .models import User, Phone, Message
from . import Database, Login
import random
import re


def init_routes(app):
    @app.route("/")
    @login_required
    def index():
        if current_user.is_user:
            logout_user()
            return render_template("maintenance.html")
        else:
            return "The flag is: <REDACTED>"

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html", task="login")
        else:
            usr = request.form["usr"]
            pwd = request.form["pwd"]
            user = User.query.filter_by(username=usr).first()
            if user and user.check_password(pwd):
                login_user(user)
            else:
                return redirect("/login?error=invalid_user_password", 302)
            return redirect("/", 301)

    @app.route("/create")
    def create():
        return render_template("login.html", task="create")

    @app.route("/forgot")
    def forgot_step1():
        return render_template("login.html", task="forgot")

    @app.route("/send-code", methods=["POST"])
    def send_code():
        usr = session["reset_user"]
        user = User.query.filter_by(username=usr).first()
        if user:
            session["code"] = str(random.randint(100000, 999999))
            m = Message("+1555725991", user.phone, "Here's your OTP code: {}".format(session["code"]))
            Database.session.add(m)
            Database.session.commit()
            return jsonify({"result": True})
        else:
            return jsonify({"result": False})

    @app.route("/reset-code", methods=["POST"])
    def reset_code():
        usr = request.form["usr"]
        user = User.query.filter_by(username=usr).first()
        if user:
            session["reset_user"] = usr
            session["attempts"] = 0
            return render_template("login.html", task="reset-code")
        else:
            return redirect("/forgot?error=user_not_exists", 302)

    @app.route("/reset-user-step2", methods=["POST"])
    def reset_user():
        code = request.form["code"]
        try:
            session["code"]
        except KeyError:
            return render_template("login.html", task="reset-code", error="Please first send the OTP token")
        attempts = session["attempts"] if "attempts" in session else 1
        if code != session["code"] and attempts < 5:
            try:
                session["attempts"] += 1
            except KeyError:
                session["attempts"] = 1
            return render_template("login.html", task="reset-code", error="Invalid OPT code!")
        elif code == session["code"]:
            session["verified"] = True
            return render_template("login.html", task="reset-user-pwd", user=session["reset_user"])
        else:
            del session["code"]
            del session["reset_user"]
            del session["attempts"]
            return redirect("/forgot?error=too_many_attempts", 302)

    @app.route("/reset", methods=["POST"])
    def reset():
        new_pwd = request.form["pwd"]
        del session["code"]
        del session["attempts"]
        del session["verified"]
        usr = session["reset_user"]
        user = User.query.filter_by(username=usr).first()
        user.password = user.hash_password(new_pwd)
        del session["reset_user"]
        m = Message("+1555725991", user.phone, "Notice: the password of your account was changed successfully.")
        Database.session.add(m)
        Database.session.commit()
        return redirect("/login?message=password_reset_ok", 302)

    @app.route("/create-account", methods=["POST"])
    def create_account():
        phone = request.form["phone"]
        usr = request.form["usr"]
        pwd = request.form["pwd"]
        pwd2 = request.form["pwd2"]
        err = ""

        if len(pwd) < 6:
            err = "Password must contain at least 6 characters!"

        if pwd != pwd2:
            err = "Password does not match!"

        if not re.match(r"^([+]?1\s?)?((\([0-9]{3}\))|[0-9]{3})[\s\-]?[\0-9]{3}[\s\-]?[0-9]{4}", phone):
            err = "Phone number is invalid!"

        if User.query.filter_by(username=usr).first() is not None:
            err = "Username already taken!"

        if User.query.filter_by(phone=phone).first() is not None:
            err = "Phone number already taken!"

        if err:
            return render_template('login.html', task='create', error=err)
        user = User(username=usr, phone=phone, password=pwd, level=1)
        m = Message("+1555725991", user.phone, "Welcome to secret site, your account is now registered!")
        Database.session.add(m)
        Database.session.add(user)
        Database.session.commit()
        return redirect('/login?message=account_created', 302)

    @app.route("/virtual-phone")
    def virtual_phone():
        return render_template("virtual.html")

    @app.route("/get-number", methods=["POST"])
    def get_number():
        p = Phone.query.filter_by(ip=request.headers.get("x-forwarded-for")).first()
        if p is not None:
            return redirect("/my-virtual-phone", 301)
        done = False
        num = None
        while not done:
            num = "+1"+str(random.randint(1000000000, 9999999999))
            p1 = Phone.query.filter_by(phone=num).first()
            if p1 is None:
                done = True
        user_phone = Phone(phone=num, ip=request.headers.get("x-forwarded-for"))
        message = Message("+1133527901", num, "Welcome to virtual phone number, have fun!")
        Database.session.add(user_phone)
        Database.session.add(message)
        Database.session.commit()
        return redirect("/my-virtual-phone", 302)

    @app.route("/my-virtual-phone")
    def my_virtual_phone():
        phone = Phone.query.filter_by(ip=request.headers.get("x-forwarded-for")).first()
        if phone is not None:
            messages = Message.query.filter_by(to_num=phone.phone).all()
            return render_template("messages.html", phone=phone.get_phone, messages=messages, message_count=len(messages))
        return redirect("/virtual-phone", 302)

    @app.route("/check-virtual")
    def check():
        p = Phone.query.filter_by(ip=request.headers.get("x-forwarded-for")).first()
        if p:
            return jsonify({"result": 1})
        return jsonify({"result": 0})

    @Login.user_loader
    def load_user(uid):
        return User.query.filter_by(id=uid).first()

    @Login.unauthorized_handler
    def unauthorized():
        return redirect("/login", 302)
