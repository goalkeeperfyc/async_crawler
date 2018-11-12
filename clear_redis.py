# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 16:29:49 2018

@author: fangyucheng
"""

import redis 

rds = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

rds.flushdb()