from api import create_app, db
from api.models import File, User, Comment
import os

api = create_app()


@api.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'file': File, 'comment': Comment}


port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=port)
