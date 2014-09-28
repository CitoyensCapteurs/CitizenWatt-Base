#!/usr/bin/env python3

import datetime
import os
import random
import stat
import struct
import sys
import time

from Crypto.Cipher import AES
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy import Float, ForeignKey, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


def warning(*objs):
    """Write warnings to stderr"""
    print("WARNING: ", *objs, file=sys.stderr)


# Configuration
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
    while True:
        measure = (random.randint(0, 4000), 0, 3444)
        print("New incoming measure:" + str(measure))

        power = measure[0]
        voltage = measure[1]
        battery = measure[2]

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
        time.sleep(8)
except KeyboardInterrupt:
    pass
