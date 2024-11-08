#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 18:41:05 2024

@author: j.nacaratti
"""

import random

class Miner:
    def __init__(self):
        self.id = random.randint(0, 1000)
        self.subscribed = False
        self.mining = False
        self.new_job = False
        self.pool_difficulty = 0.0001
        self.bytearray_target = None
        self.merkle_result = None
        self.bytearray_blockheader = None
        self.version_mask = None