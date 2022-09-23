import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://codehubv0_1_user:vJYFkroV6xLWocjgxKW7MrQ4t9RsZpzs@dpg-cci6ulpa6gdiindmmaug-a.singapore-postgres.render.com/codehubv0_1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3