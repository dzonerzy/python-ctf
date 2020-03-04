from .app import create_app
from flask_login import LoginManager
from flask_sessionstore import Session

Application, Database = create_app()
Login = LoginManager()

def init_app(flask_app):
    Login.init_app(flask_app)
    session = Session(Application)
    session.app.session_interface.db.create_all()
    flask_app.config["SESSION_SQLALCHEMY"] = Database
    from .routes import init_routes
    from .models import User
    init_routes(flask_app)
    Database.create_all()
    u = User.query.filter_by(phone="+12025550191", username='REDACTED').first()
    if not u:
        admin = User(
            username="REDACTED",
            phone="+12025550191",
            password="REDACTED",
            level=10
        )
        Database.session.add(admin)
        Database.session.commit()

