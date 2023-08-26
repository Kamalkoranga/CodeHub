# from app import create_app, db
# from app.models import Upload, User, Comment

# app = create_app()


# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Upload': Upload, 'comment': Comment}


# if __name__ == '__main__':
#     app.run(ssl_context="adhoc")

from wsgi import app