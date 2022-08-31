# Imports
from flask import Flask, render_template

# Apis
# https://4u8i9f.deta.dev/

# Database
fakeDatabase = [
    {
        'title': 'First Post',
        'description': 'This is the first post',
        'technology': 'Python',
        'coder': 'John Doe',
    },
    {
        'title': 'Second Post',
        'description': 'This is the second post',
        'technology': 'Python, CSV',
        'coder': 'Kamal',
    }
]

# Instances
app = Flask(__name__)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    return render_template('projects.html', db=fakeDatabase)

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Run
if __name__ == '__main__':
    app.run(debug=True)