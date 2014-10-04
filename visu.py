#!/usr/bin/env python3
import datetime
import hashlib
import requests


from libcitizenwatt import database
from libcitizenwatt import tools
from bottle import abort, Bottle, SimpleTemplate, static_file
from bottle import redirect, request, run
from bottle.ext import sqlalchemy
from bottlesession import PickleSession, authenticator
from libcitizenwatt.config import Config
from sqlalchemy import create_engine, desc
from sqlalchemy.exc import OperationalError


# =========
# Functions
# =========
def get_rate_type(db):
    """Returns "day" or "night" according to current time
    """
    session = session_manager.get_session()
    user = db.query(database.User).filter_by(login=session["login"]).first()
    now = datetime.datetime.now()
    now = 3600 * now.hour + 60 * now.minute
    if user is None:
        return -1
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


def update_providers(fetch, db):
    """Updates the available providers. Simply returns them without updating if
    fetch is False.
    """
    try:
        assert(fetch)
        providers = requests.get(config.get("url_energy_providers")).json()
    except (requests.ConnectionError, AssertionError):
        providers = db.query(database.Provider).all()
        if not providers:
            providers = []
        return tools.to_dict(providers)

    old_current = db.query(database.Provider).filter_by(current=1).first()
    db.query(database.Provider).delete()

    for provider in providers:
        type_id = (db.query(database.MeasureType)
                   .filter_by(name=provider["type_name"])
                   .first())
        if not type_id:
            type_db = database.MeasureType(name=provider["type_name"])
            db.add(type_db)
            db.flush()
            type_id = database.MeasureType(name=provider["type_name"]).first()

        provider_db = database.Provider(name=provider["name"],
                                        day_constant_watt_euros=provider["day_constant_watt_euros"],
                                        day_slope_watt_euros=provider["day_slope_watt_euros"],
                                        night_constant_watt_euros=provider["night_constant_watt_euros"],
                                        night_slope_watt_euros=provider["night_slope_watt_euros"],
                                        type_id=type_id.id,
                                        current=(1 if old_current and old_current.name == provider["name"] else 0))
        db.add(provider_db)
    return providers


# ===============
# Initializations
# ===============
config = Config()
database_url = ("mysql+pymysql://" + config.get("username") + ":" +
                config.get("password") + "@" + config.get("host") + "/" +
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


# ===
# API
# ===
@app.route("/api/sensors",
           apply=valid_user())
def api_sensors(db):
    """Returns a list of all the available sensors."""
    sensors = db.query(database.Sensor).all()
    if sensors:
        sensors = [{"id": sensor.id,
                    "name": sensor.name,
                    "type": sensor.type.name,
                    "type_id": sensor.type_id} for sensor in sensors]
    else:
        sensors = []

    return {"data": sensors}


@app.route("/api/sensors/<id:int>",
           apply=valid_user())
def api_sensor(id, db):
    """Returns the sensor with id <id>."""
    sensor = db.query(database.Sensor).filter_by(id=id).first()
    if sensor:
        sensor = {"id": sensor.id,
                  "name": sensor.name,
                  "type": sensor.type.name,
                  "type_id": sensor.type_id}
    else:
        sensor = {}

    return {"data": sensor}


@app.route("/api/types",
           apply=valid_user())
def api_types(db):
    """Returns a list of all the available measure types."""
    types = db.query(database.MeasureType).all()
    if types:
        types = [{"id": mtype.id,
                  "name": mtype.name} for mtype in types]
    else:
        types = []

    return {"data": types}


@app.route("/api/time",
           apply=valid_user())
def api_time(db):
    """Returns current timestamp on the server side."""
    now = datetime.datetime.now()

    return {"data": now.timestamp()}


@app.route("/api/<sensor:int>/get/watts/by_id/<id1:int>",
           apply=valid_user())
def api_get_id(sensor, id1, db):
    """Returns measure with id <id1> associated to sensor <sensor>, in watts.
    If <id1> < 0, counts from the last measure, as in Python lists.
    """
    if id1 >= 0:
        data = (db.query(database.Measures)
                .filter_by(sensor_id=sensor, id=id1)
                .first())
    else:
        data = (db.query(database.Measures)
                .filter_by(sensor_id=sensor)
                .order_by(desc(database.Measures.id))
                .slice(id1, id1))

    if not data:
        data = {}
    else:
        data = tools.to_dict(data)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>",
           apply=valid_user())
