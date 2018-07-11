import os

from flask import Flask, session
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template('layout.html')

def index():

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def login():

    username = request.form.get("Username")
    password = request.form.get("Password")

    db.execute('INSERT INTO \"User\" (Username,Password) VALUES (:Username, :Password)',
                   {'Username': username, 'Password': password })
    return 'Success'

def do_admin_login():

    username = request.form.get("Username")
    password = request.form.get("Password")

    db.execute('INSERT INTO \"User\" (Username,Password) VALUES (:Username, :Password)',
                   {'Username': username, 'Password': password })
    return 'Success'

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

