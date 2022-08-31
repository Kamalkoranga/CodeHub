from io import BytesIO

from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://Kamalkoranga:v2_3thfx_3eBKFkgQfuxXk2awV7N3DDT@db.bit.io/Kamalkoranga/codehub')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app, engine_options={"pool_recycle": 55})

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']

        upload = Upload(filename=file.filename, data=file.read())
        db.session.add(upload)
        db.session.commit()

        return f'Uploaded: {file.filename}'
    files = Upload.query.all()
    return render_template('index.html', files=files)

@app.route('/download/<upload_id>')
def download(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    print(upload)
    return send_file(BytesIO(upload.data), attachment_filename=upload.filename, as_attachment=True)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)