def api_get_ids(sensor, watt_euros, id1, id2, db):
    """Returns measures between ids <id1> and <id2> from sensor <sensor> in
    watts or euros.

    If id1 and id2 are negative, counts from the end of the measures.

    If kwatthours is asked, returns the total energy of these measures.
    If euros is asked, returns the total cost of these measures.

    Note: Returns measure in ASC order of timestamp.
    """
    if (id2 - id1) > config.get("max_returned_values"):
        abort(403,
              "Too many values to return. " +
              "(Maximum is set to %d)" % config.get("max_returned_values"))

    if id1 >= 0 and id2 >= 0 and id2 >= id1:
        data = (db.query(database.Measures)
                .filter(database.Measures.sensor_id == sensor,
                        database.Measures.id >= id1,
                        database.Measures.id < id2)
                .all())
    elif id1 <= 0 and id2 <= 0 and id2 >= id1:
        data = (db.query(database.Measures)
                .filter_by(sensor_id=sensor)
                .order_by(desc(database.Measures.id))
                .slice(-id2, -id1)
                .all())
        data.reverse()
    else:
        abort(400, "Wrong parameters id1 and id2.")

    if not data:
        data = [] if watt_euros == "watts" else {}
    else:
        data = tools.to_dict(data)
        if watt_euros == 'kwatthours' or watt_euros == 'euros':
            data = tools.energy(data)
            if watt_euros == 'euros':
                if data["night_rate"] != 0:
                    night_rate = api_watt_euros("current",
                                                'night',
                                                data['night_rate'],
                                                db)["data"]
                else:
                    night_rate = 0
                if data["day_rate"] != 0:
                    day_rate = api_watt_euros("current",
                                              'day',
                                              data['day_rate'],
                                              db)["data"]
                else:
                    day_rate = 0
                data = {"value": night_rate + day_rate}
    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>/<step:int>",
           apply=valid_user())
def api_get_ids_step(sensor, watt_euros, id1, id2, step, db, timestep=8):
    steps = [i for i in range(id1, id2 + step, step)]
    data = []

    for s in [steps[i:i+2] for i in range(len(steps)-1)]:
        if watt_euros == "watts":
            tmp = api_get_ids(sensor,
                              "kwatthours",
                              s[0],
                              s[1],
                              db)["data"]
            if len(tmp) > 0:
                tmp = {"value": tmp["value"] / (step * timestep) * 1000 * 3600,
                       "day_rate": tmp["day_rate"] / (step * timestep) * 1000 * 3600,
                       "night_rate": tmp["night_rate"] / (step * timestep) * 1000 * 3600}
            else:
                tmp = {}
        else:
            tmp = api_get_ids(sensor,
                              watt_euros,
                              s[0],
                              s[1],
                              db)["data"]
        data.append(tmp)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/watts/by_time/<time1:float>",
           apply=valid_user())
def api_get_time(sensor, time1, db):
    """Returns measure at timestamp <time1> for sensor <sensor>, in watts."""
    if time1 < 0:
        abort(400, "Invalid timestamp.")

    time1 = datetime.datetime.fromtimestamp(time1)
    data = (db.query(database.Measures)
            .filter_by(sensor_id=sensor,
                       timestamp=time1)
            .first())
    if not data:
        data = {}
    else:
        data = tools.to_dict(data)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>",
           apply=valid_user())
def api_get_times(sensor, watt_euros, time1, time2, db):
    """Returns measures between timestamps <time1> and <time2>
    from sensor <sensor> in watts or euros.

    If kwatthours is asked, returns the total energy of these measures.
    If euros is asked, returns the total cost of these measures.

    Note: Returns measure in ASC order of timestamp.
    """
    if time1 < 0 or time2 < time1:
        abort(400, "Invalid timestamps.")

    time1 = datetime.datetime.fromtimestamp(time1)
    time2 = datetime.datetime.fromtimestamp(time2)
    data = (db.query(database.Measures)
            .filter(database.Measures.sensor_id == sensor,
                    database.Measures.timestamp >= time1,
                    database.Measures.timestamp < time2)
            .all())

    if not data:
        data = [] if watt_euros == "watts" else {}
    else:
        data = tools.to_dict(data)
        if watt_euros == "kwatthours" or watt_euros == "euros":
            data = tools.energy(data)
            if watt_euros == "euros":
                data = {"value": (api_watt_euros("current",
                                                 'night',
                                                 data['night_rate'],
                                                 db)["data"] +
                                  api_watt_euros("current",
                                                 'day',
                                                 data['day_rate'],
                                                 db)["data"])}

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>/<step:float>",
           apply=valid_user())
