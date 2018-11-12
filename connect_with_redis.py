# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 00:38:51 2018

@author: fangyucheng
"""

import time
import redis


def push_url_dict_lst_to_redis(result_lst):
    rds = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    for line in result_lst:
        url = line['url']
        rds.hmset(name=url,
                  mapping=line)


def retrieve_url_dict_from_redis():
    result_lst = []
    rds = redis.StrictRedis(host='127.0.0.1', port=6379)
    rds_scan = rds.scan(count=100)
    key_lst = rds_scan[1]
    for key in key_lst:
        url_dic = rds.hgetall(key)
        result_lst.append(url_dic)
        print(url_dic)
    return result_lst

def push_video_page_html_to_redis(result_lst):
    rds = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
    for line in result_lst:
        url = line['url']
        rds.hmset(name=url,
                  mapping=line)
#test
if __name__ == "__main__":
    start = time.time()
    retrieve_url_dict_from_redis()
    cost = time.time() - start
    print("the cost of time is %s" % cost)
    #    result_lst = [{'ddd':'123'}, {'eee':'456'}]
#    push_to_redis(result_lst)
    