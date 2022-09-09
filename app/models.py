from flask_login import UserMixin
from app import db
from app import login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    uploads = db.relationship('Upload', backref='user')
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    user_id = db.Column(db.String(50), db.ForeignKey('user.username'))
    
    def __repr__(self) -> str:
        return f'<Upload {self.filename}>'
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))