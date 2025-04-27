
import os
import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)  # Enable CORS to prevent issues with frontend requests

# OpenWeatherMap API key
OPENWEATHER_API_KEY = "f75779a8a6015449da23bf3b9694ba60"

# Gemini API key (replace with your actual key)
GEMINI_API_KEY = "AIzaSyCN1M-UzpG21EDGz76W1kxrzx7lEZtzTVE"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

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
if __name__ == "__main__":
    app.run(debug=True)  # Remove ssl_context=('server.crt', 'server.key')
