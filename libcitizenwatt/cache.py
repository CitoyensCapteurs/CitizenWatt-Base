#!/usr/bin/env python3

import bisect
import datetime
import json
import numpy
import redis

from libcitizenwatt import database
from libcitizenwatt import tools
from sqlalchemy import asc, desc
from libcitizenwatt.config import Config


config = Config()


def do_cache_ids(sensor, watt_euros, id1, id2, db, force_refresh=False):
    """
    Computes the cache (if needed) for the API call
    /api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>

    Returns the stored (or computed) data or None if parameters are invalid.
    """
    r = redis.Redis(decode_responses=True)
    if not force_refresh:
        data = r.get(watt_euros + "_" + str(sensor) + "_" + "by_id" + "_" +
                     str(id1) + "_" + str(id2))
        if data:
            # If found in cache, return it
            return json.loads(data)

    if id1 >= 0 and id2 >= 0 and id2 >= id1:
        data = (db.query(database.Measures)
                .filter(database.Measures.sensor_id == sensor,
                        database.Measures.id >= id1,
                        database.Measures.id < id2)
                .order_by(asc(database.Measures.timestamp))
                .all())
    elif id1 <= 0 and id2 <= 0 and id2 >= id1:
        data = (db.query(database.Measures)
                .filter_by(sensor_id=sensor)
                .order_by(desc(database.Measures.timestamp))
                .slice(-id2, -id1)
                .all())
        data.reverse()
    else:
        return None

    if not data:
        data = None
    else:
        time1 = data[0].timestamp
        time2 = data[-1].timestamp
        if watt_euros == 'kwatthours' or watt_euros == 'euros':
            data = tools.energy(data)
            if watt_euros == 'euros':
                if data["night_rate"] != 0:
                    night_rate = tools.watt_euros(0,
                                                  'night',
                                                  data['night_rate'],
                                                  db)
                else:
                    night_rate = 0
                if data["day_rate"] != 0:
                    day_rate = tools.watt_euros(0,
                                                'day',
                                                data['day_rate'],
                                                db)
                else:
                    day_rate = 0
                data = {"value": night_rate + day_rate}
        else:
            data = tools.to_dict(data)

    # Store in cache
    r.set(watt_euros + "_" + str(sensor) + "_" + "by_id" + "_" +
          str(id1) + "_" + str(id2),
          json.dumps(data),
          time2 - time1)

    return data


def do_cache_group_id(sensor, watt_euros, id1, id2, step, db,
                      timestep=config.get("default_timestep"),
                      force_refresh=False):
    """
    Computes the cache (if needed) for the API call
    /api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>/<step:int>

    Returns the stored (or computed) data.
    """
    r = redis.Redis(decode_responses=True)
    if not force_refresh:
        data = r.get(watt_euros + "_" + str(sensor) + "_" + "by_id" + "_" +
                     str(id1) + "_" + str(id2) + "_" +
                     str(step) + "_" + str(timestep))
        if data:
            # If found in cache, return it
            return json.loads(data)

    steps = [i for i in range(id1, id2, step)]
    steps.append(id2)

    if id1 >= 0 and id2 >= 0 and id2 >= id1:
        data = (db.query(database.Measures)
                .filter(database.Measures.sensor_id == sensor,
                        database.Measures.id >= id1,
                        database.Measures.id < id2)
                .order_by(asc(database.Measures.timestamp))
                .all())
    elif id1 <= 0 and id2 <= 0 and id2 >= id1:
        data = (db.query(database.Measures)
                .filter_by(sensor_id=sensor)
                .order_by(desc(database.Measures.timestamp))
                .slice(-id2, -id1)
                .all())
        data.reverse()
    else:
        raise ValueError

    time2 = None
    if not data:
        data = [None for i in range(len(steps) - 1)]
    else:
        time1 = data[0].timestamp
        time2 = data[-1].timestamp
        data_dict = tools.to_dict(data)
        tmp = [[] for i in range(len(steps) - 1)]
        for i in data_dict:
            tmp[bisect.bisect_left(steps, i["id"]) - 1].append(i)

        data = []
        for i in tmp:
            if len(i) == 0:
                data.append(None)
                continue

            energy = tools.energy(i)
            if watt_euros == "watts":
                tmp_data = {"value": energy["value"] / (step * timestep) * 1000 * 3600,
                            "day_rate": energy["day_rate"] / (step * timestep) * 1000 * 3600,
                            "night_rate": energy["night_rate"] / (step * timestep) * 1000 * 3600}
            elif watt_euros == 'kwatthours':
                tmp_data = energy
            elif watt_euros == 'euros':
                if energy["night_rate"] != 0:
                    night_rate = tools.watt_euros(0,
                                                  'night',
                                                  energy['night_rate'],
                                                  db)
                else:
                    night_rate = 0
                if energy["day_rate"] != 0:
                    day_rate = tools.watt_euros(0,
                                                'day',
                                                energy['day_rate'],
                                                db)
                else:
                    day_rate = 0
                tmp_data = {"value": night_rate + day_rate}
            data.append(tmp_data)
    if len(data) == 0:
        data = None
    if time2 is not None:
        # Store in cache
        if time2 < datetime.datetime.now().timestamp():
            # If new measures are to come, short lifetime (basically timestep)
            r.set(watt_euros + "_" + str(sensor) + "_" + "by_id" + "_" +
                str(id1) + "_" + str(id2) + "_" +
                str(step) + "_" + str(timestep),
                json.dumps(data),
                timestep)
        else:
            # Else, store for a greater lifetime (basically time2 - time1)
            r.set(watt_euros + "_" + str(sensor) + "_" + "by_id" + "_" +
                str(id1) + "_" + str(id2) + "_" +
                str(step) + "_" + str(timestep),
                json.dumps(data),
                time2 - time1)

    return data


