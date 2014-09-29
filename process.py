#!/usr/bin/env python3

import database
import datetime
import os
import stat
import struct
import sys

from Crypto.Cipher import AES
from libcitizenwatt.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def warning(*objs):
    """Write warnings to stderr"""
    print("WARNING: ", *objs, file=sys.stderr)


# Configuration
config = Config()
key = struct.pack("<16B", *config.get("aes_key"))

# DB initialization
database_url = ("mysql+pymysql://" + config.get("username") + ":" +
                config.get("password") + "@" + config.get("host") + "/" +
                config.get("database"))
engine = create_engine(database_url, echo=config.get("debug"))
create_session = sessionmaker(bind=engine)
database.Base.metadata.create_all(engine)

last_timer = 0


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

            if timer < last_timer:
                warning("Invalid timer in the last packet, skipping it")
            else:
                db = create_session()
                sensor = (db.query(database.Sensor)
                          .filter_by(name="CitizenWatt")
                          .first())
                if not sensor or not type:
                    warning("Got packet "+str(measure)+" but install is not " +
                            "complete ! Visit http://citizenwatt first.")
                    db.close()
                else:
                    measure_db = database.Measures(sensor_id=sensor.id,
                                                   value=power,
                                                   timestamp=datetime.datetime.now())
                    db.add(measure_db)
                    db.commit()
                    print("Saved successfully.")
                    last_timer = timer
except KeyboardInterrupt:
    pass
