import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299  # may be solution of Operational Error
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT')
    SQLALCHEMY_ENABLE_POOL_PRE_PING = True
    POSTS_PER_PAGE = 30
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMINS = [(os.getenv('ADMIN_MAIL'))]
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    CODEHUB_MAIL_SENDER = 'CodeHub <admin@codehub.com>'


class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    DEBUG = True
