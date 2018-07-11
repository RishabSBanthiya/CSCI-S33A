from flask import Flask # Import the class `Flask` from the `flask` module, written by someone else.
import requests

app = Flask(__name__) # Instantiate a new web application called `app`, with `__name__` representing the current file

@app.route("/") # A decorator; when the user goes to the route `/`, exceute the function immediately below
@app.route("/")
def main():
    res = requests.get('https://api.darksky.net/forecast/df3772a5d17904133ee7948167325a28/42.360082,-71.058880' )
    data=res.text
    parsed_json = json.loads(data)
    currently=(parsed_json['currently'])
    return currently["summary"]