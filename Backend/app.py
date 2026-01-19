from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

APP_KEY = "aa273bb9b34546c1be6e3640c78dd5d4"

@app.route("/stops/<lat>/<lon>", strict_slashes=False)

def get_busstops(lat, lon):

    url = "https://api.tfl.gov.uk/StopPoint"

    params = {
        "lat": float(lat),
        "lon": float(lon),
        "stopTypes": "NaptanPublicBusCoachTram",
        "app_key": APP_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return jsonify({
            "error": "TfL API error",
            "status": response.status_code,
            "body": response.text
        }), 500

    data = response.json()

    stops = [
        {
            "id": stop.get("id"),
            "name": stop.get("commonName")
        }
        for stop in data.get("stopPoints", [])
    ]

    return jsonify(stops)


@app.route("/")

def home():
    return "Flask is running"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)