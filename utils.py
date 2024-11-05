#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:10:04 2024

@author: j.nacaratti
"""

import random
import time
import hashlib
from models import Miner, Worker

def current_time_millis():
    return int(time.time() * 1000)
    
def get_random_extranonce2(extranonce2_size):
    # Generate a random 32 bits number
    b0 = random.randint(0, 255)
    b1 = random.randint(0, 255)
    b2 = random.randint(0, 255)
    b3 = random.randint(0, 255)

    extranonce2_number = (b3 << 24) | (b2 << 16) | (b1 << 8) | b0

    # Format the number as an hex string with zeros in the left
    format_str = "{{:0{}x}}".format(extranonce2_size * 2)
    extranonce2 = format_str.format(extranonce2_number)

    return extranonce2

def get_next_extranonce2(extranonce2_size, extranonce2):
    # Converting extranonce2 from hex to int number
    extranonce2_number = int(extranonce2, 16)

    # Increments
    extranonce2_number += 1

    # Format the number as an hex string with zeros in the left
    format_str = "{{:0{}x}}".format(extranonce2_size * 2)
    extranonce2 = format_str.format(extranonce2_number)

    return extranonce2

def calculate_mining_data(worker, mine_job):
    
    miner = Miner()
    
    # Calculating target
    exponent = int(mine_job.nbits[:2], 16)
    significand = mine_job.nbits[2:]
    
    target = significand + ('00' * (exponent - 3))
    target = target.zfill(64)
    print("    target: ", target)
    
    bytearray_target = bytearray.fromhex(target)
    
    # Adjusting endianness (bytes order)
    size_target = len(bytearray_target)
    for j in range(8):
        idx1 = j
        idx2 = size_target - 1 - j
        bytearray_target[idx1], bytearray_target[idx2] = bytearray_target[idx2], bytearray_target[idx1]
    
    miner.bytearray_target = bytearray_target # in bytes
    
    # Calculating extranonce2
    extranonce2_size = worker.extranonce_size
    
    if worker.extranonce2 is None:
        worker.extranonce2 = get_random_extranonce2(extranonce2_size)
    else:
        worker.extranonce2 = get_next_extranonce2(extranonce2_size, worker.extranonce2)

    # Building coinbase
    coinbase = mine_job.coinb1 + worker.extranonce1 + worker.extranonce2 + mine_job.coinb2
    print("    coinbase: ", coinbase)
    
    coinbase_bytes = bytes.fromhex(coinbase)
    
    # Calculating double SHA-256 from coinbase
    inter_result = hashlib.sha256(coinbase_bytes).digest()
    sha_result = hashlib.sha256(inter_result).digest()
    
    miner.merkle_result = sha_result  # in bytes
    

#calculateMiningData()







