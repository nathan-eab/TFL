from flask import Flask, jsonify, render_template
import requests
from collections import defaultdict
import re

app = Flask(__name__, static_folder="static", template_folder="templates")

APP_KEY = "aa273bb9b34546c1be6e3640c78dd5d4"

@app.route("/")
def ui():
    return render_template("index.html")

def clean_base_name(name):
    name = re.sub(r"\s*→.*$", "", name)
    name = re.sub(r"\s*Stop\s+[A-Z0-9]+$", "", name)
    return name.strip()

def clean_letter(letter, name=None):
    if letter:
        letter = re.sub(r"[^A-Z0-9]", "", letter)
        return letter or None
    if name:
        m = re.search(r"\bStop\s+([A-Z0-9]+)$", name)
        if m:
            return m.group(1)
    return None

@app.route("/stops/<lat>/<lon>")
def stops(lat, lon):
    r = requests.get(
        "https://api.tfl.gov.uk/StopPoint",
        params={
            "lat": lat,
            "lon": lon,
            "stopTypes": "NaptanPublicBusCoachTram",
            "app_key": APP_KEY
        }
    )
    data = r.json()
    grouped = defaultdict(list)

    for s in data.get("stopPoints", []):
        naptan = s.get("naptanId")
        name = s.get("commonName")
        if not naptan or not name:
            continue

        base = clean_base_name(name)
        letter = clean_letter(s.get("stopLetter"), name)

        grouped[base].append({
            "id": naptan,
            "letter": letter
        })

    return jsonify([
        {"name": base, "stops": stops}
        for base, stops in grouped.items()
    ])

@app.route("/search/<query>")
def search(query):
    r = requests.get(
        "https://api.tfl.gov.uk/StopPoint/Search",
        params={
            "query": query,
            "modes": "bus",
            "app_key": APP_KEY
        }
    )
    data = r.json()
    grouped = defaultdict(list)

    for m in data.get("matches", []):
        lat = m.get("lat")
        lon = m.get("lon")
        name = m.get("name")

        if not lat or not lon or not name:
            continue

        # 🔥 SECOND REQUEST — SAME AS LOCATION
        r2 = requests.get(
            "https://api.tfl.gov.uk/StopPoint",
            params={
                "lat": lat,
                "lon": lon,
                "stopTypes": "NaptanPublicBusCoachTram",
                "radius": 120,
                "app_key": APP_KEY
            }
        )

        data2 = r2.json()

        for s in data2.get("stopPoints", []):
            naptan = s.get("naptanId")
            cname = s.get("commonName")
            letter = s.get("stopLetter")

            if not naptan or not cname:
                continue

            base = clean_base_name(cname)
            letter = clean_letter(letter, cname)

            grouped[base].append({
                "id": naptan,
                "letter": letter
            })

    return jsonify([
        {"name": base, "stops": stops}
        for base, stops in grouped.items()
        if len(stops) > 0
    ])


@app.route("/arrivals/<stop_id>")
def arrivals(stop_id):
    r = requests.get(
        f"https://api.tfl.gov.uk/StopPoint/{stop_id}/Arrivals",
        params={"app_key": APP_KEY}
    )
    arrivals = sorted(r.json(), key=lambda a: a.get("timeToStation", 9999))

    return jsonify([
        {
            "line": a["lineName"],
            "destination": a["destinationName"],
            "minutes": max(1, a["timeToStation"] // 60)
        }
        for a in arrivals[:10]
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
