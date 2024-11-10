#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:05:22 2024

@author: j.nacaratti
"""

import threading
from mining import serve_forever

# Config
POOL_HOST = 'public-pool.io'
POOL_PORT = 21496
POOL_PASSWORD = 'x'
BTC_ADDRESS = 'bc1ql076evskm73yqgl5e79g6vpukqnh8x9t32frdx'
WORKER_NAME = 'miinero'

SUGGESTED_DIFFICULTY = 0.001

stop_all_threads = threading.Event()

try:
    serve_forever(POOL_HOST, POOL_PORT, BTC_ADDRESS, WORKER_NAME, POOL_PASSWORD, SUGGESTED_DIFFICULTY, stop_all_threads)
finally:
    stop_all_threads.set()
    print("Finished script with success.")
