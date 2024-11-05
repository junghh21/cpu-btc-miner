#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:39:30 2024

@author: j.nacaratti
"""

import json
import time
from utils import current_time_millis
from models import Worker, Miner, MineJob

STRATUM_PARSE_ERROR = "STRATUM_PARSE_ERROR"
STRATUM_SUCCESS = "STRATUM_SUCCESS"
STRATUM_UNKNOWN = "STRATUM_UNKNOWN"
MINING_NOTIFY = "MINING_NOTIFY"
MINING_SET_DIFFICULTY = "MINING_SET_DIFFICULTY"

LIMIT_SILENCE_TIME = 300000

templates = 0

def stratum_subscribe(client):
    payload = {
        "id": 1,
        "method": "mining.subscribe",
        "params": ["Miinero/V1.0.0"]
    }
    if client.send_message(payload):
        time.sleep(2)
        
        response = client.read_until_newline()
        
        response = json.loads(response)
        
        extranonce1 = response.get("result")[1]
        extranonce_size = response.get("result")[2]
        
        worker = Worker(extranonce1, extranonce_size)
    
        return worker
    else:
        return None
    
def stratum_authorize(client, btc_address, pool_pass):
    payload = {
        "id": 2,
        "method": "mining.authorize",
        "params": [f"{btc_address}", f"{pool_pass}"]
    }
    if client.send_message(payload):
        time.sleep(2)
        return True
    else:
        return False
    
def stratum_suggest_difficulty(client, difficulty):
    payload = {
        "id": 3,
        "method": "mining.suggest_difficulty",
        "params": [difficulty]
    }
    if client.send_message(payload):
        time.sleep(2)
        return True
    else:
        return False

def stratum_parse_method(line):
    try:
        doc = json.loads(line)
    except json.JSONDecodeError:
        return STRATUM_PARSE_ERROR

    if "method" not in doc:
        if doc.get("error") is None:
            return STRATUM_SUCCESS
        else:
            return STRATUM_UNKNOWN

    method = doc["method"]
    if method == "mining.notify":
        return MINING_NOTIFY
    elif method == "mining.set_difficulty":
        return MINING_SET_DIFFICULTY
    else:
        return STRATUM_UNKNOWN

def stratum_parse_set_difficulty(message):
    try:
        doc = json.loads(message)
    except json.JSONDecodeError:
        return False
    
    if "params" not in doc:
        return False

    difficulty = float(doc["params"][0])
    print(f"[Stratum] Difficulty received: {difficulty:.12f}")
    
    return difficulty

def stratum_parse_notify(message):
    try:
        doc = json.loads(message)
    except json.JSONDecodeError as e:
        print("[Stratum] Work aborted:", e)
        return False

    if "params" not in doc:
        return False

    try:
        job_id = str(doc["params"][0])
        prev_block_hash = str(doc["params"][1])
        coinb1 = str(doc["params"][2])
        coinb2 = str(doc["params"][3])
        merkle_branch = doc["params"][4]
        version = str(doc["params"][5])
        nbits = str(doc["params"][6])
        ntime = str(doc["params"][7])
        clean_jobs = bool(doc["params"][8])
        
        job = MineJob(job_id, prev_block_hash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs)

        print("[Stratum] JOB RECEIVED!")
        print(f"job_id: {job.job_id}")
        print(f"prevhash: {job.prev_block_hash}")
        print(f"coinb1: {job.coinb1}")
        print(f"coinb2: {job.coinb2}")
        print(f"merkle_branch size: {len(job.merkle_branch)}")
        print(f"version: {job.version}")
        print(f"nbits: {job.nbits}")
        print(f"ntime: {job.ntime}")
        print(f"clean_jobs: {job.clean_jobs}")

        return job

    except (IndexError, KeyError) as e:
        print("[Stratum] Error processing params:", e)
        return False

def serve_forever(client, btc_address, pool_pass, suggest_difficulty):
    
    global templates
    
    miner = Miner()
    worker = None
    
    current_difficulty = suggest_difficulty
    
    print("Starting stratum...")
    
    while True:
        
        # TODO: Check wifi connection
        
        if not client.check_pool_connection():
            print("Server unreachable, waiting 2 minutes...")
            
            miner.subscribed = False
            
            time.sleep(120)
        
        if not miner.subscribed:
            
            miner.mining = False
            
            worker = stratum_subscribe(client)
            if not worker:
                client.disconnect_pool()
                continue
            
            worker.worker_name = btc_address
            worker.worker_pass = pool_pass
            
            auth_res = stratum_authorize(client, btc_address, pool_pass)
            if not auth_res:
                client.disconnect_pool()
                continue
            
            stratum_suggest_difficulty(client, suggest_difficulty)
            
            miner.subscribed = True
            client.last_message_pool = current_time_millis()
        
        if client.check_pool_inactivity(LIMIT_SILENCE_TIME):
            print("Detected more than 2 min without communication")
            
            client.disconnect_pool()
            
            miner.subscribed = False
            continue
        else:
            stratum_suggest_difficulty(client, suggest_difficulty)
        
        while client.connected():
            
            read = client.read_until_newline()
            
            if read == "":
                continue
            
            method = stratum_parse_method(read)
            if method == STRATUM_PARSE_ERROR:
                print(f"Error when parsing json: {read}")
            if method == MINING_NOTIFY:
                job = stratum_parse_notify(read)
                if job:
                    
                    templates += 1
                    
                    miner.mining = False
                    miner.pool_difficulty = current_difficulty
                    miner.new_job = True
                    
            elif method == MINING_SET_DIFFICULTY:
                difficulty = stratum_parse_set_difficulty(read)
                if difficulty:
                    current_difficulty = difficulty
                    
                    miner.pool_difficulty = current_difficulty
            elif method == STRATUM_SUCCESS:
                print("Parsed JSON: Success")
            else:
                print("Parsed JSON: Unknown")
        
        
        