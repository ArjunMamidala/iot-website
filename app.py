# from flask import Flask, jsonify, send_from_directory
# from flask_cors import CORS
# import os
# import requests

# app = Flask(__name__)

# # Enable CORS for all routes
# CORS(app)

# # Serve static files (like index.html and Locations.html) from the 'public' folder
# @app.route("/")
# def index():
#     return send_from_directory(os.path.join(app.root_path, 'public'), 'index.html')

# @app.route('/public/<path:filename>')
# def serve_static(filename):
#     return send_from_directory(os.path.join(app.root_path, 'public'), filename)


# @app.route("/Locations.html")
# def locations():
#     return send_from_directory(os.path.join(app.root_path, 'public'), 'Locations.html')

# @app.route("/api/status")
# def proxy_status():
#     try:
#         response = requests.get("http://172.20.10.12:8080/status")
#         return jsonify(response.json())
#     except requests.RequestException as e:
#         return jsonify({"error": "Failed to fetch data"}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=3000)


from flask import Flask, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
import requests
import datetime

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Define expected values for Saturday
expected_values = {
    "10am": 5,
    "11am": 10,
    "12pm": 10
}

# Function to generate the meter representation
def generate_meter(time_of_day, actual):
    expected = expected_values[time_of_day]
    ratio = min(actual / expected, 1) 

    # Calculate the number of highlighted segments (out of 10)
    highlighted_segments = int(ratio * 10)

    return highlighted_segments, 10 - highlighted_segments  # Segments that are filled and remaining

# Serve static files from the root directory
@app.route("/")
def index():
    return send_from_directory(os.path.join(app.root_path), 'index.html')

@app.route("/Locations.html")
def locations():
    return send_from_directory(os.path.join(app.root_path), 'Locations.html')

@app.route("/styles.css")
def serve_css():
    return send_from_directory(os.path.join(app.root_path), 'styles.css')

@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory(os.path.join(app.root_path, 'images'), filename)

# API route to fetch actual dog count from another service
@app.route("/api/status")
def proxy_status():
    try:
        response = requests.get("http://192.168.1.34:8080/status")
        # Assuming the response has a "dog_count" and a "timestamp" field
        data = response.json()
        dog_count = data.get("dog_count", 0)  # Default to 0 if not available
        timestamp = data.get("timestamp", "")  # Assuming timestamp is in a format like '2025-09-06T10:30:00'

        # Parse the timestamp to get the hour part
        timestamp_obj = datetime.datetime.fromisoformat(timestamp)  # Parse timestamp
        hour = timestamp_obj.hour

        # Determine the time slot (10am, 11am, or 12pm)
        if hour == 10:
            time_of_day = "10am"
        elif hour == 11:
            time_of_day = "11am"
        elif hour == 12:
            time_of_day = "12pm"
        else:
            return jsonify({"error": "Timestamp is outside the expected time slots"}), 400

        return jsonify({"dog_count": dog_count, "time_of_day": time_of_day, "timestamp": timestamp})

    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch data"}), 500

@app.route("/dog_count_meter")
def dog_count_meter():
    # Call the /api/status to get the actual dog count and the timestamp
    try:
        response = requests.get("http://127.0.0.1:3000/api/status")  # Call your internal API
        data = response.json()
        actual = data.get("dog_count", 0)
        time_of_day = data.get("time_of_day", "")
        
        if not time_of_day:
            return jsonify({"error": "No valid time_of_day data"}), 400
        
        highlighted, remaining = generate_meter(time_of_day, actual)

        # HTML template for rendering the meter, replacing dog count and timestamp with the meter
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Park Crowd Meter</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .meter {{
                    display: flex;
                    justify-content: space-between;
                    width: 300px;
                    height: 30px;
                    background-color: #e0e0e0;
                    border-radius: 15px;
                    overflow: hidden;
                }}
                .segment {{
                    flex: 1;
                    margin: 0 2px;
                    background-color: #ddd;
                    border-radius: 5px;
                }}
                .filled {{
                    background-color: #4caf50; /* Green for filled segments */
                }}
                .container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    text-align: center;
                }}
                select {{
                    padding: 10px;
                    font-size: 16px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Park Crowd Meter</h1>
                <p>Check real-time crowd levels at each location</p>
                <label for="location">Choose a location:</label>
                <select id="location">
                    <option value="PawPatrol Park">PawPatrol Park</option>
                    <!-- Add more locations if needed -->
                </select>

                <div class="meter" style="margin-top: 20px;">
                    {"".join(['<div class="segment filled"></div>' for _ in range(highlighted)])}
                    {"".join(['<div class="segment"></div>' for _ in range(remaining)])}
                </div>

                <p>Dog Count: {actual} / Expected: {expected_values[time_of_day]}</p>
                <p>Last Updated: {data.get("timestamp", "Not available")}</p>
            </div>
        </body>
        </html>
        """

        return render_template_string(html_content)
    except requests.RequestException:
        return jsonify({"error": "Unable to fetch actual dog count"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
