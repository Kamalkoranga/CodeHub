import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://codehub_b65g_user:WQ57qk82R0vMXxe7qbn9vQzaiWd7CHER@dpg-cchiqharrk0ci3q8qqe0-a.oregon-postgres.render.com/codehub_b65g'
    SQLALCHEMY_TRACK_MODIFICATIONS = False