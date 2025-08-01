#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:39:30 2024

@author: j.nacaratti
"""

import json
import time
from models import MineJob

STRATUM_PARSE_ERROR = "STRATUM_PARSE_ERROR"
STRATUM_SUCCESS = "STRATUM_SUCCESS"
STRATUM_UNKNOWN = "STRATUM_UNKNOWN"
MINING_NOTIFY = "MINING_NOTIFY"
MINING_SET_DIFFICULTY = "MINING_SET_DIFFICULTY"
VERSION_MASK = "VERSION_MASK"

def stratum_subscribe(client):
    payload = {
        "id": 1,
        "method": "mining.subscribe",
        "params": ["Miinero/V1.0.0"]
    }
    
    extranonce1 = None
    extranonce_size = None
    
    if client.send_message(payload):
        time.sleep(2)
        
        response = client.read_until_newline()
        
        response = json.loads(response)
        
        extranonce1 = response.get("result")[1]
        extranonce_size = response.get("result")[2]
    
    return extranonce1, extranonce_size
    
def stratum_authorize(client, worker_name, pool_pass):
    payload = {
        "id": 3,
        "method": "mining.authorize",
        "params": [f"{worker_name}", f"{pool_pass}"]
    }
    if client.send_message(payload):
        time.sleep(2)
        return True
    else:
        return False
    
def stratum_suggest_difficulty(client, difficulty):
    payload = {
        "id": 5,
        "method": "mining.suggest_difficulty",
        "params": [difficulty]
    }
    if client.send_message(payload):
        time.sleep(2)
        return True
    else:
        return False

def stratum_configure(client):
    payload = {
        "id": 2,
        "method": "mining.configure",
        "params": []
    }
    if client.send_message(payload):
        time.sleep(2)
        return True
    else:
        return False

def stratum_submit(client, worker_name, job_id, extranonce2, ntime, nonce):#, version_mask):
    payload = {
        "id": 4,
        "method": "mining.submit",
        "params": [
            worker_name,
            job_id,
            extranonce2,
            ntime,
            nonce,
            #version_mask
        ]
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
        if "result" in doc and isinstance(doc["result"], dict) and "version-rolling" in doc["result"].keys():
            return VERSION_MASK
        elif doc.get("error") is None:
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

def stratum_parse_version_mask(message):
    try:
        doc = json.loads(message)
    except json.JSONDecodeError:
        return False
    
    if "result" not in doc:
        return False

    mask = doc["result"]["version-rolling.mask"]
    print(f"[Stratum] Version mask received: {mask}")
    
    return mask

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
        print(f"-> job_id: {job.job_id}")
        print(f"-> prevhash: {job.prev_block_hash}")
        print(f"-> coinb1: {job.coinb1}")
        print(f"-> coinb2: {job.coinb2}")
        print(f"-> merkle_branch size: {len(job.merkle_branch)}")
        print(f"-> version: {job.version}")
        print(f"-> nbits: {job.nbits}")
        print(f"-> ntime: {job.ntime}")
        print(f"-> clean_jobs: {job.clean_jobs}")

        return job

    except (IndexError, KeyError) as e:
        print("[Stratum] Error processing params:", e)
        return False
        