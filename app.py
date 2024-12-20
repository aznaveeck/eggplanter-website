from flask import Flask, request, jsonify, render_template
import csv
import os

app = Flask(__name__)
DATA_FILE = 'data.csv'

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['temperature', 'humidity', 'water_level', 'moisture'])

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400
    
    # Extract values from received data
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    water_level = data.get("water_level")
    moisture = data.get("moisture")

    if None in [temperature, humidity, water_level, moisture]:
        return jsonify({"error": "Missing one or more data fields"}), 400

    # Append data to the CSV file
    with open(DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([temperature, humidity, water_level, moisture])

    return jsonify({"status": "success"}), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Read the last 5 entries from the CSV file
    with open(DATA_FILE, 'r') as file:
        reader = list(csv.reader(file))
        data = reader[1:]  # Skip header row
        last_entries = data[-5:] if len(data) > 0 else []

    return render_template('dashboard.html', entries=last_entries)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)