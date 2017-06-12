#!flask/bin/python
import requests
import os
import sys
import logging
import datetime

from flask import Flask
from flask_prometheus import monitor

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

@app.route('/')
def index():
    # Call Greeter Service
    timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))	
    return timestamp + " Hello, World!\n"

if __name__ == '__main__':
    monitor(app, port=8000)
    app.run(host='0.0.0.0')
