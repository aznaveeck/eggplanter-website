from flask import Flask, request, jsonify, render_template
import csv
import os
import pyotp
import time

app = Flask(__name__)

# Temporary storage file
CSV_FILE = 'data.csv'

# Ensure CSV file exists and has a header
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['value1', 'value2', 'value3', 'secret'])

# Get the secret key for authentication
SECRET_FILE = 'secret.txt'
TOTP_SECRET = open(SECRET_FILE, 'r').readline().strip()

# Testing route to check connection in a browser
@app.route('/')
def index():
    return render_template('index.html')

# Route for keepalive signals
@app.route('/keepalive', methods=['POST'])
def upload_keepalive():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be in JSON format'}), 400
        data = request.get_json()
        # Get client id from request
        id_client = data.get('id')
        # Get client totp from request
        totp_client = data.get('otp')
        # Get timestamp from request
        time_client = data.get('time')

        # Generate current server totp
        totp = pyotp.TOTP(TOTP_SECRET)
        server_totp = totp.now()

        # Print both totp
        print(server_totp)
        print(totp_client)
        print(time_client)
        if server_totp == totp_client:
            return jsonify({'message': 'Keepalive valid'}), 200
        elif server_totp != totp_client:
            return jsonify({'message': 'TOTP key invalid'}), 800
        else:
            return jsonify({'message': 'Something went wrong after connecting to the server'}), 700
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for receiving data from controllers
@app.route('/upload', methods=['POST'])
def upload_data():
    try:
        # Check if the request contains JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must be in JSON format'}), 400

        # Use get_json() to safely parse JSON data
        data = request.get_json()
        values = [
            data.get('value1'),
            data.get('value2'),
            data.get('value3'),
        ]

        # Get the totp sent by the controller
        totp_client = data.get('otp')

        # Generate current server totp
        totp = pyotp.TOTP(TOTP_SECRET)
        server_totp = totp.now()

        # Print both totp
        print(server_totp)
        print(totp_client)

        # Save data to CSV
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(values)

        return jsonify({'message': 'Data uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Route for active tasks
@app.route('/tasks', methods=['POST'])
def tasks():
    TASK_FILE = 'tasks.txt'
    #Check if the data is in JSON format
    if not request.is_json:
        return jsonify({'error': 'Request must be in JSON format'}), 400
    #Get the otp from the request
    data = request.get_json()
    totp_client = data.get('otp')
    #Generate the current server otp
    totp = pyotp.TOTP(TOTP_SECRET)
    server_totp = totp.now()
    #check if the Server and Client OTP match
    if server_totp == totp_client:
        #Open and read the value in the task file to check for available tasks.
        task_file = open(TASK_FILE, 'r')
        tasks = (task_file.readline())
        print(tasks)
        #Check if a Watering job is available 
        if tasks == 1:
            return jsonify({'message': 'Watering job available'}), 1100
        #Check if no watering job is available
        elif tasks == 0:
            return jsonify({'messgae': 'No watering job available'}), 1200
        return jsonify({'message': 'Something went wrong after connecting to the server after the otp was verified'}), 700
    else:
        return jsonify({'message': 'Something went wrong after connecting to the server'}), 700
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


