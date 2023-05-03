from flask import jsonify, request
from api.main import main
from api.models import User, TimeLine, File, Comment, Like
from api import db
# from flask_login import current_user


# @main.route('/current_user', methods=['GET'])
# def get_current_user():
#     return jsonify({
#         "id": current_user.id,
#         "username": current_user.username,
#         "email": current_user.email
#     }), 200


'''GET METHODS'''


@main.route('/')
def index():
    return 'Hello Api'


@main.route('/users/<username>', methods=['GET'])
def get_one_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'msg': 'user not found!'}), 400
    following = user.followed.all()
    followers = user.followers.all()
    return jsonify({
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "is_verified": user.isverified,
        "no_of_files": user.files.count(),
        "files": {
            j: user.files[j].filename for j in range(user.files.count())},
        "about": user.about_me,
        "last_seen": user.last_seen,
        "following": {j: following[j].username for j in range(len(following))},
        "followers": {j: followers[j].username for j in range(len(followers))}
    })


@main.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    response = {}
    for i in range(len(users)):
        no_of_files = users[i].files.count()
        response[i] = {
            "id": users[i].id,
            "name": users[i].name,
            "username": users[i].username,
            "email": users[i].email,
            "is_verified": users[i].isverified,
            "no_of_files": no_of_files,
            "files": {
                j: users[i].files[j].filename for j in range(no_of_files)},
            "about": users[i].about_me,
            "last_seen": users[i].last_seen
        }
    return jsonify(response), 200


@main.route('/timelines', methods=['GET'])
def get_timelines():
    timelines = TimeLine.query.all()
    response = {}
    for i in range(len(timelines)):
        response[i] = {
            "date": timelines[i].date,
            "title": timelines[i].title,
            "body": timelines[i].body
        }
    return jsonify(response), 200


@main.route('/files/<filename>', methods=['GET'])
def get_one_file(filename):
    file = File.query.filter_by(filename=filename).first()
    if not file:
        return jsonify({'msg': 'file not found'}), 400

    response = {
        "title": file.title,
        "description": file.description,
        "filename": file.filename,
        "data": file.data,
        "is_private_file": file.private_file,
        "created_at": file.timestamp,
        "user_id": file.user_id,
        "developer": file.user.username,
        "comments": {
            j: {
                file.comments[j].author: file.comments[j].content
            } for j in range(len(file.comments))
        },
        "likes": {
            j: file.likes[j].user.username for j in range(len(file.likes))
        },
        "no_of_comments": len(file.comments),
        "no_of_likes": len(file.likes)
    }
    return jsonify(response), 200


@main.route('/files', methods=['GET'])
def get_files():
    files = File.query.all()
    response = {}
    for i in range(len(files)):
        response[i] = {
            "id": files[i].id,
            "title": files[i].title,
            "description": files[i].description,
            "filename": files[i].filename,
            "data": files[i].data,
            "is_private_file": files[i].private_file,
            "created_at": files[i].timestamp,
            "user_id": files[i].user_id,
            "developer": files[i].user.username,
            "comments": {
                j: {
                    'id': files[i].comments[j].id,
                    files[i].comments[j].author: files[i].comments[j].content
                } for j in range(len(files[i].comments))
            },
            "likes": {
                j: files[i].likes[j].user.username for j in range(len(files[i].likes))
            },
            "no_of_comments": len(files[i].comments),
            "no_of_likes": len(files[i].likes)
        }
        # print(files[i].comments)
    return jsonify(response), 200


'''
    POST METHODS
'''


@main.route('/timelines', methods=['POST'])
def add_new_timeline():
    data = request.get_json()
    date = data['date']
    title = data['title']
    body = data['body']
    new_timeline = TimeLine(date=date, title=title, body=body)
    db.session.add(new_timeline)
    db.session.commit()
    return jsonify({'msg': 'added!'}), 200


@main.route('/file/<username>', methods=['POST'])
def add_new_file(username):
    data = request.get_json()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'msg': 'user not found'}), 400
    new_file = File(
        title=data['title'],
        description=data['description'],
        filename=data['filename'],
        data=data['data'],
        private_file=True if data['private_file'] == 'True' else False,
        user_id=user.id
    )
    db.session.add(new_file)
    db.session.commit()
    return jsonify({'msg': 'added!'}), 200


@main.route('/comment/<filename>', methods=['POST'])
def add_new_comment(filename):
    data = request.get_json()
    file = File.query.filter_by(filename=filename).first()
    if file is None:
        return jsonify({'msg': 'file not found'}), 400
    new_comment = Comment(
        author=data['author'],
        content=data['content'],
        file_id=file.id
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'msg': 'added'}), 200


@main.route('/like/<filename>', methods=['POST', 'GET'])
def like_file(filename):
    data = request.get_json()
    file = File.query.filter_by(filename=filename).first()
    if not file:
        return jsonify({'msg': 'file not found'}), 400
    like = Like.query.filter_by(
        author=data['author'],
        file_id=file.id
    ).first()

    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'msg': 'unliked'})

    else:
        like = Like(
            author=data['author'],
            file_id=file.id
        )
        db.session.add(like)
        db.session.commit()
    return jsonify({'msg': 'liked'})


@main.route('/follow/<username>', methods=['POST'])
def follow_unfollow_user(username):
    data = request.get_json()
    current_user = User.query.filter_by(username=data['current_user']).first()
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'msg': 'user not found!'}), 400

    if current_user == user:
        return jsonify({'msg': "can't follow/unfollow yourself"}), 400

    if current_user.is_following(user):
        current_user.unfollow(user)
        db.session.commit()
        return jsonify({'msg': 'unfollowed user'}), 200
    else:
        current_user.follow(user)
        db.session.commit()
        return jsonify({'msg': 'followed user'}), 200


'''
    PUT (UPDATE) METHODS
'''


@main.route('/edit_profile', methods=['PUT'])
def edit_profile():
    data = request.get_json()
    current_user = User.query.filter_by(username=data['current_user']).first()
    if not current_user:
        return jsonify({'msg': 'user not found'}), 400
    current_user.name = data['name']
    username_validate = User.query.filter_by(username=data['username']).first()
    email_validate = User.query.filter_by(email=data['email']).first()
    if username_validate is not None or email_validate is not None:
        return jsonify({'msg': 'username or email has taken'}), 201
    current_user.username = data['username']
    current_user.email = data['email']
    current_user.about_me = data['about']
    db.session.commit()
    return jsonify({'msg': 'updated'}), 200


@main.route('/edit_file/<filename>', methods=['PUT'])
def edit_file(filename):
    file = File.query.filter_by(filename=filename).first()
    if not file:
        return jsonify({'msg': 'file not found'}), 400
    data = request.get_json()
    file.title = data['title']
    file.description = data['description']
    file.filename = data['filename']
    file.data = data['data']
    file.private_file = True if data['private_file'] == 'True' else False
    db.session.commit()
    return jsonify({'msg': 'file updated!'}), 200


'''
    DELETE METHODS
'''


@main.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    file = File.query.filter_by(filename=filename).first()
    if not file:
        return jsonify({'msg': 'file not found'}), 400
    db.session.delete(file)
    db.session.commit()
    return jsonify({'msg': 'file deleted!'}), 200


@main.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.files:
            files = user.files
            for file in files:
                db.session.delete(file)
                db.session.commit()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'msg': 'user deleted!'}), 200
    return jsonify({'msg': 'user not found'}), 400


@main.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return jsonify({'msg': 'comment not found'}), 400
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'msg': 'comment deleted'}), 200
