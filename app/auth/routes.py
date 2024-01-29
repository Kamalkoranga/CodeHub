from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    abort,
    current_app
)
from urllib.parse import urlparse as url_parse
from flask_login import login_user, logout_user, current_user
from app import db, mail
from app.auth import bp
from app.auth.forms import (
    ResetPasswordRequestForm,
    ResetPasswordForm,
    RegisterForm,
    LoginForm,
    Otp
)
from app.models import User
from app.email import new_send_email
import os
import pathlib
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_mail import Message
from threading import Thread
from random import randint
from dotenv import load_dotenv
import json

load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
PROJECT_ID = os.getenv('PROJECT_ID')
AUTH_URI = os.getenv('AUTH_URI')
TOKEN_URI = os.getenv('TOKEN_URI')
CERT_URL = os.getenv('CERT_URL')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
REDIRECT_URI2 = os.getenv('REDIRECT_URI2')

client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent,
    "client_secret.json"
)

# Update client_secret.json with environment variables
client_secrets_data = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "project_id": PROJECT_ID,
        "auth_uri": AUTH_URI,
        "token_uri": TOKEN_URI,
        "auth_provider_x509_cert_url": CERT_URL,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [
            REDIRECT_URI,
            REDIRECT_URI2
        ]
    }
}

# Write the updated client_secret.json file
with open(client_secrets_file, 'w') as f:
    json.dump(client_secrets_data, f)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    # Change here for testing in local machine
    redirect_uri=REDIRECT_URI2
    # redirect_uri=REDIRECT_URI
)


@bp.route('/login_email', methods=['GET', 'POST'])
def login_email():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect password')
            return redirect(url_for('auth.login_email'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        if user.username == 'aman':
            return redirect(url_for('main.admin'))
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    # print(authorization_url)
    return redirect(authorization_url)


@bp.route("/callback")
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
    # username = email.removesuffix('@gmail.com')
    # username = email.lstrip('@gmail.com')
    username = email[:-10]
    # print(username)

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
        login_user(user, remember=True)
        if current_app.config['ADMINS']:
            send_email(
                current_app.config['ADMINS'],
                'New User',
                'email/new_user',
                user=user
            )
            send_email(
                [user.email],
                'Welcome to CodeHub',
                'email/welcome',
                user=user
            )

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
    msg = Message(
        '[CodeHub]: ' + subject,
        sender=current_app.config['CODEHUB_MAIL_SENDER'],
        recipients=to
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(
        target=send_async_email,
        args=[current_app._get_current_object(), msg]
    )
    thr.start()


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


otp = randint(10000, 99999)


@bp.route('/register_email', methods=['GET', 'POST'])
def register_email():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['e'] = user.email
        new_send_email(
            user.email,
            'Verify Email',
            'email/code',
            user=user,
            code=str(otp)
        )
        flash(f"Otp sent at {user.email}.")
        return redirect(url_for('auth.verify', username=form.username.data))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/verify/<username>', methods=["POST", "GET"])
def verify(username):
    user = User.query.filter_by(username=username).first()
    session['e'] = user.email
    form = Otp()
    if form.validate_on_submit():
        session['otp'] = form.otp.data
        return redirect(url_for('auth.validate'))
    return render_template('auth/code.html', form=form)


@bp.route('/validate', methods=["POST", "GET"])
def validate():
    user = User.query.filter_by(email=session['e']).first()
    user_otp = session['otp']
    if otp == int(user_otp):
        # user.set_password(session['p'])
        user.verify()
        db.session.commit()
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        if user.username == 'aman':
            return redirect(url_for('main.admin'))
        flash('Congratulations, you are now a registered user!')
        if current_app.config['ADMINS']:
            send_email(
                current_app.config['ADMINS'],
                'New User',
                'email/new_user',
                user=user
            )
            send_email(
                [user.email],
                'Welcome to CodeHub',
                'email/welcome',
                user=user
            )
        return redirect(url_for('main.index'))
        # return redirect(url_for('auth.login_email'))
    else:
        db.session.delete(user)
        db.session.commit()
        flash("Not Verified .. Try Again!!")
        return redirect(url_for('auth.register_email'))


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
            token = user.get_reset_password_token()
            new_send_email(
                user.email,
                'Reset Password',
                'email/reset_password',
                user=user,
                token=token
            )
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login_email'))
    return render_template(
        'auth/reset_password_request.html',
        title='Reset Password',
        form=form
    )


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
        return redirect(url_for('auth.login_email'))
    return render_template('auth/reset_password.html', form=form)
