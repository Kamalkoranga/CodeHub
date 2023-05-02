from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config, Development
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login_email'
login_manager.login_message = 'Please log in to access this page.'
mail = Mail()
jwt = JWTManager()


def create_app(config_class=Config):
    api = Flask(__name__)
    api.config.from_object(config_class)

    db.init_app(api)
    migrate.init_app(api, db)
    jwt.init_app(api)
    login_manager.init_app(api)
    mail.init_app(api)

    # from app.errors import bp as errors_bp
    # api.register_blueprint(errors_bp)

    from api.auth import auth as auth_bp
    api.register_blueprint(auth_bp, url_prefix='/auth')

    from api.main import main as main_bp
    api.register_blueprint(main_bp)
    return api


from api import models
