# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 14:19:00 2018

@author: fangyucheng
"""

import requests
import time
import asyncio
import re
import datetime
import json
import aiohttp
from bs4 import BeautifulSoup
##from crawler_sys.framework.video_fields_std import Std_fields_video
#from crawler_sys.utils.output_results import retry_get_url
from crawler.crawler_sys.utils.output_results import output_result
#from crawler_sys.utils.output_log import output_log
from crawler.crawler_sys.utils.trans_str_play_count_to_int import trans_play_count
from crawler.crawler_sys.utils import connect_with_redis

"""
'电影': 'http://v.qq.com/x/list/movie',
'电视剧': 'http://v.qq.com/x/list/tv',
'综艺': 'http://v.qq.com/x/list/variety',
'动漫': 'http://v.qq.com/x/list/cartoon',
'少儿': 'http://v.qq.com/x/list/children',
'纪录片': 'http://v.qq.com/x/list/doco',
'微电影': 'http://v.qq.com/x/list/dv',
"""

lst_page_url_dic = {'音乐': 'http://v.qq.com/x/list/music',
                    '新闻': 'http://v.qq.com/x/list/news',
                    '军事': 'http://v.qq.com/x/list/military',
                    '娱乐': 'http://v.qq.com/x/list/ent',
                    '体育': 'http://v.qq.com/x/list/sports',
                    '游戏': 'http://v.qq.com/x/list/games',
                    '搞笑': 'http://v.qq.com/x/list/fun',
                    '王者荣耀': 'http://v.qq.com/x/list/kings',
                    '时尚': 'http://v.qq.com/x/list/fashion',
                    '生活': 'http://v.qq.com/x/list/life',
                    '母婴': 'http://v.qq.com/x/list/baby',
                    '汽车': 'http://v.qq.com/x/list/auto',
                    '科技': 'http://v.qq.com/x/list/tech',
                    '教育': 'http://v.qq.com/x/list/education',
                    '财经': 'http://v.qq.com/x/list/finance',
                    '房产': 'http://v.qq.com/x/list/house',
                    '旅游': 'http://v.qq.com/x/list/travel'}


def dic_lst_to_file(listname, filename):
    file = open(filename, 'a')
    for line in listname:
        json_line = json.dumps(line)
        file.write(json_line)
        file.write('\n')
    file.flush()
    file.close()


def lst_page_task(target_channel=None,
                  page_num_max=34,
                  lst_page_url_dic=lst_page_url_dic):
    if target_channel is not None:
        target_url = lst_page_url_dic[target_channel]
        lst_page_url_dic = {target_channel: target_url}
    lst_page_task_lst = []
    videos_in_one_page = 30
    num_lst = []
    for i in range(0, page_num_max):
        num = i * videos_in_one_page
        num_lst.append(num)
    for key, value in lst_page_url_dic.items():
        task_url_lst_new = [value+'/?sort=5&offset='+ str(num) for num in num_lst]
        lst_page_task_lst.extend(task_url_lst_new)
        task_url_lst_hot = [value + '/?sort=40&offset=' + str(num) for num in num_lst]
        lst_page_task_lst.extend(task_url_lst_hot)
        task_url_lst_praise = [value+'/?sort=48&offset='+ str(num) for num in num_lst]
        lst_page_task_lst.extend(task_url_lst_praise)
    return lst_page_task_lst


def process_lst_page(resp):
    video_lst = []
    soup = BeautifulSoup(resp, 'html.parser')
    midstep = soup.find_all('li', {'class':'list_item'})
    for line in midstep:
        video_dic = {}
        url = line.a['href']
        find_play_count = BeautifulSoup(list(line)[-2], 'html.parser')
        play_count_str = find_play_count.find('span', {'class':'num'}).text.replace(' ', '')
        try:
            play_count = trans_play_count(play_count_str)
        except:
            play_count = 0
        video_dic = {"url": url,
                     "play_count": play_count}
        video_lst.append(video_dic)
    return video_lst


async def asynchronous_get_lst_page(session, url):
    get_page = await session.get(url)
    page = await get_page.text("utf-8", errors="ignore")
    return page

async def asynchronous_get_video_page(session, data_dic):
    url = data_dic['url']
    play_count = data_dic['play_count']
    get_page = await session.get(url)
    page = await get_page.text("utf-8", errors="ignore")
    return {'page': page, 'play_count': play_count, 'url': url}


def retry_get_lst_page(lsturl, 
                       retries_time=3):
    count = 0
    video_url_lst = []
    while count < retries_time:
        get_page = requests.get(lsturl)
        page = get_page.text
        video_url_lst = process_lst_page(resp=page)
        count += 1
        if video_url_lst != []:
            continue
    return video_url_lst


async def video_page(loop,
                     task_lst,
                     platform='腾讯视频',
                     output_to_file=True,
                     filepath='/home/fangyucheng/python_code',
                     output_to_es_raw=False,
                     es_index=None,
                     doc_type=None):
        async with aiohttp.ClientSession() as sess_video_page:
            task_video_page = [loop.create_task(asynchronous_get_video_page(sess_video_page, data_dic)) for data_dic in task_lst]
            video_result, unfinished = await asyncio.wait(task_video_page)
            video_page_download_result_lst = [v.result() for v in video_result]
            connect_with_redis.push_video_page_html_to_redis(result_lst=video_page_download_result_lst)
            print('success write into redis')



async def lst_page(loop,
                   task_lst,
                   platform='腾讯视频',
                   output_to_file=True,
                   filepath='/home/fangyucheng/python_code',
                   output_to_es_raw=False,
                   es_index=None,
                   doc_type=None):
    url_lst = []
    async with aiohttp.ClientSession() as sess_lst_page:
        task_video_page = [loop.create_task(asynchronous_get_lst_page(sess_lst_page, lst_url)) for lst_url in task_lst]
        lst_result, unfinished = await asyncio.wait(task_video_page)
        lst_page_download_result_lst = [v.result() for v in lst_result]
        for lst_html in lst_page_download_result_lst:
            url_lst_partial = process_lst_page(resp=lst_html)
            url_lst.extend(url_lst_partial)
        print("the length of url list is %s" % len(url_lst))
        connect_with_redis.push_url_dict_lst_to_redis(result_lst=url_lst)
        print('success write into redis')

#    for lsturl in task_lst:
#        print("current lsturl is %s" % lsturl)
#        video_url_lst = retry_get_lst_page(lsturl)
#        if video_url_lst == []:
#            continue
#        print("get %s page url list whose length is %s" % (lsturl, len(video_url_lst)))
#        async with aiohttp.ClientSession() as sess_video_page:
#            task_video_page = [loop.create_task(asynchronous_get_video_page(sess_video_page, data_dic)) for data_dic in video_url_lst]
#            video_result, unfinished = await asyncio.wait(task_video_page)
#            video_page_download_result_lst = [v.result() for v in video_result]
#            connect_with_redis.push_to_redis(result_lst=video_page_download_result_lst)
#            print('success write into redis')



#
#            for video_html in video_page_download_result_lst:
#            
#                #multiprocess.Pool here is not suitable, maybe push to redis is a good idea
#                video_data_dic = process_video_page(resp_dic=video_html)
#                print(video_data_dic)
#                final_result_lst.append(video_data_dic)
#                print("the length of video list is %s" % len(final_result_lst))
#                if len(final_result_lst) >= 100:
#                    output_result(result_Lst=final_result_lst,
#                                  platform=platform,
#                                  output_to_file=output_to_file,
#                                  filepath=filepath,
#                                  output_to_es_raw=output_to_es_raw,
#                                  es_index=es_index,
#                                  doc_type=doc_type)
#                    final_result_lst.clear()
#    if final_result_lst != []:
#        output_result(result_Lst=final_result_lst,
#                      platform=platform,
#                      output_to_file=output_to_file,
#                      filepath=filepath,
#                      output_to_es_raw=output_to_es_raw,
#                      es_index=es_index,
#                      doc_type=doc_type)


def process_video_page(resp_dic):
    url = resp_dic[b'url']
    url = url.decode("utf-8")
    play_count = resp_dic[b'play_count']
    play_count = play_count.decode("utf-8")
    page = resp_dic[b'page']
    page = page.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')
    try:
        soup_find = soup.find("script", {"r-notemplate": "true"})
        midstep = soup_find.text
        video_info_var_Lst = re.findall('var\s+VIDEO_INFO\s+=\s*{.+}', midstep)
    except:
        print("can't get info from video page")
        return None
    else:
        if video_info_var_Lst != []:
            video_info_var = video_info_var_Lst[0]
            video_info_json = re.sub('var\s+VIDEO_INFO\s+=\s*', '', video_info_var)
            try:
                video_info_dict = json.loads(video_info_json)
            except:
                print('Failed to transfer video_info_json to dict')
                video_info_dict = {}
            if video_info_dict != {}:
                try:
                    duration_str = video_info_dict['duration']
                    duration = int(duration_str)
                except:
                    duration = None
                try:
                    title = video_info_dict['title']
                except:
                    title = None
                try:
                    release_time_str = video_info_dict['video_checkup_time']
                    release_time_ts = int(datetime.datetime.strptime(release_time_str, 
                                                                     '%Y-%m-%d %H:%M:%S').timestamp()*1e3)
                except:
                    release_time_ts = None
        else:
            print('Failed to get video_info')
            return None
    try:
        releaser = soup.find('span', {'class': 'user_name'}).text
    except:
        releaser = None
        releaserUrl = None
    else:
        try:
            releaserUrl = soup.find('a', {'class': 'user_info'})['href']
        except:
            releaserUrl = None
    try:
        video_intro = soup.find('meta', {'itemprop': 'description'})['content']
    except:
        video_intro = None
    fetch_time = int(datetime.datetime.timestamp(datetime.datetime.now())*1e3)
    video_dict = {}
    video_dict['url'] = url
    video_dict['title'] = title
    video_dict['releaser'] = releaser
    video_dict['play_count'] = play_count
    video_dict['release_time'] = release_time_ts
    video_dict['duration'] = duration
    video_dict['fetch_time'] = fetch_time
    video_dict['releaserUrl'] = releaserUrl
    video_dict['video_intro'] = video_intro
    return video_dict


def parse_video_page_single_process(file_name='/home/fangyucheng/test'):
    result_lst = []
    task_lst = connect_with_redis.retrieve_video_html_from_redis()
    for raw_video_dic in task_lst:
        video_page = process_video_page(resp_dic=raw_video_dic)
        result_lst.append(video_page)
    dic_lst_to_file(listname=result_lst, filename=file_name)
    return result_lst


def run_lst_page_asyncio():
    start = time.time()
    task_lst = lst_page_task(target_channel='旅游')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(lst_page(loop, task_lst=task_lst))
    cost_time = time.time() - start
    print("the total cost of time is %s" % str(cost_time))


def run_video_page_asyncio():
    start = time.time()
    task_lst = connect_with_redis.retrieve_url_dict_from_redis()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(video_page(loop, task_lst=task_lst))
    cost_time = time.time() - start
    print("the total cost of time is %s" % str(cost_time))





if __name__ == "__main__":
    #parse_video_page_single_process()
    start = time.time()
    run_video_page_asyncio()
    #run_video_page_asyncio()
    cost = time.time() - start
    print("the cost of time is %s" % cost)