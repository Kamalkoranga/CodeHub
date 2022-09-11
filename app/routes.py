from flask import render_template, flash, redirect, url_for, request
from app import app, db, bcrypt
from app.forms import LoginForm, RegisterForm
from flask_login import login_user, current_user, login_required, logout_user
from app.models import User, Upload

@app.route('/')
def index():
    no = len(Upload.query.all())
    members=User.query.all()
    members.reverse()
    return render_template('index.html', files=Upload.query.all(), no=no, members=members)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
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

        flash('Programme Added')
        return redirect(url_for('dashboard', username=username.lower()))
    no = 0
    for file in Upload.query.all():
        if file.user.username == username:
            no += 1
        
    return render_template('dashboard.html', user=userr.capitalize(), files=Upload.query.all(), userr=userr, no=no)

@app.route('/dashboard/<username>/<filename>')
def detail(username, filename):
    print(app.root_path)
    file = Upload.query.filter_by(filename = filename).first()
    with open(f'app/static/code/{file.filename}', 'wb') as f:
        f.write(file.data)
    fi = open(f'app/static/code/{file.filename}', 'r')
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/delete/<filename>')
def delete_file(filename):
    file = Upload.query.filter_by(filename=filename).first()
    userr = file.user
    db.session.delete(file)
    db.session.commit()
    flash('Programme removed')
    return redirect(url_for('dashboard', username=userr.username))