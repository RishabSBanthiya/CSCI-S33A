import os
from flask import Flask, session,json,jsonify
import requests
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

#Directs users to home page where they can either log-in or search

@app.route("/")
def home():

    return render_template('home.html')
        # return session.get('zipcode')

@app.route("/index")
def index():

    if not session.get('logged_in'):
        return render_template('login.html')

    else:

      return location()
        # return session.get('zipcode')


# Allows users to register
@app.route('/register', methods=['POST','GET'])
def register():
     if  session.get('logged_in'):
        return render_template('success.html')
     else:
        #getting user details from form
        username = request.form.get("Username")
        password = request.form.get("Password")
        #inserting new user to User table in database
        db.execute('INSERT INTO \"User\" (Username,Password) VALUES (:Username, :Password)',
                   {'Username': username, 'Password': password })
        #starting the session for user
        session['logged_in'] = True
        session['user_id'] = username
        return render_template('success.html')

# Allows users to login
@app.route('/login', methods=['POST','GET'])
def login():

     if  session.get('logged_in'):
        return render_template('success.html')
     else:
        #getting user details from form
        username = request.form.get("Username")
        password = request.form.get("Password")
        session['user_id'] = username
        session['logged_in'] = True
        #vaildating used
        valid= db.execute('SELECT Password FROM \"User\"WHERE Username LIKE :username',{"username":username}) .fetchone()
        if valid is None:
           return render_template("error.html")
        elif valid[0] == password:
          return render_template("success.html")

        else:
          return render_template("error.html")

# Allows users to logout
@app.route("/logout")
def logout():
    session.clear()
    return index()

# Navigates user to zip finder
@app.route("/location")
def location():
    if  session.get('logged_in') :

        return render_template("weather.html")

    else :
        #if user hasn't logged in it will redirect to login page
      return render_template('login.html')

# Searches the zipcodes
@app.route("/zips", methods=['POST','GET'])
def zips():
    zipcode = request.form.get("Zipcode")
    #adding % to allow for partial searched
    zipy="%"+zipcode+"%"
    #decalaring users current zipcode
    session['zipcode']=zipcode
    #checking if zip exists
    zips= db.execute('SELECT * FROM \"ZIPCODE\"WHERE zip LIKE :zip',{"zip":zipy}).fetchall()
    if not zips:
        return render_template("error.html")
    else:
         return render_template("zips.html", zips=zips)

Comments=[]

# Gets the weather data from dark sky
@app.route("/weather",methods=['POST','GET'])
def weather():

    if  not session.get('logged_in'):
          #if user hasn't logged in it will redirect to login page
        return render_template('login.html')
    else:
         if not session.get('checked'):
           zipcode = request.args.get('zip')
           session['zipcode']=zipcode

         lat= db.execute('SELECT lat FROM \"ZIPCODE\"WHERE zip LIKE :zip',{"zip":session.get('zipcode')}).fetchone()
         longitude = db.execute('SELECT long FROM \"ZIPCODE\"WHERE zip LIKE :zip',{"zip":session.get('zipcode')}).fetchone()
         query = requests.get("https://api.darksky.net/forecast/481d5ba64549cc9fb76fa705cb31c5cd/{},{}".format(lat[0],longitude[0])).json()

         temp = query["currently"]["temperature"]
         time = query["currently"]["time"]
         summary = query["currently"]["summary"]
         humidity = query["currently"]["humidity"]
         dewPoint = query["currently"]["dewPoint"]
         session['query']=True
         session['checked']=True




    if request.method == "POST":
          if not session.get('logged_in'):
               #if user hasn't logged in it will redirect to login page
            return render_template('login.html')

          else:
              #allows users to checkin and comment
           user=session.get('user_id')
           valid= db.execute('SELECT * FROM CHECKIN WHERE userid LIKE :username',{"username":session.get('user_id')}) .fetchone()
           if valid is None:
             Comment = request.form.get("Comment")
             Comments.append(Comment)
             db.execute('UPDATE \"ZIPCODE\" SET \"check\"=\"check\"+1  WHERE zip=:zip',{"zip":session.get('zipcode')})
             db.execute('INSERT INTO CHECKIN (zip,userid) VALUES (:zip,:userid)' ,{"zip":session.get('zipcode'),
             'userid':session.get('user_id') })
             db.commit()
             #declaring that the user has checked in
             session['checked']=True




           else:
               #checking if the user has already checked in at that zip
                if session.get('checked')==True:
                 return render_template('checked.html')

                else:

                 Comment = request.form.get("Comment")
                 Comments.append(Comment)
                 db.execute('UPDATE \"ZIPCODE\" SET \"check\"=\"check\"+1  WHERE zip=:zip',{"zip":session.get('zipcode')})
                 db.execute('INSERT INTO CHECKIN (zip,userid) VALUES (:zip,:userid)' ,{"zip":session.get('zipcode'),
                 'userid':session.get('user_id') })
                 db.commit()
                 session['checked']=True




    return render_template("weatherdetails.html", temp=temp,time=time,summary=summary,Comments=Comments,humidity=humidity,dewPoint=dewPoint)

@app.route("/api")
def api():
    return render_template('api.html')

@app.route("/api/<zip>")
def weather_api(zip):

    lat= db.execute('SELECT lat FROM \"ZIPCODE\"WHERE zip LIKE :zip',{"zip":zip}).fetchone()
    longitude = db.execute('SELECT long FROM \"ZIPCODE\"WHERE zip LIKE :zip',{"zip":zip}).fetchone()

    # query=requests.get( "https://api.darksky.net/forecast/481d5ba64549cc9fb76fa705cb31c5cd/{},{}".format(float(lat[0]),float(longitude[0])))
    query = requests.get("https://api.darksky.net/forecast/481d5ba64549cc9fb76fa705cb31c5cd/{},{}".format(lat[0],longitude[0])).json()
    temp = query["currently"]["temperature"]
    check= db.execute('SELECT \"check\" FROM \"ZIPCODE\"WHERE zip LIKE :zip',{"zip":zip}).fetchone()
    check=check[0]
    time = query["currently"]["time"]
    summary = query["currently"]["summary"]
    humidity = query["currently"]["humidity"]
    dewPoint = query["currently"]["dewPoint"]





    return jsonify({
            "Temprature": temp,
            "Time": time,
            "Summary": summary,
            "humiity": humidity,
            "dewPoint":dewPoint,
            "Check":check
    })