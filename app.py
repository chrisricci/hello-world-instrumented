#!flask/bin/python
import requests
import os
import sys

from flask import Flask

app = Flask(__name__)
greeterUrl = os.environ.get('GREETER-SERVICE') if os.environ.get('GREETER-SERVICE') != None else 'http://localhost:8080'
sys.stdout.write('GREETER-SERVICE: ' + greeterUrl)

nameserviceUrl = os.environ.get('NAME-SERVICE') if os.environ.get('NAME-SERVICE') != None else 'http://localhost:8081'
sys.stdout.write('NAME-SERVICE: ' + nameserviceUrl)

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
