from api import create_app, db
from api.models import File, User, Comment

api = create_app()


@api.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'file': File, 'comment': Comment}


if __name__ == '__main__':
    api.run(debug=True)
