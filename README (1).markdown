# ClimaVerse AI  


ClimaVerse AI is an advanced web application that integrates real-time weather forecasting, eco-friendly travel planning, and AI-driven chat functionality. Built with modern web technologies, APIs, and machine learning, it offers a visually immersive and responsive interface for users to explore weather conditions, plan sustainable trips, and interact with an AI oracle.

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Demo

Experience ClimaVerse AI live at:  
🔗 **[ClimaVerse AI Live Demo](https://climaverse-ai.onrender.com/)**  

The deployed application allows you to:
- Check real-time weather forecasts for any city.
- Plan eco-friendly travel routes with weather-adjusted recommendations.
- Interact with the AI chat interface for weather queries and general knowledge.

*Note*: The live demo is hosted on Render and may take a few seconds to spin up due to free-tier limitations. If you encounter issues, please report them via the [GitHub Issues](https://github.com/vaibhav7549/ClimaVerse-AI/issues) page.

## Features

- **Real-Time Weather Exploration**:
  - Search for weather forecasts by city using the OpenWeatherMap API.
  - Display detailed metrics (temperature, humidity, wind speed, pressure, AQI).
  - Interactive Leaflet map for city location visualization.
  - Recent city search history with quick-access buttons.

- **Eco-Friendly Travel Planner**:
  - Plan sustainable travel routes based on preferences (eco-friendly, low cost, fast).
  - Dynamically adjusts routes using weather data to avoid unsuitable modes (e.g., cycling in rain).
  - Estimates CO2 emissions and travel time for each route.
  - Employs a decision tree classifier to score route eco-friendliness.

- **AI-Powered Chat Interface**:
  - Interact with an AI oracle via the Gemini API for weather queries and general knowledge.
  - Supports weather-specific queries with detailed responses and embedded maps.
  - Features chat history export and clear functionality.

- **Responsive Design**:
  - Optimized for mobile and desktop using Tailwind CSS and custom mobile CSS.
  - Touch-friendly interactions and accessibility enhancements.

- **Immersive Visuals**:
  - Three.js for 3D background animations (disabled on mobile for performance).
  - Particles.js for dynamic particle effects.
  - GSAP for smooth UI transitions.
  - Weather-based animations (rain, snow, clear skies).

## Technologies

- **Frontend**:
  - HTML5, CSS3, JavaScript
  - Tailwind CSS for responsive styling
  - Three.js for 3D animations
  - Particles.js for particle effects
  - GSAP for animations
  - Leaflet.js for interactive maps
  - Lodash for utility functions

- **Backend**:
  - Flask (Python) for API and server logic
  - Pandas for data processing
  - Scikit-learn for decision tree classifier
  - Geopy for distance calculations
  - Requests for API calls

- **APIs**:
  - OpenWeatherMap API (weather and geocoding)
  - Gemini API (AI chat responses)

- **Data**:
  - `transport_data.csv` for travel route and mode data

## Installation

### Prerequisites
- Python 3.8+
- Node.js (optional, for development tools)
- Git
- OpenWeatherMap API key
- Gemini API key

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/vaibhav7549/ClimaVerse-AI.git
   cd ClimaVerse-AI
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure `requirements.txt` includes:
   ```
   flask
   flask-cors
   pandas
   scikit-learn
   requests
   geopy
   ```

4. **Configure API Keys**:
   - Create a `.env` file in the root directory:
     ```env
     OPENWEATHER_API_KEY=your_openweathermap_api_key
     GEMINI_API_KEY=your_gemini_api_key
     ```
   - Update `app.py` to load environment variables if preferred (requires `python-dotenv`).

5. **Generate SSL Certificates** (for local development):
   ```bash
   openssl req -x509 -newkey rsa:4096 -nodes -out server.crt -keyout server.key -days 365
   ```

6. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `https://localhost:5000`. Static files (`index.html`, `mobile.css`) are served from the `static` folder.

## Usage

1. **Weather Cosmos Mode**:
   - Enter a city name to view weather details.
   - Click recent cities for quick access.
   - Explore the interactive map and weather metrics.

2. **Eco-Friendly Travel Planner**:
   - Input start and destination cities.
   - Select preferences (eco-friendly, low cost, fast) and time flexibility.
   - Review up to three route options with emissions, time, and weather-adjusted notes.

3. **AI Nexus Mode**:
   - Ask questions via the chat interface.
   - Use quick replies for sample queries.
   - Export or clear chat history as needed.

## API Endpoints

- **GET `/api/geocode?q={city}`**:
  - Returns geocoding data for the specified city.
  - Example: `/api/geocode?q=Mumbai`

- **GET `/api/weather?lat={lat}&lon={lon}`**:
  - Returns weather and AQI data for the specified coordinates.
  - Example: `/api/weather?lat=19.0760&lon=72.8777`

- **POST `/plan_trip`**:
  - Plans eco-friendly travel routes.
  - Request body:
    ```json
    {
      "start_location": "New York City",
      "destination": "Boston",
      "preferences": ["eco-friendly", "fast"],
      "time_flexibility": "medium"
    }
    ```
  - Response:
    ```json
    {
      "option_1": {
        "transport_mode": "Train",
        "estimated_time": "3 hours 24 minutes",
        "estimated_emissions": "17.0 kg CO2",
        "notes": "Fast and eco-friendly"
      },
      ...
    }
    ```

- **POST `/`**:
  - Sends user input to the Gemini API for AI responses.
  - Request body: `content={user_input}`

## File Structure

```
ClimaVerse-AI/
├── app.py                    # Flask backend
├── static/                   # Static assets
│   ├── index.html            # Main frontend file
│   ├── mobile.css            # Mobile-specific CSS
├── transport_data.csv        # Travel route and mode data
├── server.crt                # SSL certificate (generate locally)
├── server.key                # SSL key (generate locally)
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License file
├── README.md                 # Project documentation
```

## Contributing

We welcome contributions to enhance ClimaVerse AI! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

Please ensure your code adheres to PEP 8 (Python) and Prettier (JavaScript/CSS) standards. Report bugs or suggest features via the [GitHub Issues](https://github.com/vaibhav7549/ClimaVerse-AI/issues) page.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

- **Author**: Vaibhav Krishna Chaudhari
- **GitHub**: [vaibhav7549](https://github.com/vaibhav7549)
- **Email**: [vaibhavchaudhari7549@gmail.com](mailto:vaibhavchaudhari7549@gmail.com)
- **Issues**: [GitHub Issues](https://github.com/vaibhav7549/ClimaVerse-AI/issues)

---

⭐️ If you find ClimaVerse AI useful, please give it a star on GitHub! ⭐️
