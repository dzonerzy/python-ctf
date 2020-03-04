import flask
from flask_sqlalchemy import SQLAlchemy


def create_app(config=None):
    app = flask.Flask(__name__)
    if config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.from_mapping(config)
    db = SQLAlchemy(app)
    return app, db
