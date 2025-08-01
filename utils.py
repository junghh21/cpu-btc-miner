#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:10:04 2024

@author: j.nacaratti
"""

import random
import time
import hashlib
import struct

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

def le256todouble(target):
	dcut64 = struct.unpack_from('<Q', target, 24)[0] * 6277101735386680763835789423207666416102355444464034512896.0
	dcut64 += struct.unpack_from('<Q', target, 16)[0] * 340282366920938463463374607431768211456.0
	dcut64 += struct.unpack_from('<Q', target, 8)[0] * 18446744073709551616.0
	dcut64 += struct.unpack_from('<Q', target, 0)[0]
	return dcut64

def diff_from_target(target):
	TRUEDIFFONE = 26959535291011309493156476344723991336010898738574164086137773096960.0
	dcut64 = le256todouble(target)
	if dcut64 == 0:
		dcut64 = 1
	return TRUEDIFFONE / dcut64

def get_share_target(difficulty):
	TRUEDIFFONE = 26959535291011309493156476344723991336010898738574164086137773096960.0
	return int(TRUEDIFFONE / difficulty)

def double_sha256(data):
	return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def merkle_root(coinbase_tx_hash, merkle_branches):
	current_hash = bytes.fromhex(coinbase_tx_hash)
	for branch in merkle_branches:
		branch_hash = bytes.fromhex(branch)
		# Concatenate the hashes and compute the double SHA-256 hash
		current_hash = double_sha256(current_hash + branch_hash)
	return current_hash.hex()

def calculate_mining_data(worker):
	
	miner = worker.miner
	mine_job = worker.miner.job
	if not mine_job:
		return
	
	# Calculating target
	exponent = int(mine_job.nbits[:2], 16)
	significand = mine_job.nbits[2:]
	
	target = significand + ('00' * (exponent - 3))
	target = target.zfill(64)
	#print("[Header] Target: ", target)
	
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
	#print("[Header] Coinbase: ", coinbase)
	#print("[Header] Extranonce1: ", worker.extranonce1)
	#print("[Header] Extranonce2: ", worker.extranonce2)
	
	coinbase_tx = double_sha256(bytes.fromhex(coinbase)).hex()
	
	# Calculating Merkle Root
	merkle_r = merkle_root(coinbase_tx, mine_job.merkle_branch)
	miner.merkle_result = merkle_r
	
	#print("[Header] Merkle root:", merkle_r)
	
	# Changing version
	version_int = int(mine_job.version, 16)
	versionmask_int = 0#int(miner.version_mask, 16)
	
	new_version_int = version_int | versionmask_int
	new_version_hex = f"{new_version_int:08x}"
	
	#print("[Header] New version:", new_version_hex)
	
	# Building block header in big endian
	blockheader = (
		new_version_hex +
		mine_job.prev_block_hash + 
		merkle_r +
		mine_job.ntime +
		mine_job.nbits +
		"00000000"  # Starting nonce
	)
	#print("[Header] Blockheader:", blockheader)
	
	blockheader_bytes = bytes.fromhex(blockheader)
	miner.bytearray_blockheader = bytearray(blockheader_bytes)

	# Inverting version (4 bytes)
	miner.bytearray_blockheader[0:4] = miner.bytearray_blockheader[0:4][::-1]
	
	# Inverting prevhash (swaping words of 4 bytes)
	prevhash = miner.bytearray_blockheader[4:36]
	swapped_prevhash = bytearray()
	for i in range(0, len(prevhash), 4):
		word = prevhash[i:i+4][::-1]
		swapped_prevhash.extend(word)
	miner.bytearray_blockheader[4:36] = swapped_prevhash
	#print("[Header] Prev hash:", miner.bytearray_blockheader[4:36].hex())
	 
	# Inverting timestamp (4 bytes)
	miner.bytearray_blockheader[68:72] = miner.bytearray_blockheader[68:72][::-1]
	
	# Inverting difficulty (4 bytes)
	miner.bytearray_blockheader[72:76] = miner.bytearray_blockheader[72:76][::-1]






