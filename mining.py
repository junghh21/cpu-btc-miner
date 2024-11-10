#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 00:06:05 2024

@author: j.nacaratti
"""

import time
import struct
import threading
from utils import calculate_mining_data, diff_from_target, double_sha256
from models import Miner, Client, Worker
from stratum import stratum_subscribe, stratum_configure, stratum_authorize, stratum_suggest_difficulty, stratum_parse_method, stratum_parse_notify, stratum_parse_set_difficulty, stratum_parse_version_mask, stratum_submit,  STRATUM_PARSE_ERROR, STRATUM_SUCCESS, MINING_NOTIFY, MINING_SET_DIFFICULTY, VERSION_MASK

LIMIT_SILENCE_TIME = 300000
MAX_NONCE = 25000000
TARGET_NONCE = 471136297

templates = 0

running = True

def start_stratum(client, worker: Worker, suggest_difficulty):
    
    worker.miner = Miner()
    
    current_difficulty = suggest_difficulty
    
    print("[Mining] Starting stratum...")
    
    while True:
        
        # TODO: Check wifi connection
        
        if not client.check_pool_connection():
            print("[Mining] Server unreachable, waiting 2 minutes...")
            
            worker.subscribed = False
            
            time.sleep(120)
        
        if not worker.subscribed:
            
            worker.miner.mining = False
            
            extranonce1, extranonce_size = stratum_subscribe(client)
            if not extranonce1 or not extranonce_size:
                client.disconnect_pool()
                continue
            
            worker.extranonce1 = extranonce1
            worker.extranonce_size = extranonce_size
            
            # TODO: Make this optional in a way that the version mask can't be necessary
            stratum_configure(client)
            
            success_auth = stratum_authorize(client, worker.worker_name, worker.worker_pass)
            if not success_auth:
                client.disconnect_pool()
                continue
            
            stratum_suggest_difficulty(client, suggest_difficulty)
            worker.subscribed = True
        
        while client.connected():
            
            read = client.read_until_newline()
            
            if read == "":
                client.disconnect_pool()
                break
            
            method = stratum_parse_method(read)
            if method == STRATUM_PARSE_ERROR:
                print(f"[Notify] Error when parsing json: {read}")
            if method == MINING_NOTIFY:
                job = stratum_parse_notify(read)
                if job:
                    
                    worker.miner.job = job
                    
                    worker.extranonce2 = None
                    
                    worker.templates += 1
                    
                    worker.miner.mining = False
                    worker.miner.new_job = False
                    
                    calculate_mining_data(worker)
                    
                    print(f"[Notify] Initial header: {worker.miner.bytearray_blockheader.hex()}")
                    
                    worker.miner.pool_difficulty = current_difficulty
                    worker.miner.new_job = True
                    
            elif method == MINING_SET_DIFFICULTY:
                difficulty = stratum_parse_set_difficulty(read)
                if difficulty:
                    current_difficulty = difficulty
                    
                    worker.miner.pool_difficulty = current_difficulty
            elif method == VERSION_MASK:
                mask = stratum_parse_version_mask(read)
                if mask:
                    worker.miner.version_mask = mask
            elif method == STRATUM_SUCCESS:
                print("[Notify] Success when submiting!")
            else:
                print("[Notify] Unknown JSON")
        
        time.sleep(1)

def serve_forever(pool_host, pool_port, btc_address, worker_name, pool_pass, suggested_difficulty, stop_threads):
    
    client = Client(pool_host, pool_port)
    worker = Worker()
    
    worker.worker_name = f"{btc_address}.{worker_name}"
    worker.worker_pass = pool_pass
    
    threading.Thread(target=keep_alive, args=(client, worker, stop_threads), daemon=True).start()
    
    threading.Thread(target=run_miner, args=(0, client, worker, stop_threads), daemon=True).start()
    threading.Thread(target=run_miner, args=(1, client, worker, stop_threads), daemon=True).start()

    start_stratum(client, worker, suggested_difficulty)
        
def run_miner(miner_id, client: Client, worker: Worker, stop_thread):
    
    print(f"[MINER] Init hashing with miner: {miner_id}")
    
    while not stop_thread.is_set():
        
        miner: Miner = worker.miner
        
        if worker.miner == None or not worker.miner.new_job:
            time.sleep(0.05)
            continue
        
        miner.mining = True
        
        nonce = TARGET_NONCE - MAX_NONCE
        nonce += miner_id # Odd or even
        
        hash_count = 0
        start_time = time.time()
        
        print("[MINER] Started hashing nonces")
        while not stop_thread.is_set():
            
            if nonce > TARGET_NONCE:
                break
                
            if not miner.mining: 
                print("[MINER] MINER WORK ABORTED >> waiting new job") 
                break

            miner.bytearray_blockheader[76:80] = struct.pack('<I', nonce)
            
            hash_result = double_sha256(miner.bytearray_blockheader)
            hash_count += 1
        
            difficulty = diff_from_target(hash_result)
            
            if difficulty > worker.best_diff:
                worker.best_diff = difficulty
            
            if difficulty >= miner.pool_difficulty:
                
                # TODO: Calculate hashrate for all threads
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    hashes_per_second = hash_count / elapsed_time
                else:
                    hashes_per_second = 0
                
                print("[MINER] SHARE FOUND!")
                print(f"-> Nonce: {nonce}")
                print(f"-> Miner who found: {miner_id}")
                print(f"-> Share difficulty: {difficulty}")
                print(f"-> Pool difficulty: {miner.pool_difficulty}")
                print(f"-> Best difficulty: {round(worker.best_diff, 3)}")
                print(f"-> Hash: {hash_result[::-1].hex()}")                
                print(f"-> Hashrate (per thread): {hashes_per_second:.2f} H/s")
                
                stratum_submit(
                    client, 
                    worker.worker_name, 
                    miner.job.job_id, 
                    worker.extranonce2.zfill(8), 
                    miner.job.ntime,
                    f"{nonce:08x}",
                    miner.version_mask
                )
                
                hash_count = 0
                start_time = time.time()
            
            nonce += 2
        
        calculate_mining_data(worker)
        
        time.sleep(0.5)

def keep_alive(client, worker, stop_thread):
    SILENCE_LIMIT = 15000
    
    while not stop_thread.is_set():
        if client.check_pool_inactivity(SILENCE_LIMIT):
            print("[Keep Alive] Sending keep alive socket because 15 seconds without communication...")
            res = stratum_suggest_difficulty(client, worker.miner.pool_difficulty)
            if res == False:
                print("[Keep Alive] Error when sending keep alive socket")
            else:
                print("[Keep Alive] Keep alive socket sent with success")
        time.sleep(1)
    