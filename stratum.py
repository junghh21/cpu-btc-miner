#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:39:30 2024

@author: j.nacaratti
"""

import socket
import time
from utils import check_socket_connected

isMinerSubscribed = False
sock = None

def stratum_subscribe(client):
    payload = {
        "id": 1,
        "method": "mining.subscribe",
        "params": []
    }
    
    time.sleep(2)

def serve_forever(client, btc_address, suggest_difficulty):
    while True:
        
        # TODO: Check wifi connection
        
        if not client.check_pool_connection():
            print("Server unreachable, waiting 2 minutes...")
            
            isMinerSubscribed = False
            
            time.sleep(120)
        
        if not isMinerSubscribed:
            
            
        
        
        
        
        
        
        
        