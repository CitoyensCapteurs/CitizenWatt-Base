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

# API
@app.route('/api/sensors')
def api_sensors():
    data = [{'id': 1, 'type': 'power'}]
    return {'data': data}

@app.route('/api/<sensor:int>/get/by_id/<id1:int>')
def api_get_id(sensor, id1):
    data = [{'power': generate_value()} for i in range(id1)]
    return {'data': data}

@app.route('/api/<sensor:int>/get/by_id/<id1:int>/<id2:int>')
def api_get_ids(sensor, id1, id2):
    data = [{'power': generate_value()} for i in range(id2)]
    return {'data': data}

@app.route('/api/<sensor:int>/get/by_time/<time1:int>')
def api_get_time(sensor, time1):
    data = [{'power': generate_value()} for i in range(time1)]
    return {'data': data}

@app.route('/api/<sensor:int>/get/by_time/<time1:int>/<time2:int>')
def api_get_times(sensor, time1, time2):
    data = [{'power': generate_value()} for i in range(time2)]
    return {'data': data}


# Routes

@app.route('/static/<filename:path>', name='static')
def static(filename):
    return static_file(filename, root='static')

@app.route('/', name='index')
@view('index')
def index():
    return {'API_URL': app.get_url('index')}

run(app, host='0.0.0.0', port=8080, debug=True)
