import os
import pathlib
from google_auth_oauthlib.flow import Flow
from ..auth import auth
from flask import request, jsonify, session, redirect, abort, current_app
from ..models import User
from flask_jwt_extended import create_access_token
import requests
from pip._vendor import cachecontrol
import google.auth.transport.requests
from google.oauth2 import id_token
from api import db
import random
from api.email import send_email

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent,
    "client_secret.json"
)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    # redirect_uri="https://127.0.0.1:5000/auth/callback"
    redirect_uri=os.getenv('REDIRECT_URI')
)


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'msg': 'user not found!'}), 400
    if not user.check_password(password):
        return jsonify({'msg': 'incorrect password'}), 400
    if not user.isverified:
        return jsonify({'msg': 'user is not verfied..'}), 400
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200


@auth.route('/login_google')
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session
    )

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    # print(id_info)

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["profile_pic"] = id_info.get("picture")

    google_id = id_info.get('sub')  # used as a password_hash
    name = id_info.get("name")
    email = id_info.get('email')
    profile_pic = id_info.get('picture')
    username = email[:-10]

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(google_id):
        user = User(
            name=name,
            username=username,
            email=email,
            profile_pic=profile_pic
        )
        user.set_password(google_id)
        user.verify()
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=username)

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200


@auth.route('/register', methods=['POST'])
def add_new_user():
    data = request.get_json()
    new_user = User(
        name=data['name'],
        username=data['username'],
        email=data['email']
    )
    otp = random.randint(100000, 999999)
    send_email(
        new_user.email,
        'Verify Email',
        'email/code',
        user=new_user,
        code=str(otp)
    )
    new_user.set_password(data['password'])
    new_user.set_otp(otp)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'added!'}), 200


@auth.route('/register_google')
def register_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth.route('/verify_request/<username>', methods=['GET'])
def verify_request(username):
    user = User.query.filter_by(username=username).first()
    otp = random.randint(100000, 999999)
    send_email(
        user.email,
        'Verify Email',
        'email/code',
        user=user,
        code=str(otp)
    )
    user.set_otp(otp)
    db.session.commit()
    return jsonify({'msg': 'otp sent'}), 200


@auth.route('/verify/<username>', methods=['POST'])
def verify(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'msg': 'user not found'}), 400
    data = request.get_json()
    if user.otp == data['user_otp']:
        user.verify()
        access_token = create_access_token(identity=username)
        db.session.commit()
        send_email(
            current_app.config['ADMINS'],
            'New User',
            'email/new_user',
            user=user
            )
        send_email(
            user.email,
            'Welcome to CodeHub',
            'email/welcome',
            user=user
        )
        return jsonify({
            'msg': 'user verified',
            'access_token': access_token}), 200
    return jsonify({'msg': 'otp is wrong'}), 400


@auth.route('/reset_password_request', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'msg': 'user not found'}), 400
    token = user.get_reset_password_token()
    send_email(
        user.email,
        'Reset Password',
        'email/reset_password',
        user=user,
        token=token
    )
    return jsonify({'msg': 'reset password email sent'}), 200


@auth.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    user = User.verify_reset_password_token(token)
    if not user:
        return jsonify({'msg': 'user not found'}), 400
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'msg': 'password reseted!'}), 200
