from flask import Blueprint

auth = Blueprint('auth', __name__)

from api.auth import routes
