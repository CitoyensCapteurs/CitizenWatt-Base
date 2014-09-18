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

@app.route('/api/get/<nb1:int>')
def api_get_last(nb1):
    data = [{'power': generate_value()} for i in range(nb1)]
    return {'data': data}

@app.route('/api/get/<nb1:int>/<nb2:int>')
def api_get_items(nb1, nb2):
    data = [{'power': generate_value()} for i in range(nb2)]
    return {'data': data}

@app.route('/', name='index')
@view('index')
def index():
    return {'API_URL': app.get_url('index')}

run(app, host='0.0.0.0', port=8080, debug=True)
