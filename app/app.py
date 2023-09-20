# imports
from flask import Flask, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import bcrypt
import json
import os

# Setting up config json file
with open('config.json', 'r') as c:
    param = json.load(c)["params"]

# creating flask instance with database instance
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/groovydb'
app.config['SQLALCHEMY_DATABASE_URI'] = param['local_uri']
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

# For upload location
app.config['UPLOAD_FOLDER'] = param['upload_location']


# Modeling the table

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class Song(db.Model):
    songid = db.Column(db.Integer, primary_key=True,
                       nullable=False, autoincrement=True)
    songname = db.Column(db.String(45), nullable=False)
    artist = db.Column(db.String(45), nullable=False)
    genre = db.Column(db.String(45), nullable=False)
    album = db.Column(db.String(45), nullable=False)

    def __init__(self, songname, artist, genre, album):
        self.songname = songname
        self.artist = artist
        self.genre = genre
        self.album = album


 # creating table with the help of models
with app.app_context():
    db.create_all()


# creating decorates

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['Get', 'POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # to check credentials
        # to check email id, matching
        user = User.query.filter_by(email=email).first()
        # to check pass, matching
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            # return render_template('login.html', error="Wrong Credentials")
            return render_template('error.html')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'email' in session:
        songs = Song.query.first()
        return render_template('dashboard.html', songs=songs)

    flash('Please log in first', 'error')
    return redirect('/login')


@app.route('/upload',  methods=['GET', 'POST'])
def upload():
    if 'email' in session:
        # handle upload
        if (request.method == 'POST'):
            songname = request.form['songname']
            artist = request.form['artist']
            genre = request.form['genre']
            album = request.form['album']

            new_song = Song(songname=songname, artist=artist,
                            genre=genre, album=album)
            db.session.add(new_song)
            db.session.commit()

            # handle .mp3 upload
            f = request.files['file']
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            flash('Successfly Uploaded')
            return redirect('/dashboard')

        return render_template('upload.html')
    flash('Please log in first', 'error')
    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


@app.route('/profile')
def profile():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('profile.html', user=user)

    flash('Please log in first', 'error')
    return redirect('/login')



# ChatGPT gave this code to use for getting db values for table
@app.route('/')
def display_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Execute an SQL query to retrieve all rows
    cursor.execute("SELECT artist, genre, songname, album  FROM users")
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('profile.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

# debuggin
if __name__ == '__main__':
    app.run(debug=True)
