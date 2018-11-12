# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 19:03:43 2018

@author: fangyucheng
"""

import argparse
import configparser
from crawler.crawler_sys.framework.platform_crawler_register import get_crawler

arg_parse = argparse.ArgumentParser(description="crawler for video website list page")
arg_parse.add_argument('-p', '--platform', default='腾讯视频', type=str, help=('a platform must be input'))
arg_parse.add_argument('-c', '--conf', default='/home/hanye/crawlers/crawler_sys/utils/list_page_conf.ini',
                       type=str, help=('absolute path of conf file'))
args = arg_parse.parse_args()

config = configparser.ConfigParser()
config.read(filenames=args.conf)
platform = args.platform

task_lst = config[platform]