def do_cache_times(sensor, watt_euros, time1, time2, db, force_refresh=False):
    """
    Computes the cache (if needed) for the API call
    /api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>
    Returns the stored (or computed) data.
    """
    r = redis.Redis(decode_responses=True)
    if not force_refresh:
        data = r.get(watt_euros + "_" + str(sensor) + "_" + "by_time" + "_" +
                     str(time1) + "_" + str(time2))
        if data:
            # If found in cache, return it
            return json.loads(data)

    data = (db.query(database.Measures)
            .filter(database.Measures.sensor_id == sensor,
                    database.Measures.timestamp >= time1,
                    database.Measures.timestamp < time2)
            .order_by(asc(database.Measures.timestamp))
            .all())

    if not data:
        data = None
    else:
        if watt_euros == "kwatthours" or watt_euros == "euros":
            data = tools.energy(data)
            if watt_euros == "euros":
                data = {"value": (tools.watt_euros(0,
                                                   'night',
                                                   data['night_rate'],
                                                   db) +
                                  tools.watt_euros(0,
                                                   'day',
                                                   data['day_rate'],
                                                   db))}

        else:
            data = tools.to_dict(data)

    # Store in cache
    r.set(watt_euros + "_" + str(sensor) + "_" + "by_id" + "_" +
          str(time1) + "_" + str(time2),
          json.dumps(data),
          int(time2) - int(time1))

    return data


def do_cache_group_timestamp(sensor, watt_euros, time1, time2, step, db,
                             force_refresh=True):
    """
    Computes the cache (if needed) for the API call
    /api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>/<step:float>

    Returns the stored (or computed) data.
    """
    r = redis.Redis(decode_responses=True)
    if not force_refresh:
        data = r.get(watt_euros + "_" + str(sensor) + "_" + "by_time" + "_" +
                     str(time1) + "_" + str(time2) + "_" + str(step))
        if data:
            # If found in cache, return it
            return json.loads(data)

    steps = [i for i in numpy.arange(time1, time2, step)]
    steps.append(time2)

    data = (db.query(database.Measures)
            .filter(database.Measures.sensor_id == sensor,
                    database.Measures.timestamp
                    .between(time1, time2))
            .order_by(asc(database.Measures.timestamp))
            .all())

    if not data:
        data = [None for i in range(len(steps) - 1)]
    else:
        tmp = [[] for i in range(len(steps) - 1)]
        for i in data:
            index = bisect.bisect_left(steps, i.timestamp)
            if index > 0:
                index -= 1
            tmp[index].append(i)

        data = []
        for i in tmp:
            if len(i) == 0:
                data.append(None)
                continue

            energy = tools.energy(i)
            if watt_euros == "watts":
                tmp_data = {"value": energy["value"] / step * 1000 * 3600,
                            "day_rate": energy["day_rate"] / step * 1000 * 3600,
                            "night_rate": energy["night_rate"] / step * 1000 * 3600}
            elif watt_euros == 'kwatthours':
                tmp_data = energy
            elif watt_euros == 'euros':
                if energy["night_rate"] != 0:
                    night_rate = tools.watt_euros(0,
                                                  'night',
                                                  energy['night_rate'],
                                                  db)
                else:
                    night_rate = 0
                if energy["day_rate"] != 0:
                    day_rate = tools.watt_euros(0,
                                                'day',
                                                energy['day_rate'],
                                                db)
                else:
                    day_rate = 0
                tmp_data = {"value": night_rate + day_rate}
            data.append(tmp_data)
    if len(data) == 0:
        data = None
    # Store in cache
    if time2 < datetime.datetime.now().timestamp():
        # If new measures are to come, short lifetime (basically timestep)
        r.setex(watt_euros + "_" + str(sensor) + "_" + "by_time" + "_" +
                str(time1) + "_" + str(time2) + "_" + str(step),
                json.dumps(data),
                int(step))
    else:
        # Else, store for a greater lifetime (basically time2 - time1)
        r.setex(watt_euros + "_" + str(sensor) + "_" + "by_time" + "_" +
                str(time1) + "_" + str(time2) + "_" + str(step),
                json.dumps(data),
                int(time2 - time1))

    return data
