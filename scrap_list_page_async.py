# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 19:03:43 2018

@author: fangyucheng
"""

import argparse
import configparser
from crawler.crawler_sys.framework.platform_crawler_register import get_crawler

parser = argparse.ArgumentParser(description="crawler for video website list page")
parser.add_argument('-p', '--platform', default='腾讯视频', type=str, help=('a platform must be input'))
parser.add_argument('-c', '--conf', default='/home/hanye/crawlers/crawler_sys/utils/list_page_conf.ini',
                       type=str, help=('absolute path of config file'))
parser.add_argument('-ch', '--channel', default=[], action='append', type=str,
                       help=('input all of the channel you want to scrap, while no input means all channels'))
parser.add_argument('-f', '--output_file_path', default=None, type=str,
                    help=('Specify output file path, default None.'))
parser.add_argument('-f', '--output_file_path', default=None, type=str,
                    help=('Specify output file path, default None.'))
parser.add_argument('-w', '--output_to_es_raw', default='True', type=str,
                    help=('Write data into es or not, default to True'))
parser.add_argument('-g', '--output_to_es_register', default='True', type=str,
                    help=('Write data into es or not, default to True'))
parser.add_argument('-s', '--processes_num', default=20, type=int,
                    help=('Processes number to be used in multiprocessing'))
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(filenames=args.conf)
platform = args.platform

crawler_got = get_crawler(platform)
crawler_initialization = crawler_got()

if args.output_file_path is None:
    output_to_file = False
    filepath = None
else:
    output_to_file = True
    filepath = args.output_file_path

output_to_es_raw = args.output_to_es_raw
output_to_es_register = args.output_to_es_register

para_dic = {'output_to_file': output_to_file,
            'filepath': filepath,
            'output_to_es_raw': output_to_es_raw,
            'output_to_es_register': output_to_es_register}

task_dic = config[platform]
task_lst = []
target_channel = args.channel
if target_channel != []:
    for channel in target_channel:
        task_lst.append(task_dic[channel])
else:
    task_lst = [value for key,value in task_dic.items()]

for task in task_lst:
    crawler_initialization.run_lst_page_asyncio(lst_page_url=task)
    crawler_initialization.run_video_page_asyncio()
    crawler_initialization.parse_video_page_multiprocess(para_dic)