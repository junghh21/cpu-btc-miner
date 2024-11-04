#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:05:22 2024

@author: j.nacaratti
"""

from models import Client

# Config
POOL_HOST = 'public-pool.io'
POOL_PORT = 21496
BTC_ADDRESS = 'YOUR_BTC_WALLET'

SUGGESTED_DIFFICULTY = 0.0001

client = Client(POOL_HOST, POOL_PORT)

