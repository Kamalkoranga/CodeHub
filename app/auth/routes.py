
from flask import render_template, redirect, url_for, flash, request, session, abort, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db, mail
from app.auth import bp
from app.auth.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
import os
import pathlib
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_mail import Message
from threading import Thread

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="https://127.0.0.1:5000/auth/callback"
    # redirect_uri = os.getenv('REDIRECT_URI')
)
'''
@bp.route('/login', methods=['GET', 'POST'])
def login():    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        if user.username == 'aman':
            return redirect(url_for('main.admin'))
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Sign In', form=form)
'''
@bp.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    print(authorization_url)
    return redirect(authorization_url)

@bp.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

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

    google_id = id_info.get('sub') # used as a password_hash
    name = id_info.get("name")
    email = id_info.get('email')
    profile_pic = id_info.get('picture')
    # username = email.removesuffix('@gmail.com')
    # username = email.lstrip('@gmail.com')
    username = email[:-10]
    # print(username)

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(google_id):
        user = User(name=name, username=username, email=email, profile_pic=profile_pic)
        user.set_password(google_id)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        if current_app.config['ADMINS']:
            send_email(current_app.config['ADMINS'], 'New User', 'email/new_user', user=user)
            send_email([user.email], 'Welcome to CodeHub', 'email/welcome', user=user)

    login_user(user, remember=True)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('main.index')
    if user.username == 'devemail13.1':
        return redirect(url_for('main.admin'))
    return redirect(url_for('main.index'))

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message('[CodeHub]: ' + subject, sender = current_app.config['CODEHUB_MAIL_SENDER'], recipients=to)
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    '''
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)
    '''
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
