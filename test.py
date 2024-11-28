# This is only for testing for now
# Real implementation of the Website is on hold until the website is available for testing

from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Hello world!'
