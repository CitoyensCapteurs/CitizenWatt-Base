#!/usr/bin/env python3
from sqlalchemy import Column, Float
from sqlalchemy import ForeignKey, Integer, Text, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True)
    type_id = Column(Integer,
                     ForeignKey("measures_types.id", ondelete="CASCADE"),
                     nullable=False)
    measures = relationship("Measures", passive_deletes=True)
    last_timer = Column(Integer)
    type = relationship("MeasureType", lazy="joined")
    aes_key = Column(VARCHAR(255))
    base_address = Column(VARCHAR(30))


class Measures(Base):
    __tablename__ = "measures"
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer,
                       ForeignKey("sensors.id", ondelete="CASCADE"),
                       nullable=False)
    value = Column(Float)
    timestamp = Column(Integer, index=True)
    night_rate = Column(Integer)  # Boolean, 1 if night_rate


class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(length=255), unique=True)
    type_id = Column(Integer,
                     ForeignKey("measures_types.id", ondelete="CASCADE"),
                     nullable=False)
    day_slope_watt_euros = Column(Float)
    day_constant_watt_euros = Column(Float)
    night_slope_watt_euros = Column(Float)
    night_constant_watt_euros = Column(Float)
    current = Column(Integer)
    threshold = Column(Integer)


class MeasureType(Base):
    __tablename__ = "measures_types"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(VARCHAR(length=255), unique=True)
    password = Column(Text)
    is_admin = Column(Integer)
    # Stored as seconds since beginning of day
    start_night_rate = Column(Integer)
    end_night_rate = Column(Integer)
