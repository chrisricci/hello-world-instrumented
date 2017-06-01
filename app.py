#!flask/bin/python
import requests
import os
import sys
import logging

from flask import Flask
from prometheus_client import Summary, Counter

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

greeterUrl = os.environ.get('GREETERSERVICE') if os.environ.get('GREETERSERVICE') != None else 'http://localhost:8080'
app.logger.debug('GREETERSERVICE: ' + greeterUrl)

nameserviceUrl = os.environ.get('NAMESERVICE') if os.environ.get('NAMESERVICE') != None else 'http://localhost:8081'
app.logger.debug('NAMESERVICE: ' + nameserviceUrl)

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
@REQUEST_TIME.time()
@app.route('/')
def index():
    # Call Greeter Service
    greeterResponse = requests.get(greeterUrl)
    app.logger.debug('GREETER-RESPONSE: ' + greeterResponse.text)

    # Call Name Service
    nameserviceResponse = requests.get(nameserviceUrl) 
    app.logger.debug('NAME-SERVICE: ' + nameserviceUrl)
    return "%s, %s!" % (greeterResponse.text, nameserviceResponse.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug=True)
    start_http_server(8000)
