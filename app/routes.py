from flask import render_template, flash, redirect, url_for, request
from app import app, db, bcrypt
from app.forms import LoginForm, RegisterForm, EditProfileForm
from flask_login import login_user, current_user, login_required, logout_user
from app.models import User, Upload
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/index')
@app.route('/')
def index():
    try:
        no = len(Upload.query.all()) # error chances
    except:
        return redirect(url_for('index'))
    members=User.query.all()
    members.reverse()
    timeline = [
        {
            'date': '6 September 2022',
            'heading': 'Beginning',
            'paragraph': 'Project Started'
        },
        
        {
            'date': '12 September 2022',
            'heading': 'Deployed',
            'paragraph': 'Project Deployed Online at codehub.gq'
        },
        
        {
            'date': '14 September 2022',
            'heading': 'Group Video Call Feature',
            'paragraph': 'Added a group video call feature. You can check them out at dashboard after creating account.'
        }
    ]
    timeline.reverse()
    return render_template('index.html', files=Upload.query.all(), no=no, members=members, timeline=timeline)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # global user
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user:
    #         if bcrypt.check_password_hash(user.password, form.password.data):
    #             login_user(user)
    #             flash('Successfully Logged In')
    #             if user.username == 'kamalkoranga13+9gse6':
    #                 return redirect(url_for('admin'))
    #             else:
    #                 return redirect(url_for('dashboard', username=user.username))
                    
    # return render_template('login.html', form=form)
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard', username=current_user.username)
        return redirect(url_for('dashboard', username=current_user.username))
    return render_template('login.html', title='Sign In', form=form)

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
        
    return render_template('dashboard.html', files=Upload.query.all(), no=no)

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
    # form = RegisterForm()

    # if form.validate_on_submit():
    #     username = form.username.data.lower()
    #     password = form.password.data
    #     new_user = User(username=username, password=password)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     return redirect(url_for('login'))

    # return render_template('register.html', form=form)
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    files = Upload.query.all()
    return render_template('user.html', user=user, files=files)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()
        
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/group_video_chat/<username>')
@login_required
def group_video_chat(username):
    return render_template('group.html')

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
    flash('Programme deleted')
    if current_user.username == 'kamalkoranga13+9gse6':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('dashboard', username=userr.username))

@app.route('/deleteUser/<username>')
def delete_user(username):
    userr = User.query.filter_by(username=username).first()
    if userr:
        if userr.uploads:
            files = userr.uploads
            print(11)
            for file in files:
                db.session.delete(file)
                db.session.commit()
        db.session.delete(userr)
        db.session.commit()
        flash('User deleted!')
    if current_user == 'kamalkoranga13+9gse6':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    admin = current_user.username
    files = Upload.query.all()
    users = User.query.all()
    return render_template('admin.html', files=files, users=users, admin=admin)