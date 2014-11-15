#!/usr/bin/env python3
import datetime
import hashlib
import json
import os
import requests
import subprocess
import re


from libcitizenwatt import cache
from libcitizenwatt import database
from libcitizenwatt import tools
from bottle import abort, Bottle, SimpleTemplate, static_file
from bottle import redirect, request, run
from bottle.ext import sqlalchemy
from bottlesession import PickleSession, authenticator
from libcitizenwatt.config import Config
from sqlalchemy import asc, create_engine, desc
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from xmlrpc.client import ServerProxy


# ===============
# Initializations
# ===============
config = Config()
database_url = (config.get("database_type") + "://" + config.get("username") +
                ":" + config.get("password") + "@" + config.get("host") + "/" +
                config.get("database"))
engine = create_engine(database_url, echo=config.get("debug"))

app = Bottle()
plugin = sqlalchemy.Plugin(
    engine,
    database.Base.metadata,
    keyword='db',
    create=True,
    commit=True,
    use_kwargs=False
)
app.install(plugin)

session_manager = PickleSession()
valid_user = authenticator(session_manager, login_url='/login')


# =========
# Functions
# =========
def get_rate_type(db):
    """Returns "day" or "night" according to current time"""
    if not tools.is_day_night_rate(db):
        return "none"
    session = session_manager.get_session()
    user = db.query(database.User).filter_by(login=session.get("login")).first()
    now = datetime.datetime.now()
    now = 3600 * now.hour + 60 * now.minute
    if user is None:
        return None
    elif user.end_night_rate > user.start_night_rate:
        if now > user.start_night_rate and now < user.end_night_rate:
            return "night"
        else:
            return "day"
    else:
        if now > user.start_night_rate or now < user.end_night_rate:
            return "night"
        else:
            return "day"


def api_auth(post, db):
    """
    Handles login authentication for API.

    Returns True if login is ok, False otherwise.
    """
    login = post.get("login")
    user = db.query(database.User).filter_by(login=login).first()

    password = (config.get("salt") +
                hashlib.sha256(post.get("password", "").encode('utf-8'))
                .hexdigest())
    if user and user.password == password:
        return True
    else:
        return False


# ===
# API
# ===

# Sensors management
# ==================
@app.route("/api/sensors",
           apply=valid_user())
def api_sensors(db):
    """Returns a list of all the available sensors.

    If no sensors are found, returns null"""
    sensors = db.query(database.Sensor).all()
    if sensors:
        sensors = [{"id": sensor.id,
                    "name": sensor.name,
                    "type": sensor.type.name,
                    "type_id": sensor.type_id} for sensor in sensors]
    else:
        sensors = None

    return {"data": sensors}


@app.route("/api/sensors",
           method="post")
