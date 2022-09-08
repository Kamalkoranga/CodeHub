# Imports

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os
import glob

# Config

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER'] = 'static/code'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
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

# Forms
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username", "class": "input"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password", "class": "input"})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"autocomplete": "username", "id": "login__username", "type": "text", "class": "form__input", "placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"id": "login__password", "type": "password", "class": "form__input", "placeholder": "Password"})
    submit = SubmitField('Login')

def path(folder_path):
    path = os.getcwd()
    dir_path = f'{path}/{folder_path}'
    count = 0
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
    return count

def view():
    i = 1
    fileName = []
    parent_dir = os.getcwd() + '/static/code'
    print('All Programs: ')
    for pdf_file in glob.glob(os.path.join(parent_dir, '*.py')):
        file = os.path.basename(pdf_file)
        f_name, f_ext = os.path.splitext(file)
        i += 1
        fileName.append(file)
    return fileName

# Routes

@app.route('/')
def index():
    no = len(Upload.query.all())
    return render_template('index.html', files=Upload.query.all(), no=no)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                # print(user.username)
                flash('Successfully Logged In')
                return redirect(url_for('dashboard', username=user.username))
    return render_template('login.html', form=form)

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def dashboard(username):
    userr = current_user.username
    if request.method == 'POST':
        file = request.files['file']

        upload = Upload(filename=file.filename, data=file.read(), user_id=userr)
        db.session.add(upload)
        db.session.commit()

        # return f'Uploaded: {file.filename}'
        flash('Programme Added')
        return redirect(url_for('dashboard', username=username.lower()))
    no = 0
    for file in Upload.query.all():
        if file.user.username == username:
            no += 1
        
    return render_template('dashboard.html', user=userr.capitalize(), files=Upload.query.all(), userr=userr, no=no)
    
@app.route('/dashboard/<username>/<filename>')
def detail(username, filename):
    file = Upload.query.filter_by(filename = filename).first()
    # print(type(file.data))
    with open(f'static/code/{file.filename}', 'wb') as f:
        f.write(file.data)
    fi = open(f'static/code/{file.filename}', 'r')
    a = fi.read()
    return render_template('detail.html',f=a, file=file)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/dashboard/<username>/profile')
def profile(username):
    return render_template('profile.html', user=username.capitalize())

@app.route('/delete/<filename>')
def delete_file(filename):
    file = Upload.query.filter_by(filename=filename).first()
    userr = file.user
    db.session.delete(file)
    db.session.commit()
    flash('Programme removed')
    return redirect(url_for('dashboard', username=userr.username))

@app.errorhandler(404)
def page_not_found(e): 
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)