# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 00:38:51 2018

@author: fangyucheng
"""


import json
#import time
import redis


rds = redis.StrictRedis(host='192.168.17.60', port=6379, db=13)


def push_lst_to_redis(key, result_lst):
    """
    push a list of url(only url, type str) into a redis list
    """
    for line in result_lst:
        rds.lpush(key, line)
    print("the length of %s is %s" % (key, rds.llen(key)))

def retrieve_url_from_redis(key, retrieve_count=30):
    count = 0
    result_lst = []
    while retrieve_count > count:
        if count %2 == 0:
            url = rds.rpop(key)
            count += 1
            result_lst.append(url)
        else:
            url = rds.lpop(key)
            result_lst.append(url)
        if url is None:
            return result_lst
    return result_lst


def push_lst_page_html_to_redis(result_lst):
    for line in result_lst:
        rds.lpush('lst_page_html', line)
    print("the length of lst_page_html is %s" % rds.llen('lst_page_html'))

def retrieve_lst_page_html_from_redis():
    lst_page_html_byte = rds.rpop('lst_page_html')
    lst_page_html_str = lst_page_html_byte.decode("utf-8").replace("\'", "\"")
    return lst_page_html_str


def push_url_dict_lst_to_redis(result_lst):
    for line in result_lst:
        rds.lpush('urldict', line)
    print("the length of urldict list is %s" % rds.llen('urldict'))

def retrieve_url_dict_from_redis(retrieve_count=90):
    count = 0
    result_lst = []
    while retrieve_count > count:
        url_dic_bytes = rds.rpop('urldict')
        if url_dic_bytes is None:
            print("total output %s url dicts" % len(result_lst))
            return result_lst
        else:
            url_dic_str = url_dic_bytes.decode('utf-8').replace("\'", "\"")
            url_dic = json.loads(url_dic_str)
            count += 1
            result_lst.append(url_dic)
    print("total output %s url dicts" % len(result_lst))
    return result_lst


def push_video_page_html_to_redis(result_lst):
    for line in result_lst:
        rds.lpush('videopagehtml', line)
    print("the length of videopagehtml list is %s" % rds.llen('videopagehtml'))

def retrieve_video_html_from_redis():
    video_html_bytes = rds.rpop('videopagehtml')
    video_html_str = video_html_bytes.decode("utf-8").replace("\'", "\"")
    return video_html_str


def length_of_lst(lst_key):
    """
    To get the length of a redis list
    """
    length = rds.llen(lst_key)
    return length


def push_error_html_to_redis(error_page):
    """
    Used for asynchronous crawler, to push error list page into redis
    """
    rds.lpush('error', error_page)



"""
this part is for renew video data
"""

platform_redis_list_reg = {'toutiao': 'toutiao_url_list',
                           '腾讯视频': 'v_qq_url_list',
                           'youku': 'youku_url_list',
                           'iqiyi': 'iqiyi_url_list',
                           }


def retrieve_video_url_from_redis(platform, retrieve_count=90):
    count = 0
    result_lst = []
    redis_key = platform_redis_list_reg[platform]
    while retrieve_count > count:
        url_dic_bytes = rds.spop(redis_key)
        if url_dic_bytes is None:
            print("total output %s urls" % len(result_lst))
            return result_lst
        else:
            url_dic_str = url_dic_bytes.decode('utf-8').replace("\'", "\"")
            url_dic = json.loads(url_dic_str)
            count += 1
            result_lst.append(url_dic)
    print("total output %s urls" % len(result_lst))
    return result_lst
