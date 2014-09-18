#!/usr/bin/env python3

from random import random

from bottle import Bottle, run, SimpleTemplate, static_file, template, view

MAX_POWER = 3500

app = Bottle()
SimpleTemplate.defaults['get_url'] = app.get_url

@app.route('/static/<filename:path>', name='static')
def static(filename):
    return static_file(filename, root='static')

@app.route('/ajax/:nb')
def ajax(nb):
    nb = int(nb)
    data = [{'power': random() * MAX_POWER} for i in range(nb)]
    return {'data': data}

@app.route('/')
@view('index')
def index():
    return {}

run(app, host='0.0.0.0', port=8080, debug=True)
