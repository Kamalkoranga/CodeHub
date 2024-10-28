from flask import jsonify
from app import create_app, db
from app.models import Upload, User, Comment

app = create_app()

@app.route('/system_status', methods=['GET'])
def system_status():
    return jsonify({'message': "System is running properly ✅"}), 200


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Upload': Upload, 'comment': Comment}


# if __name__ == '__main__':
#     app.run()
