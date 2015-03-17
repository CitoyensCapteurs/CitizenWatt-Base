import math

from libcitizenwatt import database

def add_measure(db, timestamp, power):
    """Add a new mesure to counters in db at time timestamp with value
    power"""

    # Counter scales that are required, which means that they are created if
    # they do not exist.
    scales = [
        3600,      # hourly
        3600 * 24, # dayly
    ]
    scales = {scale: False for scale in scales}

    counters = (db.query(database.Counters)
                  .filter(database.Counters.start_time <= timestamp,
                          database.Counters.end_time > timestamp)
                  .all())

    try:
        db.begin()
        for counter in counters:
            (db.query(database.Counters).filter_by(id=counter.id)
                                        .update({"value": counter.value + power}))

            # Mark corresponding scale as seen
            scales[counter.end_time - counter.start_time] = True

        # For each required scale that has not been seen, create a new counter
        not_seen_scales = [scale for scale, seen in scales.items() if not seen]
        for scale in not_seen_scales:
            prev_timestamp = timestamp

            prev_same_scale_counter = (db.query(database.Counters)
                  .filter(database.Counters.end_time - database.Counters.start_time == scale)
                  .order_by(desc(database.Measure.start_time))
                  .first())

            if same_scale_counters:
                prev_timestamp = prev_same_scale_counter.start_time

            start_time = prev_timestamp + math.floor((timestamp - prev_timestamp) / scale)
            end_time = start_time + scale

            new_counter = database.Counter(value=power,
                                           start_time=start_time,
                                           end_time=end_time)
            db.add(new_counter)
            


        db.commit()
    except:
        db.rollback()


