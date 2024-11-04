#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 23:50:53 2024

@author: j.nacaratti
"""

import socket
import json

class Client:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = None
        
    def connect_pool(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (self._host, self._port)
        print("[Client] Connecting to the pool...")
        try:
            self._sock.connect(addr)
            print("[Client] Connected to mining pool!")
            return True
        except socket.error as e:
            print("[Client] Error when connecting:", e)
            return False
    
    def check_pool_connection(self):
        
        if self.connected():
            return True
        
        print("[Client] Client not connected...")

        return self.connect_pool()
    
    def send_message(self, payload):
        json_message = json.dumps(payload) + '\n'
        print("[Client] Sending to pool:", json_message.strip())
        self._sock.send(json_message.encode())
        
    def read_until_newline(self):
        buffer = ""
        while True:
            chunk = self._sock.recv(1).decode()  # Read one byte
            if not chunk:  # If not more data
                break
            buffer += chunk
            if buffer.endswith('\n'):  # Check if the line is complete
                break
        return buffer.strip()
    
    def connected(self):
        if self._sock == None:
            return False
        
        try:
            self._sock.getpeername()
            return True
        except socket.error:
            return False