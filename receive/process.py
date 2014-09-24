#!/usr/bin/env python3

import os
import struct
import tempfile
from Crypto.Cipher import AES

namedfifo = "/tmp/sensor"
key_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
key = ''.join([chr(i) for i in key_list])

try:
    os.mkfifo(namedfifo)
except OSError:
    pass

with open(namedfifo, 'rb') as fifo:
    measure = fifo.read(16)
    print(measure)
    decryptor = AES.new(key, AES.MODE_ECB)
    measure = decryptor.decrypt(measure)
    measure = struct.unpack("<HHHLlH", measure)
    power = measure[0]
    voltage = measure[1]
    battery = measure[2]
    timer = measure[3]
