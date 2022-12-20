from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login_manager
from sqlalchemy.sql import func

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# The User class is a database model that inherits from db.Model and UserMixin
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.Text)
    profile_pic = db.Column(db.Text)
    isverified = db.Column(db.Boolean, default=False)
    uploads = db.relationship('Upload', backref='user', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('Like', backref='user', passive_deletes=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def verify(self):
        self.isverified = True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        if self.profile_pic:
            return self.profile_pic
        else:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, 120)

    # def avatar(self, size):
    #     digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    #     return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

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
        """
        "Return a query object that contains all the posts of the users that the current user is
        following, as well as the current user's own posts, ordered by timestamp."

        The first line of the function is a query object that contains all the posts of the users that
        the current user is following. The second line is a query object that contains the current
        user's own posts. The third line combines the two query objects into one, and orders the posts
        by timestamp
        :return: The followed.union(own) is returning a union of the two queries.
        """
        followed = Upload.query.join(
            followers, (followers.c.followed_id == Upload.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Upload.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Upload.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

# The Upload class is a database model that represents a file upload. It has a title, description,
# filename, data, timestamp, user_id, and comments
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.Text)
    filename = db.Column(db.String(50), unique=True)
    data = db.Column(db.Text)
    private_file = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.String(64), db.ForeignKey('user.username'))
    comments = db.relationship('Comment', backref='upload')
    likes = db.relationship('Like', backref='upload', passive_deletes=True)

    def __repr__(self) -> str:
        return f'<Upload {self.filename}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# It defines a table named comment, with four columns, id, author, content, and timestamp. The id
# column is an integer and is the primary key of the table. The author column is a string with a
# maximum length of 100 characters. The content column is a text column. The timestamp column is a
# datetime column
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'))
    likes = db.relationship('Like', backref='comment', passive_deletes=True)

    def __repr__(self):
        return f'<Comment "{self.content[:20]}...">'

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    upload_id = db.Column(db.Integer, db.ForeignKey(
        'upload.id', ondelete="CASCADE"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))