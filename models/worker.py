#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 23:44:35 2024

@author: j.nacaratti
"""

class Worker:
    def __init__(self):
        self.subscribed = False
        self.extranonce1 = None
        self.extranonce_size = None
        self.extranonce2 = None
        self.worker_name = None
        self.worker_pass = None
        self.miner = None
        self.templates = 0
        self.best_diff = 0