def api_sensors_post(db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_sensors(db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/sensors/<id:int>",
           apply=valid_user())
def api_sensor(id, db):
    """Returns the sensor with id <id>.

    If no matching sensor is found, returns null"""
    sensor = db.query(database.Sensor).filter_by(id=id).first()
    if sensor:
        sensor = {"id": sensor.id,
                  "name": sensor.name,
                  "type": sensor.type.name,
                  "type_id": sensor.type_id}
    else:
        sensor = None

    return {"data": sensor}


@app.route("/api/sensors/<id:int>",
           method="post")
def api_sensor_post(id, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_sensor(id, db)
    else:
        abort(403, "Access forbidden")


# Measure types
# =============
@app.route("/api/types",
           apply=valid_user())
def api_types(db):
    """Returns a list of all the available measure types.

    If no types are found, returns null"""
    types = db.query(database.MeasureType).all()
    if types:
        types = [{"id": mtype.id,
                  "name": mtype.name} for mtype in types]
    else:
        types = None

    return {"data": types}


@app.route("/api/types",
           method="post")
def api_types_post(db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_types(db)
    else:
        abort(403, "Access forbidden")


# Time
# ====
@app.route("/api/time",
           apply=valid_user())
def api_time(db):
    """
    Returns current timestamp on the server side."""
    now = datetime.datetime.now()

    return {"data": now.timestamp()}


@app.route("/api/time",
           method="post")
def api_time_post(db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_time(db)
    else:
        abort(403, "Access forbidden")


# Get measures
# ============
@app.route("/api/<sensor:int>/get/watts/by_id/<id1:int>",
           apply=valid_user())
def api_get_id(sensor, id1, db):
    """
    Returns measure with id <id1> associated to sensor <sensor>, in watts.

    If <id1> < 0, counts from the last measure, as in Python lists.

    If no matching data is found, returns null.
    """
    if id1 >= 0:
        data = (db.query(database.Measure)
                .filter_by(sensor_id=sensor, id=id1)
                .first())
    else:
        data = (db.query(database.Measure)
                .filter_by(sensor_id=sensor)
                .order_by(desc(database.Measure.timestamp))
                .slice(-id1, -id1)
                .first())

    if not data:
        data = None
    else:
        data = tools.to_dict(data)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/watts/by_id/<id1:int>",
           method="post")
def api_get_id_post(sensor, id1, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_get_id(sensor, id1, db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>/<step:int>",
           apply=valid_user())
def api_get_ids_step(sensor, watt_euros, id1, id2, step, db,
                     timestep=config.get("default_timestep")):
    """
    Returns all the measures of sensor `sensor` between ids `id1`
    and `id2`, grouped by step, as a list of the number of steps element.
    Each item is null if no matching measures are found.

    * If `watts_euros` is watts, returns the mean power for each group.
    * If `watt_euros` is kwatthours, returns the total energy for each group.
    * If `watt_euros` is euros, returns the cost of each group.

    Returns measure in ASC order of timestamp.

    Returns null if no measures were found.
    """
    if id1 * id2 < 0 or id2 <= id1 or step <= 0:
        abort(400, "Invalid parameters")
    elif (id2 - id1) > config.get("max_returned_values"):
        abort(403,
              "Too many values to return. " +
              "(Maximum is set to %d)" % config.get("max_returned_values"))

    try:
        data = cache.do_cache_group_id(sensor,
                                       watt_euros,
                                       id1,
                                       id2,
                                       step,
                                       db,
                                       timestep)
    except ValueError:
        abort(400, "Wrong parameters id1 and id2.")

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>/<step:int>",
           method="post")
def api_get_ids_step_post(sensor, watt_euros, id1, id2, step, db,
                          timestep=config.get("default_timestep")):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_get_ids_step(sensor, watt_euros, id1, id2, step, db, timestep)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<sensor:int>/get/watts/by_time/<time1:float>",
           apply=valid_user())
def api_get_time(sensor, time1, db):
    """
    Returns measure at timestamp <time1> for sensor <sensor>, in watts.

    Returns null if no measure is found.
    """
    if time1 < 0:
        abort(400, "Invalid timestamp.")

    data = (db.query(database.Measure)
            .filter_by(sensor_id=sensor,
                       timestamp=time1)
            .first())
    if not data:
        data = None
    else:
        data = tools.to_dict(data)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/watts/by_time/<time1:float>",
           method="post")
def api_get_time_post(sensor, time1, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_get_time(sensor, time1, db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>",
           apply=valid_user())
def api_get_times(sensor, watt_euros, time1, time2, db):
    """
    Returns measures between timestamps <time1> and <time2>
    from sensor <sensor> in watts or euros.

    * If `watts_euros` is watts, returns the list of measures.
    * If `watt_euros` is kwatthours, returns the total energy for all the
    measures (dict).
    * If `watt_euros` is euros, returns the cost of all the measures (dict).

    Returns measure in ASC order of timestamp.

    Returns null if no matching measures are found.
    """
    if time1 < 0 or time2 < time1:
        abort(400, "Invalid timestamps.")

    data = cache.do_cache_times(sensor, watt_euros, time1, time2, db)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>",
           method="post")
def api_get_times_post(sensor, watt_euros, time1, time2, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_get_times(sensor, watt_euros, time1, time2, db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>/<step:float>",
           apply=valid_user())
def api_get_times_step(sensor, watt_euros, time1, time2, step, db):
    """
    Returns all the measures of sensor `sensor` between timestamps `time1`
    and `time2`, grouped by step, as a list of the number of steps element.
    Each item is null if no matching measures are found.

    * If `watts_euros` is watts, returns the mean power for each group.
    * If `watt_euros` is kwatthours, returns the total energy for each group.
    * If `watt_euros` is euros, returns the cost of each group.

    Returns measure in ASC order of timestamp.
    """
    if time1 < 0 or time2 < 0 or step <= 0:
        abort(400, "Invalid parameters")

    data = cache.do_cache_group_timestamp(sensor,
                                          watt_euros,
                                          time1,
                                          time2,
                                          step,
                                          db)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>/<step:float>",
           method="post")
def api_get_times_step_post(sensor, watt_euros, time1, time2, step, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_get_times_step(sensor, watt_euros, time1, time2, step, db)
    else:
        abort(403, "Access forbidden")


# Delete measures
# ===============
@app.route("/api/<sensor:int>/delete/by_id/<id1:int>",
           apply=valid_user())
def api_delete_id(sensor, id1, db):
    """
    Deletes measure with id <id1> associated to sensor <sensor>.

    If <id1> < 0, counts from the last measure, as in Python lists.

    If no matching data is found, returns null. Else, returns the number of
    deleted measures (1).
    """
    if id1 >= 0:
        data = (db.query(database.Measure)
                .filter_by(sensor_id=sensor, id=id1)
                .delete())
    else:
        data = (db.query(database.Measure)
                .filter_by(sensor_id=sensor)
                .order_by(desc(database.Measure.timestamp))
                .slice(-id1, -id1)
                .first())
        data = db.delete(data)

    if data == 0:
        data = None

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/delete/by_id/<id1:int>",
           method="post")
def api_delete_id_post(sensor, id1, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_delete_id(sensor, id1, db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<sensor:int>/delete/by_id/<id1:int>/<id2:int>",
           apply=valid_user())
def api_delete_ids(sensor, id1, id2, db):
    """
    Deletes measures between ids <id1> and <id2>
    from sensor <sensor>.

    Returns null if no matching measures are found. Else, returns the number of
    deleted measures.
    """
    if id2 < id1 or id2 * id1 < 0:
        abort(400, "Invalid parameters")
    else:
        if id1 >= 0 and id2 >= 0 and id2 >= id1:
            data = (db.query(database.Measure)
                    .filter(database.Measure.sensor_id == sensor,
                            database.Measure.id >= id1,
                            database.Measure.id < id2)
                    .delete())
        elif id1 <= 0 and id2 <= 0 and id2 >= id1:
            to_delete = (db.query(database.Measure)
                         .filter_by(sensor_id=sensor)
                         .order_by(desc(database.Measure.timestamp))
                         .slice(-id2, -id1)
                         .all())
            if to_delete:
                data = len(to_delete)
                for delete in to_delete:
                    db.delete(delete)
            else:
                data = 0

    if data == 0:
        data = None

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/delete/by_id/<id1:int>/<id2:int>",
           method="post")
def api_delete_ids_post(sensor, id1, id2, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_delete_ids(sensor, id1, id2, db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<sensor:int>/delete/by_time/<time1:float>",
           apply=valid_user())
def api_delete_time(sensor, time1, db):
    """
    Deletes measure at timestamp <time1> for sensor <sensor>.

    Returns null if no measure is found. Else, returns the number of deleted
    measures (1).
    """
    if time1 < 0:
        abort(400, "Invalid timestamp.")

    data = (db.query(database.Measure)
            .filter_by(sensor_id=sensor,
                       timestamp=time1)
            .delete())
    if data == 0:
        data = None

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/delete/by_time/<time1:float>",
           method="post")
def api_delete_time_post(sensor, time1, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_delete_time(sensor, time1, db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<sensor:int>/delete/by_time/<time1:float>/<time2:float>",
           apply=valid_user())
def api_delete_times(sensor, time1, time2, db):
    """
    Deletes measures between timestamps <time1> and <time2>
    from sensor <sensor>.

    Returns null if no matching measures are found. Else, returns the number of
    deleted measures.
    """
    if time1 < 0 or time2 < time1:
        abort(400, "Invalid timestamps.")

    to_delete = (db.query(database.Measure)
                 .filter(database.Measure.sensor_id == sensor,
                         database.Measure.timestamp >= time1,
                         database.Measure.timestamp < time2)
                 .order_by(asc(database.Measure.timestamp))
                 .all())
    if to_delete:
        data = len(to_delete)
        for delete in to_delete:
            db.delete(delete)
    else:
        data = 0

    if data == 0:
        data = None

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/delete/by_time/<time1:float>/<time2:float>",
           method="post")
def api_delete_times_post(sensor, time1, time2, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_delete_times(sensor, time1, time2, db)
    else:
        abort(403, "Access forbidden")


# Insert measures
# ===============
@app.route("/api/<sensor:int>/insert/<value:float>/<timestamp:int>/<night_rate:int>",
           apply=valid_user())
def api_insert_measure(sensor, value, timestamp, night_rate, db):
    """
    Insert a measure with:
        * Timestamp `<timestamp>`
        * Value `<value>`
        * Tariff "day" if `<night_rate> == 0`, "night" otherwise.

    Returns `True` if successful. `False` otherwise.
    """
    if timestamp < 0:
        abort(400, "Invalid timestamp.")

    if night_rate != 0:
        night_rate = 1

    measure = database.Measure(value=value,
                               timestamp=timestamp,
                               night_rate=night_rate,
                               sensor_id=sensor)
    db.add(measure)
    try:
        db.commit()
        data = True
    except IntegrityError:
        data = False
        db.rollback()

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/insert/<value:float>/<timestamp:int>/<night_rate:int>",
           method="post")
def api_insert_measure_post(sensor, value, timestamp, night_rate, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_insert_measure(sensor, value, timestamp, night_rate, db)
    else:
        abort(403, "Access forbidden")


# Energy providers
# ================
@app.route("/api/energy_providers",
           apply=valid_user())
def api_energy_providers(db):
    """Returns all the available energy providers or null if none found."""
    providers = db.query(database.Provider).all()
    if not providers:
        providers = None
    else:
        providers = tools.to_dict(providers)
        for provider in providers:
            if provider["day_slope_watt_euros"] != provider["night_slope_watt_euros"]:
                session = session_manager.get_session()
                user = db.query(database.User).filter_by(login=session["login"]).first()
                start_night_rate = ("%02d" % (user.start_night_rate // 3600) + ":" +
                                    "%02d" % ((user.start_night_rate % 3600) // 60))
                end_night_rate = ("%02d" % (user.end_night_rate // 3600) + ":" +
                                  "%02d" % ((user.end_night_rate % 3600) // 60))
                provider["start_night_rate"] = start_night_rate
                provider["end_night_rate"] = end_night_rate

    return {"data": providers}


@app.route("/api/energy_providers",
           method="post")
def api_energy_providers_post(db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_energy_providers(db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/energy_providers/<id:re:current|\d*>",
           apply=valid_user())
def api_specific_energy_providers(id, db):
    """
    Returns the current energy provider,
    or the specified energy provider.
    """
    if id == "current":
        provider = (db.query(database.Provider)
                    .filter_by(current=1)
                    .first())
    else:
        try:
            id = int(id)
        except ValueError:
            abort(400, "Invalid parameter.")

        provider = (db.query(database.Provider)
                    .filter_by(id=id)
                    .first())

    if not provider:
        provider = None
    else:
        provider = tools.to_dict(provider)
        if provider["day_slope_watt_euros"] != provider["night_slope_watt_euros"]:
            session = session_manager.get_session()
            user = db.query(database.User).filter_by(login=session["login"]).first()
            start_night_rate = ("%02d" % (user.start_night_rate // 3600) + ":" +
                                "%02d" % ((user.start_night_rate % 3600) // 60))
            end_night_rate = ("%02d" % (user.end_night_rate // 3600) + ":" +
                              "%02d" % ((user.end_night_rate % 3600) // 60))
            provider["start_night_rate"] = start_night_rate
            provider["end_night_rate"] = end_night_rate

    return {"data": provider}


@app.route("/api/energy_providers/<id:re:current|\d*>",
           method="post")
def api_specific_energy_providers_post(id, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_specific_energy_providers(id, db)
    else:
        abort(403, "Access forbidden")


@app.route("/api/<energy_provider:re:current|\d>/watt_to_euros/<tariff:re:night|day>/<consumption:float>",
           apply=valid_user())
def api_watt_euros(energy_provider, tariff, consumption, db):
    """
    Returns the cost in € associated with a certain consumption, in kWh.

    One should specify the tariff (night or day) and the id of the
    energy_provider.

    Returns null if no valid result to return.
    """
    # Consumption should be in kWh !!!

    if energy_provider == "current":
        energy_provider = 0

    try:
        int(energy_provider)
    except ValueError:
        abort(400, "Wrong parameter energy_provider.")

    data = tools.watt_euros(energy_provider, tariff, consumption, db)
    return {"data": data}


@app.route("/api/<energy_provider:re:current|\d>/watt_to_euros/<tariff:re:night|day>/<consumption:float>",
           method="post")
def api_watt_euros_post(energy_provider, tariff, consumption, db):
    """Same as above, but with POST auth"""
    if api_auth(request.POST, db):
        return api_watt_euros(energy_provider, tariff, consumption, db)
    else:
        abort(403, "Access forbidden")


# ======
# Routes
# ======
@app.route("/static/<filename:path>",
           name="static")
def static(filename):
    """Routes static files"""
    return static_file(filename, root="static")


@app.route('/',
           name="index",
           template="index",
           apply=valid_user())
def index():
    """Index view"""
    return {}


@app.route("/conso",
           name="conso",
           template="conso",
           apply=valid_user())
def conso(db):
    """Conso view"""
    provider = db.query(database.Provider).filter_by(current=1).first()
    return {"provider": provider.name}


@app.route("/reset_timer/<sensor:int>", apply=valid_user())
def reset_timer(sensor, db):
    """Reset the timer for specified sensor"""
    db.query(database.Sensor).filter_by(id=sensor).update({"last_timer": 0})
    redirect("/settings")


@app.route("/toggle_ssh", apply=valid_user())
def toggle_ssh(state, db):
    """Enable or disable SSH service"""
    tools.toggle_ssh()
    redirect("/settings")


@app.route("/settings",
           name="settings",
           template="settings",
           apply=valid_user())
def settings(db):
    """Settings view"""
    sensors = db.query(database.Sensor).all()
    if sensors:
        sensors = [{"id": sensor.id,
                    "name": sensor.name,
                    "type": sensor.type.name,
                    "type_id": sensor.type_id,
                    "aes_key": sensor.aes_key,
                    "base_address": hex(int(tools.get_base_address())).upper() + "LL"}
                   for sensor in sensors]
    else:
        sensors = []

    sensor_cw = [sensor for sensor in sensors if sensor["name"] ==
                 "CitizenWatt"][0]

    providers = tools.update_providers(config.get("url_energy_providers"),
                                       True,
                                       db)

    session = session_manager.get_session()
    user = db.query(database.User).filter_by(login=session["login"]).first()
    start_night_rate = ("%02d" % (user.start_night_rate // 3600) + ":" +
                        "%02d" % ((user.start_night_rate % 3600) // 60))
    end_night_rate = ("%02d" % (user.end_night_rate // 3600) + ":" +
                      "%02d" % ((user.end_night_rate % 3600) // 60))

    for p in providers:
        p['is_day_night_rate'] = tools.is_day_night_rate(db, p)

    return {"sensors": sensors,
            "providers": providers,
            "start_night_rate": start_night_rate,
            "end_night_rate": end_night_rate,
            "base_address": hex(int(tools.get_base_address())).upper() + "LL",
            "aes_key": '-'.join([str(i) for i in
                                 json.loads(sensor_cw["aes_key"])]),
            "nrf_power": tools.get_nrf_power(),
            "ssh_status": tools.ssh_status()}


@app.route("/settings",
           name="settings",
           template="settings",
           apply=valid_user(),
           method="post")
def settings_post(db):
    """Settings view with POST data"""
    error = None

    password = request.forms.get("password").strip()
    password_confirm = request.forms.get("password_confirm")

    if password:
        if password == password_confirm:
            password = (config.get("salt") +
                        hashlib.sha256(password.encode('utf-8')).hexdigest())
            session = session_manager.get_session()
            (db.query(database.User)
             .filter_by(login=session["login"])
             .update({"password": password},
                     synchronize_session=False))
        else:
            error = {"title": "Les mots de passe ne sont pas identiques.",
                     "content": ("Les deux mots de passe doient " +
                                 "être identiques.")}
            settings_json = settings(db)
            settings_json.update({"err": error})
            return settings_json

    raw_provider = request.forms.get("provider")
    provider = (db.query(database.Provider)
                .filter_by(name=raw_provider)
                .first())
    if not provider:
        error = {"title": "Fournisseur d'électricité invalide.",
                 "content": "Le fournisseur choisi n'existe pas."}
        settings_json = settings(db)
        settings_json.update({"err": error})
        return settings_json
    db.query(database.Provider).update({"current": 0})
    (db.query(database.Provider)
     .filter_by(name=raw_provider)
     .update({"current": 1}))

    raw_start_night_rate = request.forms.get("start_night_rate")
    raw_end_night_rate = request.forms.get("end_night_rate")

    raw_base_address = request.forms.get("base_address")
    raw_aes_key = request.forms.get("aes_key")

    raw_nrf_power = request.forms.get("nrf_power")

    try:
        base_address_int = int(raw_base_address.strip("L"), 16)
        base_address = str(hex(base_address_int)).upper() + "LL"
    except ValueError:
        error = {"title": "Format invalide",
                 "content": ("L'adresse de la base entrée est invalide.")}
        settings_json = settings(db)
        settings_json.update({"err": error})
        return settings_json

    if base_address != tools.get_base_address():
        tools.update_base_address(base_address_int)

    try:
        aes_key = [int(i.strip()) for i in raw_aes_key.split("-")]
        if len(aes_key) != 16:
            raise ValueError
    except ValueError:
        error = {"title": "Format invalide",
                 "content": ("La clé AES doit être constituée de 16 " +
                             "chiffres entre 0 et 255, séparés " +
                             "par des tirets.")}
        settings_json = settings(db)
        settings_json.update({"err": error})
        return settings_json

    try:
        assert(raw_nrf_power in tools.nrf_power_dict)
    except AssertionError:
        error = {"title": "Format invalide",
                 "content": ("Les deux mots de passe doient " +
                             "être identiques.")}
        settings_json = settings(db)
        settings_json.update({"err": error})
        return settings_json

    if raw_nrf_power != tools.get_nrf_power():
        tools.update_nrf_power(raw_nrf_power)

    (db.query(database.Sensor)
     .filter_by(name="CitizenWatt")
     .update({"aes_key": json.dumps(aes_key)}))
    db.commit()

    try:
        if tools.is_day_night_rate(db, provider):
            start_night_rate = 0
        else:
            start_night_rate = raw_start_night_rate.split(":")
            assert(len(start_night_rate) == 2)
            start_night_rate = [int(i) for i in start_night_rate]
            assert(start_night_rate[0] >= 0 and start_night_rate[0] <= 23)
            assert(start_night_rate[1] >= 0 and start_night_rate[1] <= 59)
            start_night_rate = 3600 * start_night_rate[0] + 60*start_night_rate[1]
    except (AssertionError, ValueError):
        error = {"title": "Format invalide",
                 "content": ("La date de début d'heures " +
                             "creuses doit être au format hh:mm.")}
        settings_json = settings(db)
        settings_json.update({"err": error})
        return settings_json
    try:
        if tools.is_day_night_rate(db, provider):
            end_night_rate = 0
        else:
            end_night_rate = raw_end_night_rate.split(":")
            assert(len(end_night_rate) == 2)
            end_night_rate = [int(i) for i in end_night_rate]
            assert(end_night_rate[0] >= 0 and end_night_rate[0] <= 23)
            assert(end_night_rate[1] >= 0 and end_night_rate[1] <= 59)
            end_night_rate = 3600 * end_night_rate[0] + 60*end_night_rate[1]
    except (AssertionError, ValueError):
        error = {"title": "Format invalide",
                 "content": ("La date de fin d'heures " +
                             "creuses doit être au format hh:mm.")}
        settings_json = settings(db)
        settings_json.update({"err": error})
        return settings_json

    session = session_manager.get_session()
    (db.query(database.User)
     .filter_by(login=session["login"])
     .update({"start_night_rate": start_night_rate,
              "end_night_rate": end_night_rate}))

    redirect("/settings")


@app.route("/update", name="update")
def update():
    """Handles updating"""
    subprocess.Popen([os.path.dirname(os.path.realpath(__file__)) +
                      "/updater.sh"])
    redirect("/settings")


@app.route("/community",
           name="community",
           template="community")
def store():
    """Community view"""
    return {}


@app.route("/help",
           name="help",
           template="help")
def help():
    """Help view"""
    return {}


@app.route("/faq",
           name="faq",
           template="faq")
def faq():
    """Show the FAQ from the wiki"""
    try:
        wiki = ServerProxy('http://wiki.citizenwatt.paris/lib/exe/xmlrpc.php')
        text = wiki.wiki.getPage('les_questions_que_vous_vous_posez_tous')
        parsed = re.split('====== (.*) ======', text)
        l = [c.strip() for c in parsed if c.strip() != '']
        faq = list(zip(l[::2], l[1::2]))
    except requests.exceptions.RequestException:
        faq = []
    return {"faq": faq}


@app.route("/login",
           name="login",
           template="login")
def login(db):
    """Login view"""
    try:
        if not db.query(database.User).all():
            redirect("/install")
    except ProgrammingError:
        redirect("/install")
    session = session_manager.get_session()
    if session['valid'] is True:
        redirect('/')
    else:
        return {"login": ''}


@app.route("/login",
           name="login",
           template="login",
           method="post")
def login_post(db):
    """Login view with POST data"""
    login = request.forms.get("login")
    user = db.query(database.User).filter_by(login=login).first()
    session = session_manager.get_session()
    session['valid'] = False
    session_manager.save(session)

    password = (config.get("salt") +
                hashlib.sha256(request.forms.get("password")
                               .encode('utf-8')).hexdigest())
    if user and user.password == password:
        session['valid'] = True
        session['login'] = login
        session['is_admin'] = user.is_admin
        session_manager.save(session)
        redirect('/')
    else:
        return {
            "login": login,
            "err": {
                "title": "Identifiants incorrects.",
                "content": ("Aucun utilisateur n'est enregistré à ce nom."
                            if user else "Mot de passe erroné.")
            }
        }


@app.route("/logout",
           name="logout")
def logout():
    """Logout"""
    session = session_manager.get_session()
    session['valid'] = False
    del(session['login'])
    del(session['is_admin'])
    session_manager.save(session)
    redirect('/')


@app.route("/install",
           name="install",
           template="install")
def install(db):
    """Install view (first run)"""
    if db.query(database.User).all():
        redirect('/')

    db.query(database.MeasureType).delete()
    db.query(database.Provider).delete()
    db.query(database.Sensor).delete()

    electricity_type = database.MeasureType(name="Électricité")
    db.add(electricity_type)
    db.flush()

    providers = tools.update_providers(config.get("url_energy_providers"),
                                       True,
                                       db)

    for p in providers:
        p['is_day_night_rate'] = tools.is_day_night_rate(db, p)

    sensor = database.Sensor(name="CitizenWatt",
                             type_id=electricity_type.id,
                             last_timer=0)
    db.add(sensor)

    return {"login": '',
            "providers": providers,
            "start_night_rate": '',
            "end_night_rate": '',
            "base_address": '',
            "aes_key": '',
            "nrf_power": 'high'}


@app.route("/install",
           name="install",
           template="install",
           method="post")
def install_post(db):
    """Install view with POST data"""
    error = None
    try:
        if db.query(database.User).all():
            redirect('/')
    except OperationalError:
        error = {"title": "Connexion à la base de données impossible",
                 "content": ("Impossible d'établir une connexion avec la " +
                             "base de données.")}
        install_json = install(db)
        install_json.update({"err": error})
        return install_json

    login = request.forms.get("login").strip()
    password = request.forms.get("password")
    password_confirm = request.forms.get("password_confirm")
    raw_start_night_rate = request.forms.get("start_night_rate")
    raw_end_night_rate = request.forms.get("end_night_rate")
    raw_base_address = request.forms.get("base_address")
    raw_aes_key = request.forms.get("aes_key")
    raw_nrf_power = request.forms.get("nrf_power")
    raw_provider = request.forms.get("provider")

    ret = {"login": login,
           "providers": tools.update_providers(config.get("url_energy_providers"),
                                               False,
                                               db),
           "start_night_rate": raw_start_night_rate,
           "end_night_rate": raw_end_night_rate,
           "base_address": raw_base_address,
           "aes_key": raw_aes_key,
           "nrf_power": raw_nrf_power}

    try:
        base_address_int = int(raw_base_address.strip("L"), 16)
    except ValueError:
        error = {"title": "Format invalide",
                 "content": ("L'adresse de la base entrée est invalide.")}
        ret.update({"err": error})
        return ret
    tools.update_base_address(base_address_int)
    try:
        aes_key = [int(i.strip()) for i in raw_aes_key.split("-")]
        if len(aes_key) != 16:
            raise ValueError
    except ValueError:
        error = {"title": "Format invalide",
                 "content": ("La clé AES doit être constituée de 16 " +
                             "chiffres entre 0 et 255, séparés " +
                             "par des tirets.")}
        ret.update({"err": error})
        return ret

    try:
        assert(raw_nrf_power in tools.nrf_power_dict)
    except AssertionError:
        error = {"title": "Format invalide",
                 "content": ("La puissance indiquée pour le nRF est " +
                             "invalide. ")}
        ret.update({"err": error})
        return ret
    tools.update_nrf_power(raw_nrf_power)

    (db.query(database.Sensor)
     .filter_by(name="CitizenWatt")
     .update({"aes_key": json.dumps(aes_key)}))
    db.commit()

    provider = (db.query(database.Provider)
                .filter_by(name=raw_provider)
                .first())
    if not provider:
        error = {"title": "Fournisseur d'électricité invalide.",
                 "content": "Le fournisseur choisi n'existe pas."}
        ret.update({"err": error})
        return ret

    try:
        if tools.is_day_night_rate(db, provider):
            start_night_rate = 0
        else:
            start_night_rate = raw_start_night_rate.split(":")
            assert(len(start_night_rate) == 2)
            start_night_rate = [int(i) for i in start_night_rate]
            assert(start_night_rate[0] >= 0 and start_night_rate[0] <= 23)
            assert(start_night_rate[1] >= 0 and start_night_rate[1] <= 59)
            start_night_rate = 3600 * start_night_rate[0] + 60*start_night_rate[1]
    except (AssertionError, ValueError):
        error = {"title": "Format invalide",
                 "content": ("La date de début d'heures creuses " +
                             "doit être au format hh:mm.")}
        ret.update({"err": error})
        return ret

    try:
        if tools.is_day_night_rate(db, provider):
            end_night_rate = 0
        else:
            end_night_rate = raw_end_night_rate.split(":")
            assert(len(end_night_rate) == 2)
            end_night_rate = [int(i) for i in end_night_rate]
            assert(end_night_rate[0] >= 0 and end_night_rate[0] <= 23)
            assert(end_night_rate[1] >= 0 and end_night_rate[1] <= 59)
            end_night_rate = 3600 * end_night_rate[0] + 60*end_night_rate[1]
    except (AssertionError, ValueError):
        error = {"title": "Format invalide",
                 "content": ("La date de fin d'heures creuses " +
                             "doit être au format hh:mm.")}
        ret.update({"err": error})
        return ret

    if login and password and password == password_confirm:
        password = (config.get("salt") +
                    hashlib.sha256(password.encode('utf-8')).hexdigest())
        admin = database.User(login=login,
                              password=password,
                              is_admin=1,
                              start_night_rate=start_night_rate,
                              end_night_rate=end_night_rate)
        db.add(admin)

        db.query(database.Provider).update({"current": 0})
        (db.query(database.Provider)
         .filter_by(name=raw_provider)
         .update({"current": 1}))

        session = session_manager.get_session()
        session['valid'] = True
        session['login'] = login
        session['is_admin'] = 1
        session_manager.save(session)

        redirect('/')
    else:
        ret.update({"err": {"title": "Champs obligatoires manquants",
                            "content": ("Vous devez renseigner tous " +
                                        "les champs obligatoires.")}})
        return ret


if __name__ == '__main__':
    SimpleTemplate.defaults["get_url"] = app.get_url
    SimpleTemplate.defaults["API_URL"] = app.get_url("index")
    SimpleTemplate.defaults["valid_session"] = lambda: session_manager.get_session()['valid']
    run(app, host="0.0.0.0", port=config.get("port"), debug=config.get("debug"),
        reloader=config.get("autoreload"), server="cherrypy")
