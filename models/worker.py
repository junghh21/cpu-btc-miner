#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 23:44:35 2024

@author: j.nacaratti
"""

class Worker:
    def __init__(self, extranonce1, extranonce_size):
        self.extranonce1 = extranonce1
        self.extranonce_size = extranonce_size
        self.extranonce2 = None
        self.worker_name = None
        self.worker_pass = None
