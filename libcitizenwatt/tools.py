#!/usr/bin/env python3

"""
Misc functions
"""

import numpy
import os
import requests
import subprocess
import sys

from libcitizenwatt import database


def warning(*objs):
    """Write warnings to stderr"""
    print("WARNING: ", *objs, file=sys.stderr)


def to_dict(model):
    """
    Returns a JSON representation of an SQLAlchemy-backed object.

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


def is_day_night_rate(db, provider=None):
    """
    Returns true if night and day rates are distincts, false otherwise (meaning
    that such a distinction is useless)
    """
    if provider is None:
        provider = db.query(database.Provider).filter_by(current=1).first().__dict__
    ds = provider['day_slope_watt_euros']
    dc = provider['day_constant_watt_euros']
    ns = provider['night_slope_watt_euros']
    nc = provider['night_constant_watt_euros']
    return ds != ns or dc != nc


def energy(powers, default_timestep=8):
    """
    Compute the energy associated to a list of measures (in W)
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
    """
    Given an energy_provider, tariff (night or day) and a consumption in kWh
    it returns the associated cost."""
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
    """
    Update the address of the base stored in
    ~/.config/citizenwatt/base_address
    """
    path = os.path.expanduser("~/.config/citizenwatt/base_address")
    with open(path, "w+") as fh:
        fh.write(str(base_address))


def get_base_address():
    """
    Get the base address stored in
    ~/.config/citizenwatt/base_address

    Returns false if an error happened.
    """
    path = os.path.expanduser("~/.config/citizenwatt/base_address")
    try:
        with open(path, "r") as fh:
            return fh.read()
    except FileNotFoundError:
        return False


nrf_power_dict = {"min": 0, "low": 1, "med": 2, "high": 3}


def update_nrf_power(nrf_power):
    """
    Update the power for the nrf stored in
    ~/.config/citizenwatt/nrf_power
    """
    path = os.path.expanduser("~/.config/citizenwatt/nrf_power")
    with open(path, "w+") as fh:
        fh.write(str(nrf_power_dict[nrf_power]))


def get_nrf_power():
    """
    Get the power for the nrf stored in
    ~/.config/citizenwatt/nrf_power

    Returns false if an error happened.
    """
    path = os.path.expanduser("~/.config/citizenwatt/nrf_power")
    try:
        nrf_power = 3
        with open(path, "r") as fh:
            nrf_power = int(fh.read())
        return [name for name, index in nrf_power_dict.items()
                if index == nrf_power][0]
    except FileNotFoundError:
        return False


def update_providers(url_energy_providers, fetch, db):
    """Updates the available providers. Simply returns them without updating if
    fetch is False.
    """
    try:
        assert(fetch)
        providers = requests.get(url_energy_providers).json()
    except (requests.ConnectionError, AssertionError):
        providers = db.query(database.Provider).all()
        if not providers:
            providers = []
        return to_dict(providers)

    old_current = db.query(database.Provider).filter_by(current=1).first()
    db.query(database.Provider).delete()

    providers = [dict(provider, **{'current': (1 if old_current and old_current.name == provider["name"]
                                               else 0)})
                 for provider in providers]

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
                                        current=provider['current'],
                                        threshold=int(provider["threshold"]))
        db.add(provider_db)
    return providers


def ssh_status():
    """Check SSH status. Returns `True` if SSH is running, `False` otherwise.
    """
    try:
        subprocess.check_call(["/etc/init.d/ssh", "status"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def toggle_ssh():
    """Start / stop SSH service."""
    status = ssh_status()
    if status is True:
        # Start the service
        try:
            subprocess.call(["sudo", "/etc/init.d/ssh", "start"])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    elif status is False:
        # Stop it
        try:
            subprocess.call(["sudo", "/etc/init.d/ssh", "stop"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
