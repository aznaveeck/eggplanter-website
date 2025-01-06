from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key
DATA_FILE = 'data.csv'
USERS_FILE = 'users.csv'

MOISTURE_MIN = 30

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['temperature', 'humidity', 'water_level', 'moisture'])

# Ensure the users file exists
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'password'])
        writer.writerow(['admin', 'pw123'])  # Default credentials, to be changed later

@app.route('/loading')
def loading():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('loading.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Verify credentials
        with open(USERS_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    session['username'] = username
                    return redirect(url_for('loading'))  # Changed this line
        return "Invalid username or password", 401
    return render_template('login.html')

    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

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

    # Check if moisture is below the minimum threshold
    if moisture < MOISTURE_MIN:
        if water_level == 0:
            with open(DATA_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([temperature, humidity, water_level, moisture])
            return jsonify({"error": "Moisture below minimum threshold"}), 850
        else:
            with open(DATA_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([temperature, humidity, water_level, moisture])
            return jsonify({"error": "water level below minimum threshold"}), 200


    # Append data to the CSV file
    with open(DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([temperature, humidity, water_level, moisture])

    return jsonify({"status": "success"}), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Read the last 5 entries from the CSV file
    with open(DATA_FILE, 'r') as file:
        reader = list(csv.reader(file))
        data = reader[1:]  # Skip header row
        last_entries = data[-5:] if len(data) > 0 else []

    return render_template('dashboard.html', entries=last_entries)

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
