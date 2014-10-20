#!/usr/bin/env python3

import bisect
import datetime

from libcitizenwatt import database
from libcitizenwatt import tools
from sqlalchemy import asc, desc


def do_cache_group_id(sensor, watt_euros, id1, id2, step, db, timestep=8):
    """
    Computes the cache (if needed) for the API call
    /api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_id/<id1:int>/<id2:int>/<step:int>

    Returns the stored (or computed) data.
    """
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

    if not data:
        data = []
    else:
        data_dict = tools.to_dict(data)
        tmp = [[] for i in range(len(steps))]
        for i in data_dict:
            tmp[bisect.bisect_left(steps, i["id"]) - 1].append(i)

        data = []
        for i in tmp:
            if len(i) == 0:
                data.append(i)
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
                    night_rate = tools.watt_euros("current",
                                                  'night',
                                                  energy['night_rate'],
                                                  db)["data"]
                else:
                    night_rate = 0
                if energy["day_rate"] != 0:
                    day_rate = tools.watt_euros("current",
                                                'day',
                                                energy['day_rate'],
                                                db)["data"]
                else:
                    day_rate = 0
                tmp_data = {"value": night_rate + day_rate}
            data.append(tmp_data)

    return data


def do_cache_group_timestamp(sensor, watt_euros, time1, time2, step, db):
    """
    Computes the cache (if needed) for the API call
    /api/<sensor:int>/get/<watt_euros:re:watts|kwatthours|euros>/by_time/<time1:float>/<time2:float>/<step:float>

    Returns the stored (or computed) data.
    """
    steps = [i for i in range(time1, time2, step)]
    steps.append(time2)

    data = (db.query(database.Measures)
            .filter(database.Measures.sensor_id == sensor,
                    database.Measures.timestamp
                    .between(datetime.datetime.fromtimestamp(time1),
                             datetime.datetime.fromtimestamp(time2)))
            .order_by(asc(database.Measures.timestamp))
            .all())

    if not data:
        data = []
    else:
        tmp = [[] for i in range(len(steps))]
        for i in data:
            tmp[bisect.bisect_left(steps, i.timestamp.timestamp()) - 1].append(i)

        data = []
        for i in tmp:
            if len(i) == 0:
                data.append([])
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
                    night_rate = tools.watt_euros("current",
                                                  'night',
                                                  energy['night_rate'],
                                                  db)["data"]
                else:
                    night_rate = 0
                if energy["day_rate"] != 0:
                    day_rate = tools.watt_euros("current",
                                                'day',
                                                energy['day_rate'],
                                                db)["data"]
                else:
                    day_rate = 0
                tmp_data = {"value": night_rate + day_rate}
            data.append(tmp_data)

    return data
