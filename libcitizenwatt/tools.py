#!/usr/bin/env python3
import numpy
import os
import sys


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
            x.append(i.timestamp.timestamp())
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


def update_base_address(base_address):
    """Update the address of the base stored in
    ~/.config/citizenwatt/base_address
    """
    path = os.path.expanduser("~/.config/citizenwatt/base_address")
    with open(path, "w+") as fh:
        fh.write(str(base_address))
