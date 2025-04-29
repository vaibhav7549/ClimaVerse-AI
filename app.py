import os
import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import json
from typing import List, Dict
import numpy as np
from geopy.distance import geodesic

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)  # Enable CORS to prevent issues with frontend requests

# OpenWeatherMap API key
OPENWEATHER_API_KEY = "f75779a8a6015449da23bf3b9694ba60"

# Gemini API key (replace with your actual key)
GEMINI_API_KEY = "AIzaSyCN1M-UzpG21EDGz76W1kxrzx7lEZtzTVE"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

# Load dataset for travel planner
try:
    transport_data = pd.read_csv("transport_data.csv")
    required_columns = ['route_id', 'start_location', 'destination', 'modes', 'distance_km', 'extra_distance_km', 'notes', 'transport_mode', 'co2_per_km', 'speed_km_h']
    if not all(col in transport_data.columns for col in required_columns):
        raise ValueError(f"CSV missing required columns: {required_columns}")
except Exception as e:
    raise ValueError(f"Failed to load transport_data.csv: {str(e)}")

# Separate route and mode data
modes_data = transport_data[transport_data['route_id'].isna()][['transport_mode', 'co2_per_km', 'speed_km_h']].set_index('transport_mode')
routes_data = transport_data[transport_data['route_id'].notna()]

def calculate_route_emissions_time(modes: str, distance_km: float, extra_distance_km: float) -> tuple:
    total_emissions = 0
    total_time_h = 0
    for mode in modes.split('+'):
        mode_data = modes_data.loc[mode.strip()]
        total_emissions += (distance_km + extra_distance_km) * mode_data['co2_per_km'] / 1000  # kg CO2
        total_time_h += (distance_km + extra_distance_km) / mode_data['speed_km_h']
    hours = int(total_time_h)
    minutes = int((total_time_h - hours) * 60)
    time_str = f"{hours} hours {minutes} minutes" if minutes > 0 else f"{hours} hours"
    return total_emissions, time_str

def get_geocode(city: str) -> tuple:
    try:
        response = requests.get(
            f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        )
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return data['lat'], data['lon']
        return None, None
    except:
        return None, None

def estimate_distance(start: str, dest: str) -> float:
    start_lat, start_lon = get_geocode(start)
    dest_lat, dest_lon = get_geocode(dest)
    if start_lat and dest_lat:
        return geodesic((start_lat, start_lon), (dest_lat, dest_lon)).km
    return 0

def train_decision_tree():
    X = []
    y = []
    for _, row in routes_data.iterrows():
        modes = row['modes']
        distance_km = row['distance_km']
        extra_distance_km = row['extra_distance_km']
        emissions, _ = calculate_route_emissions_time(modes, distance_km, extra_distance_km)
        # Additional features: mode count, has_cycling, has_flight
        mode_count = len(modes.split('+'))
        has_cycling = 1 if 'Cycling' in modes or 'Walking' in modes else 0
        has_flight = 1 if 'Flight' in modes else 0
        X.append([emissions, distance_km, extra_distance_km, mode_count, has_cycling, has_flight])
        y.append(1 if 'eco-friendly' in row['notes'].lower() else 0)
    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X, y)
    return clf

clf = train_decision_tree()

def get_gemini_response(content):
    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": content}]}]
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    return f"Error: {response.status_code} - {response.text}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form["content"]
        response_text = get_gemini_response(content)
        return Response(response_text, mimetype="text/plain")
    return app.send_static_file("index.html")

@app.route("/api/geocode", methods=["GET"])
def geocode():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    try:
        response = requests.get(
            f"https://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={OPENWEATHER_API_KEY}"
        )
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch city data"}), response.status_code
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/weather", methods=["GET"])
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "lat and lon parameters are required"}), 400
    try:
        weather_response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        aqi_response = requests.get(
            f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        )
        if weather_response.status_code != 200 or aqi_response.status_code != 200:
            return jsonify({"error": "Failed to fetch weather data"}), 500
        return jsonify({
            "weather": weather_response.json(),
            "aqi": aqi_response.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/plan_trip', methods=['POST'])
def plan_trip():
    user_input = request.get_json()
    start = user_input.get('start_location')
    dest = user_input.get('destination')
    preferences = user_input.get('preferences', [])
    time_flexibility = user_input.get('time_flexibility', 'medium')

    # Filter routes for the given start and destination
    matching_routes = routes_data[
        (routes_data['start_location'] == start) & 
        (routes_data['destination'] == dest)
    ]

    options = []
    if matching_routes.empty:
        # Generate dynamic routes for unknown city pairs
        distance_km = estimate_distance(start, dest)
        if distance_km == 0:
            return jsonify({"error": "Unable to estimate distance for the route"})
        available_modes = ['Train', 'Bus', 'EV Car', 'Cycling', 'Walking', 'Metro', 'Flight']
        # Filter modes based on distance and preferences
        for mode in available_modes:
            if (mode in ['Cycling', 'Walking'] and distance_km > 50) or \
               (mode == 'Metro' and distance_km > 100) or \
               (mode == 'Flight' and distance_km < 200):
                continue
            extra_distance_km = np.random.uniform(5, 20) if mode != 'Flight' else 5
            notes = "Generated route"
            if mode == 'Flight':
                notes += "; high emissions"
            elif mode in ['Train', 'Metro', 'Cycling', 'Walking']:
                notes += "; eco-friendly"
            emissions, time_str = calculate_route_emissions_time(mode, distance_km, extra_distance_km)
            mode_count = 1
            has_cycling = 1 if mode in ['Cycling', 'Walking'] else 0
            has_flight = 1 if mode == 'Flight' else 0
            eco_score = clf.predict([[emissions, distance_km, extra_distance_km, mode_count, has_cycling, has_flight]])[0]
            if eco_score == 1 or mode in ['Walking', 'Cycling', 'Metro', 'Train', 'EV Car']:
                options.append({
                    'transport_mode': mode,
                    'estimated_time': time_str,
                    'estimated_emissions': emissions,
                    'notes': notes
                })
    else:
        # Use existing routes from CSV
        for _, route in matching_routes.iterrows():
            modes = route['modes']
            distance_km = route['distance_km']
            extra_distance_km = route['extra_distance_km']
            notes = route['notes']
            emissions, time_str = calculate_route_emissions_time(modes, distance_km, extra_distance_km)
            mode_count = len(modes.split('+'))
            has_cycling = 1 if 'Cycling' in modes or 'Walking' in modes else 0
            has_flight = 1 if 'Flight' in modes else 0
            eco_score = clf.predict([[emissions, distance_km, extra_distance_km, mode_count, has_cycling, has_flight]])[0]
            if eco_score == 1 or any(m in modes.lower() for m in ['walking', 'cycling', 'metro', 'train', 'ev_car']):
                options.append({
                    'transport_mode': modes,
                    'estimated_time': time_str,
                    'estimated_emissions': emissions,
                    'notes': notes
                })

    # Sort by emissions and select top 3
    options.sort(key=lambda x: x['estimated_emissions'])
    top_options = options[:3]

    # Format output
    result = {f"option_{i+1}": {
        "transport_mode": opt['transport_mode'],
        "estimated_time": opt['estimated_time'],
        "estimated_emissions": f"{opt['estimated_emissions']:.1f} kg CO2",
        "notes": opt['notes']
    } for i, opt in enumerate(top_options)}

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('server.crt', 'server.key'))
