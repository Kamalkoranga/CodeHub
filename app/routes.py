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
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or user.password != form.password.data:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        if current_user.username == 'kamalkoranga13+9gse6':
            return redirect(url_for('admin'))
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
        username = form.username.data.lower()
        password = form.password.data
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/dashboard/<username>/profile')
def profile(username):
    return render_template('profile.html', user=username)

@app.route('/group_video_chat/<username>')
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
def admin():
    admin = current_user.username
    files = Upload.query.all()
    users = User.query.all()
    return render_template('admin.html', files=files, users=users, admin=admin)