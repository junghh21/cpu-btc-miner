#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:05:22 2024

@author: j.nacaratti
"""

from models import Client
import threading
from stratum import serve_forever, start_stratum

stop_event = threading.Event()

# Config
POOL_HOST = 'public-pool.io'
POOL_PORT = 21496
BTC_ADDRESS = 'YOUR_BTC_WALLET'

SUGGESTED_DIFFICULTY = 0.0001

client = Client(POOL_HOST, POOL_PORT)

stratum_thread = threading.Thread(target=start_stratum, args=(client, BTC_ADDRESS, "x", SUGGESTED_DIFFICULTY, stop_event))
stratum_thread.start()

try:
    serve_forever()
finally:
    stop_event.set()
    stratum_thread.join()
    print("Finished script with success.")

    
    