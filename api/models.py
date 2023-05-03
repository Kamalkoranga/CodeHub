from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from api import db, login_manager
from sqlalchemy.sql import func
from random import randint

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    files = db.relationship('File', backref='user', lazy='dynamic')
    profile_pic = db.Column(db.Text)
    isverified = db.Column(db.Boolean, default=False)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    otp = db.Column(db.Integer, default=randint(100000, 999999))
    likes = db.relationship('Like', backref='user', passive_deletes=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_otp(self, otp):
        self.otp = otp

    def verify(self):
        self.isverified = True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        if self.profile_pic:
            return self.profile_pic
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={120}'

    # def avatar(self, size):
    #     digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    #     return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'\
        # .format(digest, size)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = File.query.join(
            followers, (followers.c.followed_id == File.user_id)).filter(
                followers.c.follower_id == self.id)
        own = File.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(File.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
        except Exception:
            return
        return User.query.get(id)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.Text)
    filename = db.Column(db.String(50), unique=True)
    data = db.Column(db.Text)
    private_file = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='file', passive_deletes=True)
    likes = db.relationship('Like', backref='file', passive_deletes=True)

    def __repr__(self) -> str:
        return f'<File {self.filename}>'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    file_id = db.Column(db.Integer, db.ForeignKey(
        'file.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f'<Comment "{self.content[:20]}...">'


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey(
        'file.id', ondelete="CASCADE"), nullable=False)


class TimeLine(db.Model):
    __tablename__ = 'timelines'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text)
