#!/usr/bin/env python3

import datetime
import os
import stat
import struct
import sys

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


# Configuration
config = Config()
key = struct.pack("<16B", *config.get("aes_key"))

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

            decryptor = AES.new(key, AES.MODE_ECB)
            measure = decryptor.decrypt(measure)
            measure = struct.unpack("<HHHLlH", measure)
            print("New incoming measure:" + str(measure))

            power = measure[0]
            voltage = measure[1]
            battery = measure[2]
            timer = measure[3]

            db = create_session()
            sensor = (db.query(database.Sensor)
                        .filter_by(name="CitizenWatt")
                        .first())
            last_timer = sensor.last_timer if sensor else 0

            if last_timer > 0 and last_timer < 4233600000 and timer < last_timer:
                tools.warning("Invalid timer in the last packet, skipping it")
            else:
                if not sensor or not type:
                    tools.warning("Got packet "+str(measure)+" but install " +
                                  "is not complete ! " +
                                  "Visit http://citizenwatt.local first.")
                    db.close()
                else:
                    measure_db = database.Measures(sensor_id=sensor.id,
                                                   value=power,
                                                   timestamp=datetime.datetime.now(),
                                                   night_rate=get_rate_type(db))
                    db.add(measure_db)
                    sensor.last_timer = timer
                    (db.query(database.Sensor)
                     .filter_by(name="CitizenWatt")
                     .update({"last_timer": last_timer}))
                    db.commit()
                    print("Saved successfully.")
except KeyboardInterrupt:
    pass
