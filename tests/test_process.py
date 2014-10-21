#!/usr/bin/env python3
"""Generate test data instead of piping from the sensor."""

import datetime
import random
import time
import math

from libcitizenwatt import database
from libcitizenwatt import tools
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

# DB initialization
database_url = (config.get("database_type") + "://" + config.get("username") + ":" +
                config.get("password") + "@" + config.get("host") + "/" +
                config.get("database"))
engine = create_engine(database_url, echo=config.get("debug"))
create_session = sessionmaker(bind=engine)
database.Base.metadata.create_all(engine)

try:
    while True:
        power = random.randint(0, 4000)
        power = math.sin(time.clock()*2)**2 * 2000
        print("New encrypted packet:" + str(power))

        db = create_session()
        sensor = (db.query(database.Sensor)
                  .filter_by(name="CitizenWatt")
                  .first())
        if not sensor:
            tools.warning("Got packet "+str(power)+" but install is not " +
                          "complete ! Visit http://citizenwatt first.")
            db.close()
        else:
            now = datetime.datetime.now().timestamp()
            measure_db = database.Measures(sensor_id=sensor.id,
                                           value=power,
                                           timestamp=now,
                                           night_rate=get_rate_type(db))
            db.add(measure_db)
            db.commit()
            print(now)
            print("Saved successfully.")
        time.sleep(8)
except KeyboardInterrupt:
    pass
