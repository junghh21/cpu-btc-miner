#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 23:50:53 2024

@author: j.nacaratti
"""

import socket
import json
import time

class Client:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = None
        self._last_message_pool = self._current_time_millis()
        
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
    
    def disconnect_pool(self):
        if self._sock:
            try:
                self._sock.close()
                print("[Client] Disconnected from the pool.")
            except socket.error as e:
                print("[Client] Error when disconnecting:", e)
            finally:
                self._sock = None
        else:
            print("[Client] No active connection to disconnect.")
    
    def check_pool_connection(self):
        
        if self.connected():
            return True
        
        print("[Client] Client not connected...")

        return self.connect_pool()
    
    def check_pool_inactivity(self, limit_silence_time):
        actual_millis = self._current_time_millis()
        return actual_millis - self._last_message_pool > limit_silence_time
    
    def send_message(self, payload):
        json_message = json.dumps(payload) + '\n'
        print("[Client] Sending to pool:", json_message.strip())
        try:
            bytes_sent = self._sock.send(json_message.encode())
            if bytes_sent == len(json_message.encode()):
                self._last_message_pool = self._current_time_millis()
                return True
            else:
                return False
        except socket.error:
            return False
        
    def read_until_newline(self):
        buffer = ""
        while True:
            self._sock.settimeout(30)
            chunk = self._sock.recv(1).decode()  # Read one byte
            if not chunk:  # If not more data
                break
            buffer += chunk
            if buffer.endswith('\n'):  # Check if the line is complete
                break
            
        if buffer != "":
            self._last_message_pool = self._current_time_millis()
            print("[Client] Received from pool:", buffer)
            
        return buffer.strip()
    
    def connected(self):
        if self._sock == None:
            return False
        
        try:
            self._sock.getpeername()
            return True
        except socket.error:
            return False
    
    def _current_time_millis(self):
        return int(time.time() * 1000)