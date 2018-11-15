# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 16:13:01 2018

@author: fangyucheng
"""


from multiprocessing import Pool
from crawler.crawler_sys.site_crawler import crawler_v_qq_async

pool = Pool(processes=8)
for line in range(8):
    pool.apply_async(crawler_v_qq_async.parse_video_page_single_process)
pool.close()
pool.join()