#!/usr/bin/env python3
import numpy
import os
import sys

from libcitizenwatt import database


def warning(*objs):
    """Write warnings to stderr"""
    print("WARNING: ", *objs, file=sys.stderr)


def to_dict(model):
    """Returns a JSON representation of an SQLAlchemy-backed object.

    Returns a timestamp for DateTime fields, to be easily JSON serializable.

    TODO : Use runtime inspection API
    From https://zato.io/blog/posts/converting-sqlalchemy-objects-to-json.html
    """
    if isinstance(model, list):
        return [to_dict(i) for i in model]
    else:
        dict = {}
        dict['id'] = getattr(model, 'id')

        for col in model._sa_class_manager.mapper.mapped_table.columns:
            if str(col.type) == "TIMESTAMP":
                dict[col.name] = getattr(model, col.name).timestamp()
            else:
                dict[col.name] = getattr(model, col.name)

        return dict


def last_day(month, year):
    """Returns the last day of month <month> of year <year>."""
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month == 2:
        if year % 4 == 0 and (not year % 100 or year % 400):
            return 29
        else:
            return 28
    else:
        return 30


def energy(powers, default_timestep=8):
    """Compute the energy associated to a list of measures (in W)
    and associated timestamps (in s).
    """
    energy = {'night_rate': 0, 'day_rate': 0, 'value': 0}
    if len(powers) == 1:
        if powers[0].night_rate == 1:
            energy["night_rate"] = (powers[0].value / 1000 *
                                    default_timestep / 3600)
        else:
            energy["day_rate"] = (powers[0].value / 1000 *
                                  default_timestep / 3600)
        energy['value'] = energy['day_rate'] + energy['night_rate']
    else:
        x = []
        day_rate = []
        night_rate = []
        for i in powers:
            x.append(i.timestamp)
            if i.night_rate == 1:
                night_rate.append(i.value)
                day_rate.append(0)
            else:
                day_rate.append(i.value)
                night_rate.append(0)
        energy["night_rate"] = numpy.trapz(night_rate, x) / 1000 / 3600
        energy["day_rate"] = numpy.trapz(day_rate, x) / 1000 / 3600
        energy['value'] = energy['day_rate'] + energy['night_rate']
    return energy


def watt_euros(energy_provider, tariff, consumption, db):
    if energy_provider != 0:
        provider = (db.query(database.Provider)
                    .filter_by(id=energy_provider)
                    .first())
    else:
        provider = (db.query(database.Provider)
                    .filter_by(current=1)
                    .first())
    if not provider:
        data = None
    else:
        if tariff == "night":
            data = provider.night_slope_watt_euros * consumption
        elif tariff == "day":
            data = provider.day_slope_watt_euros * consumption
        else:
            data = None
    return data


def update_base_address(base_address):
    """Update the address of the base stored in
    ~/.config/citizenwatt/base_address
    """
    path = os.path.expanduser("~/.config/citizenwatt/base_address")
    with open(path, "w+") as fh:
        fh.write(str(base_address))
