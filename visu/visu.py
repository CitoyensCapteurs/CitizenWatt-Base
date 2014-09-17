#!/usr/bin/env python3

from bottle import Bottle, run, SimpleTemplate, static_file, template, view

app = Bottle()
SimpleTemplate.defaults['get_url'] = app.get_url

@app.route('/static/<filename:path>', name='static')
def static(filename):
    return static_file(filename, root='static')

@app.route('/ajax')
def ajax():
    return

@app.route('/')
@view('index')
def index():
    return {}

run(app, host='0.0.0.0', port=8080)
