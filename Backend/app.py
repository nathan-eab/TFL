from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

APP_KEY = "aa273bb9b34546c1be6e3640c78dd5d4"

@app.route("/")

def get_busstops(lat, lon):
    lat = 51.51679
    lon = -0.012329
    url = "https://api.tfl.gov.uk/StopPoint"
    parameters = {
                    "lat": lat,
                    "lon": lon,
                    "stopTypes": "NaptamPublicBusCoachTram",
                    "app_key": APP_KEY                    
                 }
    response = requests.get(url, params=parameters)
    data = response.json()

    stops = []
    for stop in data.get("stopPoints", []):
        stops.append({"id":stop.get("id"),"name": stop.get("commonName")})

    return jsonify(stops)

def home():
    return "Flask is running"

if __name__ == "__main__":
    home()
    app.run(debug=True)
