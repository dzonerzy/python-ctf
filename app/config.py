import os
import base64


SESSION_USE_SIGNER = True
SECRET_KEY = base64.b64encode(os.urandom(32))
SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite"
SQLALCHEMY_TRACK_MODIFICATIONS = False
TEMPLATES_AUTO_RELOAD = True
SESSION_TYPE = "sqlalchemy"
SESSION_SQLALCHEMY_TABLE = 'sessions'
