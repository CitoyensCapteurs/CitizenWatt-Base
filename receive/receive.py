#!/usr/bin/env python3

import datetime
import nrf24
import sqlalchemy as sql
import time

PIPE = [0xE0, 0x56, 0xD4, 0x46, 0xD0]
NRF_CHANNEL = 76
NRF_SPEED = nrf24.NRF24.BR_1MBPS
NRF_PA_LEVEL = nrf24.NRF24.PA_MAX

db = sql.create_engine('mysql+pymysql://root:citizenwatt@localhost/citizenwatt')
metadata = sql.MetaData()
measures = sql.Table('measures', metadata,
                     sql.Column('id', sql.Integer, primary_key=True),
                     sql.Column('date', sql.DateTime),
                     sql.Column('power', sql.Integer),
		     mysql_engine='InnoDB',
             mysql_charset='utf8')
metadata.create_all(db)

radio = nrf24.NRF24()
radio.begin(1, 0, "P9_15", "P9_16")
radio.setRetries(15, 15)
radio.setPayloadSize(8)
radio.setChannel(NRF_CHANNEL)
radio.setDataRate(NRF_SPEED)
radio.setPALevel(NRF_PA_LEVEL)
radio.setAutoAck(True)
radio.openReadingPipe(1, PIPE)

radio.printDetails()

while True:
    while not radio.available(PIPE):
        time.sleep(0.01)

    recv_buffer = []
    radio.read(recv_buffer)

    print(recv_buffer)
    i = measures.insert()
    i.execute({'power': int(recv_buffer),
               'time': datetime.datetime.now()
               })
