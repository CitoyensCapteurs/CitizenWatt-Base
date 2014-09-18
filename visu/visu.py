#!/usr/bin/env python3

from random import random
from math import sin

from bottle import abort, Bottle, SimpleTemplate, static_file, view
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, DateTime, event, Float, ForeignKey, Integer, Text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

## Constants ##
MAX_POWER = 3500
## ##

n_values = 0
def generate_value():
    """Generate values for debug purpose"""
    global n_values
    n_values += 1
    return sin(n_values / 10.0) ** 2 * MAX_POWER
    return random() * MAX_POWER

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

app = Bottle()
plugin = sqlalchemy.Plugin(
    engine,
    Base.metadata,
    keyword='db',
    create=True,
    commit=True,
    use_kwargs=False
)
app.install(plugin)
SimpleTemplate.defaults['get_url'] = app.get_url


class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    type = Column(Text)
    measures = relationship('Measures', passive_deletes=True)


class Measures(Base):
    __tablename__ = 'measures'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id', ondelete='CASCADE'))
    value = Column(Float)
    timestamp = Column(DateTime)

# API
@app.route('/api/sensors')
def api_sensors(db):
    sensors = db.query(Sensor).all()
    if sensors:
        print(sensors)
    else:
        abort(404, 'No sensors found.')

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
    if time1 < 0:
        abort(404, 'Invalid timestamp.')

    data = [{'power': generate_value()} for i in range(time1)]
    return {'data': data}

@app.route('/api/<sensor:int>/get/by_time/<time1:int>/<time2:int>')
def api_get_times(sensor, time1, time2):
    if time1 < 0 or time2 > 0:
        abort(404, 'Invalid timestamps.')

    data = [{'power': generate_value()} for i in range(time2)]
    return {'data': data}

@app.route('/api/energy_providers')
def api_energy_providers(db):
    # TODO
    #providers = db.query(Provider).all()
    #if sensors:
    #    print(sensors)
    #else:
    #    abort(404, 'No sensors found.')
    abort(501, 'Not implemented.')

@app.route('/api/<energy_provider:int>/watt_euros/<consumption:int>')
def api_energy_providers(energy_provider, consumption, db):
    # TODO
    #providers = db.query(Provider).all()
    #if sensors:
    #    print(sensors)
    #else:
    #    abort(404, 'No sensors found.')
    abort(501, 'Not implemented.')

# Routes

@app.route('/static/<filename:path>', name='static')
def static(filename):
    return static_file(filename, root='static')

@app.route('/', name='index')
@view('index')
def index():
    return {'API_URL': app.get_url('index')}

@app.route('/conso', name='conso')
@view('conso')
def visu():
    return {'API_URL': app.get_url('index')}

run(app, host='0.0.0.0', port=8080, debug=True)
