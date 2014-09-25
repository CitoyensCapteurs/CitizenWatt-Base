#!/usr/bin/env python3

import binascii
import datetime
import os
import struct
import sys

from Crypto.Cipher import AES
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy import Float, ForeignKey, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

namedfifo = "/tmp/sensor"
key_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
key = ''.join([chr(i) for i in key_list])

Base = declarative_base()
username = "citizenwatt"
password = "citizenwatt"
database = "citizenwatt"
host = "localhost"
engine = create_engine("mysql+pymysql://"+username+":"+password+"@"+host+"/"+database, echo=True)


def warning(*objs):
    """Write warnings to stderr"""
    print("WARNING: ", *objs, file=sys.stderr)


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


# Test
cipher = [0xFE, 0xE4, 0xD1, 0x5D,
          0xD2, 0xB3, 0x68, 0x1B,
          0xDE, 0x1D, 0xBC, 0xBD,
          0xFF, 0x49, 0x37, 0xF8]
clear = [0x58, 0x2A, 0x00, 0x00,
         0x74, 0x0D, 0x8C, 0x11,
         0x00, 0x00, 0x00, 0x00,
         0x00, 0x00, 0x00, 0x00]
clear = struct.pack("<16B", *clear)
cipher = struct.pack("<16B", *cipher)
decryptor = AES.new(key, AES.MODE_ECB)
print(decryptor.encrypt(clear))
print(decryptor.decrypt(cipher))
sys.exit()
# /Test

try:
    os.mkfifo(namedfifo)
except OSError:
    pass

with open(namedfifo, 'rb') as fifo:
    measure = fifo.read(16)
    print("New incoming measure:" + measure)
    decryptor = AES.new(key, AES.MODE_ECB)
    measure = decryptor.decrypt(measure)
    measure = struct.unpack("<HHHLlH", measure)
    power = measure[0]
    voltage = measure[1]
    battery = measure[2]
    timer = measure[3]

    db = sessionmaker(bind=engine)
    sensor = db.query(Sensor).filter_by(name="CitizenWatt").first()
    type = db.query(MeasureType).filter_by(name="Électricité").first()
    if not sensor or not type:
        warning("Got packet "+str(measure)+" but install is not complete ! " +
                "Visit http://citizenwatt first.")
    else:
        measure_db = Measures(sensor_id=sensor.id,
                            type_id=type.id,
                            measures=power,
                            timestamp=datetime.datetime.now)
        db.add(measure_db)
        db.commit()
        print("Saved successfully.")
