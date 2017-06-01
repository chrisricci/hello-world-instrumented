#!flask/bin/python
import requests
import os
import sys

from flask import Flask

app = Flask(__name__)
greeterUrl = os.environ.get('GREETERSERVICE') if os.environ.get('GREETERSERVICE') != None else 'http://localhost:8080'
sys.stdout.write('GREETERSERVICE: ' + greeterUrl)

nameserviceUrl = os.environ.get('NAMESERVICE') if os.environ.get('NAMESERVICE') != None else 'http://localhost:8081'
sys.stdout.write('NAMESERVICE: ' + nameserviceUrl)

@app.route('/')
def index():
    # Call Greeter Service
    greeterResponse = requests.get(greeterUrl)
    sys.stdout.write('GREETER-RESPONSE: ' + greeterResponse.text)

    # Call Name Service
    nameserviceResponse = requests.get(nameserviceUrl) 
    sys.stdout.write('NAME-SERVICE: ' + nameserviceUrl)

    return "%s, %s!" % (greeterResponse.text, nameserviceResponse.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug=True)
