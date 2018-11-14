# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 09:10:25 2018

@author: fangyucheng
"""

import time
import redis
from crawler.crawler_sys.site_crawler import crawler_v_qq_async

rds = redis.StrictRedis(host='192.168.17.60', port=6379, db=13)
while True:
    if rds.llen('urldict') > 0:        
        crawler_v_qq_async.run_video_page_asyncio()
    else:
        print("there is no data in redis")
        time.sleep(5)