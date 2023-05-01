import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from config import Config, Development
from flask_socketio import SocketIO


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login_email'
login_manager.login_message = 'Please log in to access this page.'
mail = Mail()
moment = Moment()
socketio = SocketIO()


def create_app(config_class=Development):
    api = Flask(__name__)
    api.config.from_object(config_class)

    db.init_app(api)
    migrate.init_app(api, db)
    login_manager.init_app(api)
    mail.init_app(api)
    moment.init_app(api)
    socketio.init_app(api, cors_allowed_origins="*")

    # from app.errors import bp as errors_bp
    # api.register_blueprint(errors_bp)

    # from app.auth import bp as auth_bp
    # api.register_blueprint(auth_bp, url_prefix='/auth')

    from api.main import main as main_bp
    api.register_blueprint(main_bp)
    return api


from api import models
