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


def retrieve_url_dict_from_redis(count=100):
    result_lst = []
    rds = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    rds_scan = rds.scan(count=count)
    key_lst = rds_scan[1]
    for key in key_lst:
        url_dic = rds.hgetall(key)
        result_lst.append(url_dic)
    print("total output %s url dicts" % len(result_lst))
    return result_lst

def push_video_page_html_to_redis(result_lst):
    rds = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
    for line in result_lst:
        url = line['url']
        rds.hmset(name=url,
                  mapping=line)

def retrieve_video_html_from_redis(count=100):
    result_lst = []
    rds = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
    rds_scan = rds.scan(count=count)
    key_lst = rds_scan[1]
    for key in key_lst:
        video_html_dic = rds.hgetall(key)
        print(key)
        #print(video_html_dic)
        result_lst.append(video_html_dic)
    #print(video_html_dic)
    return result_lst


#test
if __name__ == "__main__":
    start = time.time()
    result_lst = retrieve_video_html_from_redis()
    cost = time.time() - start
    print("the cost of time is %s" % cost)
    #    result_lst = [{'ddd':'123'}, {'eee':'456'}]
#    push_to_redis(result_lst)
    