def api_get_times_step(sensor, watt_euros, time1, time2, step, db):
    time1 = int(time1)
    time2 = int(time2)
    step = int(step)

    steps = [i for i in range(time1, time2 + step, step)]
    data = []

    for s in [steps[i:i+2] for i in range(len(steps)-1)]:
        if watt_euros == "watts":
            tmp = api_get_times(sensor,
                                "kwatthours",
                                s[0],
                                s[1],
                                db)["data"]
            if len(tmp) > 0:
                tmp = {"value": tmp["value"] / step * 1000 * 3600,
                       "day_rate": tmp["day_rate"] / step * 1000 * 3600,
                       "night_rate": tmp["night_rate"] / step * 1000 * 3600}
            else:
                tmp = {}
        else:
            tmp = api_get_times(sensor,
                                watt_euros,
                                s[0],
                                s[1],
                                db)["data"]
        data.append(tmp)

    return {"data": data, "rate": get_rate_type(db)}


@app.route("/api/energy_providers",
           apply=valid_user())
def api_energy_providers(db):
    """Returns all the available energy providers."""
    providers = db.query(database.Provider).all()
    if not providers:
        providers = []
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


@app.route("/api/energy_providers/<id:re:current|\d*>",
           apply=valid_user())
def api_specific_energy_providers(id, db):
    """Returns the current energy provider,
    or the specified energy provider."""
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
        provider = {}
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


@app.route("/api/<energy_provider:re:current|\d>/watt_to_euros/<tariff:re:night|day>/<consumption:float>",
           apply=valid_user())
def api_watt_euros(energy_provider, tariff, consumption, db):
    """Returns the cost associated with a certain amount in watts"""
    # Consumption should be in kWh !!!

    if energy_provider == "current":
        energy_provider = 0

    try:
        int(energy_provider)
    except ValueError:
        abort(400, "Wrong parameter energy_provider.")

    if energy_provider != 0:
        provider = (db.query(database.Provider)
                    .filter_by(id=energy_provider)
                    .first())
    else:
        provider = (db.query(database.Provider)
                    .filter_by(current=1)
                    .first())
    if not provider:
        data = -1
    else:
        if tariff == "night":
            data = provider.night_slope_watt_euros * consumption
        elif tariff == "day":
            data = provider.day_slope_watt_euros * consumption
        else:
            abort(400, "Wrong parameter tariff.")
    return {"data": data}


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
    db.query(database.Sensor).filter_by(id=sensor).update({"last_timer": 0})
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
                    "type_id": sensor.type_id}
                   for sensor in sensors]
    else:
        sensors = []

    providers = update_providers(True, db)

    session = session_manager.get_session()
    user = db.query(database.User).filter_by(login=session["login"]).first()
    start_night_rate = ("%02d" % (user.start_night_rate // 3600) + ":" +
                        "%02d" % ((user.start_night_rate % 3600) // 60))
    end_night_rate = ("%02d" % (user.end_night_rate // 3600) + ":" +
                      "%02d" % ((user.end_night_rate % 3600) // 60))

    return {"sensors": sensors,
            "providers": providers,
            "start_night_rate": start_night_rate,
            "end_night_rate": end_night_rate}


@app.route("/settings",
           name="settings",
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

    provider = request.forms.get("provider")
    provider = (db.query(database.Provider)
                .filter_by(name=provider)
                .update({"current": 1}))

    raw_start_night_rate = request.forms.get("start_night_rate")
    raw_end_night_rate = request.forms.get("end_night_rate")

    try:
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


@app.route("/login",
           name="login",
           template="login")
def login(db):
    """Login view"""
    if not db.query(database.User).all():
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

    providers = update_providers(True, db)

    sensor = database.Sensor(name="CitizenWatt",
                             type_id=electricity_type.id)
    db.add(sensor)

    return {"login": '',
            "providers": providers,
            "start_night_rate": '',
            "end_night_rate": ''}


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
    provider = request.forms.get("provider")
    raw_start_night_rate = request.forms.get("start_night_rate")
    raw_end_night_rate = request.forms.get("end_night_rate")

    ret = {"login": login,
           "providers": update_providers(False, db),
           "start_night_rate": raw_start_night_rate,
           "end_night_rate": raw_end_night_rate}

    try:
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

        provider = (db.query(database.Provider)
                    .filter_by(name=provider)
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


# ===
# App
# ===
SimpleTemplate.defaults["get_url"] = app.get_url
SimpleTemplate.defaults["API_URL"] = app.get_url("index")
SimpleTemplate.defaults["valid_session"] = lambda: session_manager.get_session()['valid']
run(app, host="0.0.0.0", port=config.get("port"), debug=config.get("debug"), reloader=True)
