from distutils.command.upload import upload
from flask import render_template, flash, redirect, url_for, request
from app import app, db, bcrypt
from app.forms import LoginForm, RegisterForm, EditProfileForm, CommentForm, UploadFile, EmptyForm
from flask_login import login_user, current_user, login_required, logout_user
from app.models import User, Upload, Comment
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/index')
@app.route('/')
def index():
    no = len(Upload.query.all()) # error chances
    members=User.query.all()
    # print(members)
    # members.reverse()
    if current_user.is_anonymous:
        f_users = []
    else:
        f_users = current_user.followed.all()
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
            'date': '16 September 2022',
            'heading': 'UI updated',
            'paragraph': 'Updated webapp ui'
        },
        
        {
            'date': '18 September 2022',
            'heading': 'Explore Page, Profile Page and Comment Section !!',
            'paragraph': "Explore the programs made by other developers, Check Profile to know about that particular developer at ''username'' and at last but not the least Comment section where you can appericiate about their code or suggest some easy methods at ''Explore page'' -> ''filename.py''"
        },
        
        {
            'date': '20 September 2022',
            'heading': 'Title and Descriptions',
            'paragraph': 'Now you can give a stunning title and description about your program to others and fixed some ui bugs.'
        },
        
        {
            'date': '21 September 2022',
            'heading': 'A new and modern UI',
            'paragraph': 'A new ui of homepage and dashboard after login, that is responsive and looks like github.'
        },
        {
            'date': '24 September 2022',
            'heading': 'Follow and Unfollow other developers',
            'paragraph': 'Follow other developers to see their programs in seprate "Following" tab which helps to find their programs easily also you can unfollow others.'
        },
    ]
    timeline.reverse()
    if current_user.is_anonymous:
        return render_template('index.html', files=Upload.query.order_by(Upload.timestamp.desc()).all(), no=no, members=members, timeline=timeline, comments = Comment.query.all(), fuser=f_users)
    else:

        page1 = request.args.get('page', 1, type=int)
        posts1 = current_user.followed.paginate(page1, app.config['POSTS_PER_PAGE'], False)
        
        page2 = request.args.get('page', 1, type=int)
        posts2 = Upload.query.order_by(Upload.timestamp.desc()).paginate(page2, app.config['POSTS_PER_PAGE'], False)
        

        next_url1 = url_for('index', page=posts1.next_num) if posts1.has_next else None
        prev_url1 = url_for('index', page=posts1.prev_num) if posts1.has_prev else None
        
        next_url2 = url_for('index', page=posts2.next_num) if posts2.has_next else None
        prev_url2 = url_for('index', page=posts2.prev_num) if posts2.has_prev else None
    
        return render_template('index.html', files=Upload.query.order_by(Upload.timestamp.desc()).all(), no=no, members=members, timeline=timeline, comments = Comment.query.all(), fuser=f_users, posts1=posts1.items, posts2=posts2.items, next_url1=next_url1, prev_url1=prev_url1, next_url2=next_url2, prev_url2=prev_url2)

@app.route('/login', methods=['GET', 'POST'])
def login():    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        if user.username == 'aman':
            return redirect(url_for('admin'))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

# @app.route('/dashboard/<username>', methods=['GET', 'POST'])
# @login_required
# def dashboard(username):
#     userr = current_user.username
#     if request.method == 'POST':
#         file = request.files['file']

#         upload = Upload(filename=file.filename, data=file.read(), user_id=userr)
#         db.session.add(upload)
#         db.session.commit()

#         flash('Programme Added')
#         return redirect(url_for('dashboard', username=username.lower()))
#     no = 0
#     for file in Upload.query.all():
#         if file.user.username == username:
#             no += 1
        
#     return render_template('dashboard.html', files=Upload.query.all(), no=no)

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    userr = current_user.username
    form = UploadFile()
    if form.validate_on_submit():
        title =  form.title.data
        description = form.description.data
        file = form.file.data
        upload = Upload(title = title, description = description, filename = file.filename, data = file.read(), user_id=userr)
        db.session.add(upload)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('new.html', form=form)

# @app.route('/explore')
# @login_required
# def explore():
#     uploads = Upload.query.order_by(Upload.timestamp.desc()).all()
#     return render_template('explore.html', title='Explore', files=uploads)

@app.route('/file/<filename>', methods=['GET', 'POST'])
@login_required
def detail(filename):
    print(app.root_path)
    file = Upload.query.filter_by(filename = filename).first()
    with open(f'app/static/code/{file.filename}', 'wb') as f:
        f.write(file.data)
    fi = open(f'app/static/code/{file.filename}', 'r')
    a = fi.read()
    form = CommentForm()
    if form.validate_on_submit():
        # comment = Comment(author= request.form['author'], content=request.form['content'], upload_id=file.id)
        username = form.username.data
        comment = form.comment.data
        comments = Comment(author = username, content=comment, upload_id=file.id)
        db.session.add(comments)
        db.session.commit()
        return redirect(url_for('detail', filename=file.filename))
    elif request.method == 'GET':
        form.username.data = current_user.username
        
    return render_template('detail.html',f=a, file=file, username=file.user.username, form=form, users=User.query.all())

@app.route('/register', methods=['GET', 'POST'])
def register():    
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
    page = request.args.get('page', 1, type=int)
    posts = user.uploads.order_by(Upload.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, files=files, username=username, form = EmptyForm(), posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()
        
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
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

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

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
    if current_user.username == 'aman':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('index'))

@app.route('/deleteUser/<username>')
def delete_user(username):
    userr = User.query.filter_by(username=username).first()
    if userr:
        if userr.uploads:
            files = userr.uploads
            for file in files:
                db.session.delete(file)
                db.session.commit()
        db.session.delete(userr)
        db.session.commit()
        flash('User deleted!')
    if current_user.username == 'aman':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('index'))
    
@app.post('/comments/<int:comment_id>/delete')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    filename = comment.upload.filename
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('detail', filename=filename))

@app.route('/admin')
@login_required
def admin():
    admin = current_user.username
    files = Upload.query.all()
    users = User.query.all()
    return render_template('index.html', files=files, users=users, admin=admin, members=users)