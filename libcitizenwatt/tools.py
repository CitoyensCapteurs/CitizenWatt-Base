#!/usr/bin/env python3
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
            if str(col.type) == "DATETIME":
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


def energy(powers):
    """Compute the energy associated to a dict of powers (in W)
    and associated timestamps (in s).
    """
    # TODO : Better integration
    energy = {'night_rate': 0, 'day_rate': 0, 'value': 0}
    for i in range(len(powers) - 1):
        if powers[i]["night_rate"] == 1:
            energy['night_rate'] += (powers[i]["value"] / 1000 *
                                     abs(powers[i]["timestamp"] - powers[i+1]["timestamp"]) / 3600)
        else:
            energy['day_rate'] += (powers[i]["value"] / 1000 *
                                   abs(powers[i]["timestamp"] - powers[i+1]["timestamp"]) / 3600)
    energy['value'] = energy['day_rate'] + energy['night_rate']
    return energy
