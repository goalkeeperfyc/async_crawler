# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 00:38:51 2018

@author: fangyucheng
"""

import redis

rds = redis.StrictRedis(host='127.0.0.1', port=6379)

def push_url_dict_lst_to_redis(result_lst):
    for line in result_lst:
        url = line['url']
        rds.hmset(name=url,
                  mapping=line)

#test
#if __name__ == "__main__":
#    result_lst = [{'ddd':'123'}, {'eee':'456'}]
#    push_to_redis(result_lst)
    