#!/usr/bin/env python3

"""
Database models for SQLAlchemy
"""

from sqlalchemy import Column, Float
from sqlalchemy import ForeignKey, Integer, Text, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Sensor(Base):
    """Represents a sensor"""
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True)
    type_id = Column(Integer,  # Measures type
                     ForeignKey("measures_types.id", ondelete="CASCADE"),
                     nullable=False)
    measures = relationship("Measure", passive_deletes=True)
    last_timer = Column(Integer)  # Counter to prevent replay attacks
    type = relationship("MeasureType", lazy="joined")
    aes_key = Column(VARCHAR(255))  # AES key to decrypt the measures


class Measure(Base):
    """Represents a measure"""
    __tablename__ = "measures"
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer,
                       ForeignKey("sensors.id", ondelete="CASCADE"),
                       nullable=False)
    value = Column(Float)
    timestamp = Column(Integer, index=True)
    night_rate = Column(Integer)  # Boolean, 1 if night_rate


class Provider(Base):
    """Represents an (energy) provider"""
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(length=255), unique=True)
    type_id = Column(Integer,  # Type of what he provides
                     ForeignKey("measures_types.id", ondelete="CASCADE"),
                     nullable=False)
    # Price is constant + slope * measure
    # This handles night and day tariffs (electricity)
    # If no distinction between night and day, day_* should be equal to night_*
    day_slope_watt_euros = Column(Float)
    day_constant_watt_euros = Column(Float)
    night_slope_watt_euros = Column(Float)
    night_constant_watt_euros = Column(Float)

    current = Column(Integer)  # Stores whether it is the provider used right now
    threshold = Column(Integer)  # Position of the threshold on the graph


class MeasureType(Base):
    """List all of the available measure types (electricity, gas, temp…)"""
    __tablename__ = "measures_types"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), unique=True)


class User(Base):
    """Represents a user in the system"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(VARCHAR(length=255), unique=True)
    password = Column(Text)
    is_admin = Column(Integer)

    # start_night_rate and end_night_rate are stored as seconds since
    # beginning of day
    start_night_rate = Column(Integer)
    end_night_rate = Column(Integer)
