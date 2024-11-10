#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 23:44:02 2024

@author: j.nacaratti
"""

class MineJob:
    def __init__(self, job_id, prev_block_hash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs):
        self.job_id = job_id
        self.prev_block_hash = prev_block_hash
        self.coinb1 = coinb1
        self.coinb2 = coinb2
        self.merkle_branch = merkle_branch
        self.version = version
        self.nbits = nbits
        self.ntime = ntime
        self.clean_jobs = clean_jobs
