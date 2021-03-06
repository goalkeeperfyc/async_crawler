# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 00:38:51 2018

@author: fangyucheng
"""

import redis

rds = redis.StrictRedis(host='127.0.0.1', port=6379)

def push_to_redis(result_lst):
    name = 1
    for line in result_lst:
        rds.hmset(name=str(name),
                  mapping=line)
        name += 1