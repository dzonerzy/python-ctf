import hashlib
import datetime
import random
from . import Database
from flask_login import UserMixin


class User(Database.Model, UserMixin):
    id = Database.Column(Database.Integer, primary_key=True)
    username = Database.Column(Database.String(64),  nullable=False)
    phone = Database.Column(Database.String(64), nullable=False)
    password = Database.Column(Database.String(32), nullable=False)
    level = Database.Column(Database.Integer, nullable=False)

    def __init__(self, username, phone, password, level=1):
        self.username = username
        self.phone = phone
        self.password = self.hash_password(password)
        self.level = level

    def gen_salt(self, length=16):
        charset = list("abcdefABCDEF0123456789")
        return "".join([random.choice(charset) for _ in range(0, length)])

    def hash_password(self, password, salt=None):
        sha256 = hashlib.sha256()
        sha256.update(password.encode('latin1'))
        if salt is None:
            salt = self.gen_salt()
        sha256.update(salt.encode('latin1'))
        out = "{}:{}".format(salt, sha256.hexdigest())
        return out

    def check_password(self, password):
        salt, _ = self.password.split(":")
        return self.hash_password(password, salt) == self.password

    @property
    def is_admin(self):
        return self.level == 10

    @property
    def is_moderator(self):
        return self.level == 8

    @property
    def is_user(self):
        return self.level == 1

    def __repr__(self):
        return '<User %r>' % self.username


class Phone(Database.Model):
    id = Database.Column(Database.Integer, primary_key=True)
    phone = Database.Column(Database.String(64), nullable=False)
    ip = Database.Column(Database.String(64), nullable=False)

    def __init__(self, phone, ip):
        self.phone = phone
        self.ip = ip

    @property
    def get_phone(self):
        return self.phone

    def __repr__(self):
        return '<Phone %r>' % self.phone


class Message(Database.Model):
    id = Database.Column(Database.Integer, primary_key=True)
    date = Database.Column(Database.DateTime, nullable=False)
    content = Database.Column(Database.String(128), nullable=False)
    from_num = Database.Column(Database.String(64), nullable=False)
    to_num = Database.Column(Database.String(64), nullable=False)

    def __init__(self, f, t, content):
        self.date = datetime.datetime.now()
        self.from_num = f
        self.to_num = t
        self.content = content

    def is_directed_to(self, num):
        return self.to_num == num

    @property
    def get_content(self):
        return self.content

    @property
    def get_formatted_date(self):
        return self.date.strftime("%m/%d, %H:%M:%S")

    def __repr__(self):
        return '<Message From:%r To:%r>' % (self.from_num, self.to_num)
