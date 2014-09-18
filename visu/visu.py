#!/usr/bin/env python3

from random import random
from math import sin

from bottle import Bottle, run, SimpleTemplate, static_file, template, view

## Constants ##
BASE_URL = '' # without leading /
MAX_POWER = 3500
## ##

n_values = 0
def generate_value():
    """Generate values for debug purpose"""
    global n_values
    n_values += 1
    return sin(n_values / 10.0) ** 2 * MAX_POWER
    return random() * MAX_POWER

app = Bottle()
SimpleTemplate.defaults['get_url'] = app.get_url

@app.route('/static/<filename:path>', name='static')
def static(filename):
    return static_file(filename, root='static')

@app.route('/ajax/:nb')
def ajax(nb):
    nb = int(nb)
    data = [{'power': generate_value()} for i in range(nb)]
    return {'data': data}

@app.route('/')
@view('index')
def index():
    return {'BASE_URL': BASE_URL}

run(app, host='0.0.0.0', port=8080, debug=True)
