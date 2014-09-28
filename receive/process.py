#!/usr/bin/env python3

import datetime
import os
import stat
import struct
import sys

from Crypto.Cipher import AES
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy import Float, ForeignKey, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


def warning(*objs):
    """Write warnings to stderr"""
    print("WARNING: ", *objs, file=sys.stderr)


# Configuration
named_fifo = "/tmp/sensor"

key_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
key = struct.pack("<16B", *key_list)

username = "citizenwatt"
password = "citizenwatt"
database = "citizenwatt"
host = "localhost"

debug = True

# DB initialization
Base = declarative_base()
engine_url = "mysql+pymysql://"+username+":"+password+"@"+host+"/"+database
engine = create_engine(engine_url, echo=debug)
create_session = sessionmaker(bind=engine)
last_timer = 0


# ORM models
class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True)
    type_id = Column(Integer,
                     ForeignKey("measures_types.id", ondelete="CASCADE"),
                     nullable=False)
    measures = relationship("Measures", passive_deletes=True)
    type = relationship("MeasureType", lazy="joined")


class Measures(Base):
    __tablename__ = "measures"
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer,
                       ForeignKey("sensors.id", ondelete="CASCADE"),
                       nullable=False)
    value = Column(Float)
    timestamp = Column(DateTime)


class MeasureType(Base):
    __tablename__ = "measures_types"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True)


Base.metadata.create_all(engine)


try:
    assert(stat.S_ISFIFO(os.stat(named_fifo).st_mode))
except (AssertionError, FileNotFoundError):
    sys.exit("Unable to open fifo "+named_fifo+".")

try:
    with open(named_fifo, 'rb') as fifo:
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
                sensor = db.query(Sensor).filter_by(name="CitizenWatt").first()
                if not sensor or not type:
                    warning("Got packet "+str(measure)+" but install is not " +
                            "complete ! Visit http://citizenwatt first.")
                    db.close()
                else:
                    measure_db = Measures(sensor_id=sensor.id,
                                          value=power,
                                          timestamp=datetime.datetime.now())
                    db.add(measure_db)
                    db.commit()
                    print("Saved successfully.")
                    last_timer = timer
except KeyboardInterrupt:
    pass
