#!/usr/bin/env python3

"""
This script receives incoming AES encrypted measures from `receive` via
a named pipe and do the necessary to store them in database.
"""


import datetime
import json
import os
import stat
import struct
import sys
import time

from libcitizenwatt import database
from libcitizenwatt import tools
from Crypto.Cipher import AES
from libcitizenwatt.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_rate_type(db):
    """Returns "day" or "night" according to current time
    """
    user = db.query(database.User).filter_by(is_admin=1).first()
    now = datetime.datetime.now()
    now = 3600 * now.hour + 60 * now.minute
    if user is None:
        return -1
    elif user.end_night_rate > user.start_night_rate:
        if now > user.start_night_rate and now < user.end_night_rate:
            return 1
        else:
            return 0
    else:
        if now > user.start_night_rate or now < user.end_night_rate:
            return 1
        else:
            return 0


def get_cw_sensor():
    """Returns the citizenwatt sensor object or None"""
    db = create_session()
    sensor = (db.query(database.Sensor)
              .filter_by(name="CitizenWatt")
              .first())
    db.close()
    return sensor


# Configuration
config = Config()

# DB initialization
database_url = (config.get("database_type") + "://" + config.get("username") +
                ":" + config.get("password") + "@" + config.get("host") + "/" +
                config.get("database"))
engine = create_engine(database_url, echo=config.get("debug"))
create_session = sessionmaker(bind=engine)
database.Base.metadata.create_all(engine)

try:
    assert(stat.S_ISFIFO(os.stat(config.get("named_fifo")).st_mode))
except (AssertionError, FileNotFoundError):
    sys.exit("Unable to open fifo " + config.get("named_fifo") + ".")

try:
    with open(config.get("named_fifo"), 'rb') as fifo:
        while True:
            measure = fifo.read(16)
            print("New encrypted packet:" + str(measure))

            sensor = get_cw_sensor()
            while not sensor or not sensor.aes_key:
                tools.warning("Install is not complete ! " +
                              "Visit http://citizenwatt.local first.")
                time.sleep(1)
                sensor = get_cw_sensor()

            key = json.loads(sensor.aes_key)
            key = struct.pack("<16B", *key)

            decryptor = AES.new(key, AES.MODE_ECB)
            measure = decryptor.decrypt(measure)
            measure = struct.unpack("<HHHLlH", measure)
            print("New incoming measure:" + str(measure))

            power = measure[0]
            voltage = measure[1]
            battery = measure[2]
            timer = measure[3]

            if(sensor.last_timer and sensor.last_timer > 0 and
               sensor.last_timer < 4233600000 and
               timer < sensor.last_timer):
                tools.warning("Invalid timer in the last packet, skipping it")
            else:
                try:
                    db = create_session()
                    measure_db = database.Measure(sensor_id=sensor.id,
                                                   value=power,
                                                   timestamp=datetime.datetime.now().timestamp(),
                                                   night_rate=get_rate_type(db))
                    db.add(measure_db)
                    sensor.last_timer = timer
                    (db.query(database.Sensor)
                     .filter_by(name="CitizenWatt")
                     .update({"last_timer": sensor.last_timer}))
                    print("Saved successfully.")
                finally:
                    db.commit()
except KeyboardInterrupt:
    pass
