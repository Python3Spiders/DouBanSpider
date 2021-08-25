# -*- coding: utf-8 -*-
# author:           inspurer(月小水长)
# create_time:      2021/8/24 8:25
# 运行环境           Python3.6+
# github            https://github.com/inspurer
# 微信公众号         月小水长

# todo: add proxy

import requests

from lxml import etree

from time import sleep

HEADERS_LIST = [
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13',
    'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre'
]

timeout = 10

import random

import traceback

'''
没把 cookie 配置在文件中的原因是
json 只能双引号包裹，cookie 中就有双引号，懒得转义，容易出错，直接放在 python 的单引号中，
'''

Cookie = 'bidxxxxx 改成你自己的 cookie, path 是 statues'
def get_user_status(user_url='https://www.douban.com/people/170796758'):
     # todo status 详情里的回应内容，转发，点赞数
    global config_json
    statuses_url = f'{user_url}/statuses'

    result_json = []
    title = None
    params = {
        'p': cur_user_cur_page_index
    }
    while True:

        try:
            response = requests.get(url=statuses_url, headers={'User-Agent': random.choice(HEADERS_LIST), 'Cookie': Cookie},
                                timeout=timeout, params=params)
        except:
            print(traceback.format_exc())
            break

        if response.status_code == 403:
            print('被识别出爬虫了，请打开豆瓣网页填写验证码')

            config_json['cur_user_cur_page_index'] = params['p']
            saveConfig()

            saveData(result_json, title)

            import sys
            sys.exit(0)

        html = etree.HTML(response.text.encode(response.encoding).decode('utf-8'))

        if not title:
            title = html.xpath('//title/text()')[0].strip()

        search_items = html.xpath('//div[@class="stream-items"]/div[starts-with(@class,"new-status status-wrapper")]')

        if len(search_items) == 0:
            if params['p'] <= 1:
                print(f'如果 {statuses_url} 主页有数据的话，请留意 cookie 是否失效')
            print('爬完了')
            break

        for si in search_items:

            if len(si.xpath('.//span[@class="reshared_by"]')) > 0 or len(si.xpath('.//div[contains(@class, "reshared")]')) > 0:
                # todo
                print('转发的暂不处理')
                continue


            created_at = si.xpath('.//span[@class="created_at"]/@title')[0]

            status_url = si.xpath('.//div[@class="hd "]/@data-status-url')[0]

            status_text = si.xpath('.//div[@class="text"]')[0].xpath('string(.)').strip()

            if '看过' in status_text or '在看' in status_text or '想看' in status_text:
                # 电影
                status_movie = si.xpath('.//div[@class="content"]/div[@class="title"]/a')[0]
                status_movie_title = status_movie.xpath('./text()')[0]
                status_movie_url = status_movie.xpath('./@href')[0]
                result_json.append({
                    'created_at':  created_at,
                    'status_type': 'movie',
                    'status_url': status_url,
                    'status_text': status_text,
                    'status_movie_title': status_movie_title,
                    'status_movie_url': status_movie_url,
                })
                print(status_url, status_text, status_movie_title, status_movie_url, '\n')
            elif '说:' in status_text:
                # 单纯的说说
                try:
                    status_saying = si.xpath('.//div[@class="status-saying"]/blockquote/p/text()')[0]
                except:
                    # 纯图片
                    status_saying = ''
                pic_group = si.xpath(
                    './/div[starts-with(@class,"attachments-saying group-pics")]/span[starts-with(@class,"group-pic")]')
                pic_url_list = []
                if len(pic_group) > 0:
                    print(status_url, len(pic_group))
                    for pic in pic_group:
                        pic_url = pic.xpath('./img/@data-original-url')[0]
                        pic_url_list.append(pic_url)
                result_json.append({
                    'created_at':  created_at,
                    'status_type': 'saying',
                    'status_url': status_url,
                    'status_text': status_text,
                    'status_saying': status_saying,
                    'status_pic_list': pic_url_list,
                })
                print(status_saying, pic_url_list, '\n')
            elif '听过' in status_text or '在听' in status_text or '想听' in status_text:
                # 音乐，解析其实和电影一样
                status_music = si.xpath('.//div[@class="content"]/div[@class="title"]/a')[0]
                status_music_title = status_music.xpath('./text()')[0]
                status_music_url = status_music.xpath('./@href')[0]
                result_json.append({
                    'created_at':  created_at,
                    'status_type': 'music',
                    'status_url': status_url,
                    'status_text': status_text,
                    'status_music_title': status_music_title,
                    'status_music_url': status_music_url,
                })
                print(status_url, status_text, status_music_title, status_music_url, '\n')
            elif '关注了话题' in status_text:
                status_topic = si.xpath('.//div[@class="content"]/div[starts-with(@class,"title")]/a')[0]
                status_topic_title = status_topic.xpath('./text()')[0]
                status_topic_url = status_topic.xpath('./@href')[0]
                result_json.append({
                    'created_at':  created_at,
                    'status_type': 'topic',
                    'status_url': status_url,
                    'status_text': status_text,
                    'status_topic_title': status_topic_title,
                    'status_topic_url': status_topic_url,
                })
                print(status_url, status_text, status_topic_title, status_topic_url, '\n')
            elif '读过' in status_text or '在读' in status_text or '想读' in status_text:
                # 书，解析其实和电影一样
                status_book = si.xpath('.//div[@class="content"]/div[@class="title"]/a')[0]
                status_book_title = status_book.xpath('./text()')[0]
                status_book_url = status_book.xpath('./@href')[0]
                result_json.append({
                    'created_at':  created_at,
                    'status_type': 'topic',
                    'status_url': status_url,
                    'status_text': status_text,
                    'status_book_title': status_book_title,
                    'status_book_url': status_book_url,
                })
                print(status_url, status_text, status_book_title, status_book_url, '\n')

        params['p'] = params['p'] + 1

        if params['p'] % 5 == 0:
            print(' saving per 5 page ')
            saveData(result_json, title)

        print(f'\n\n\n parsing page  {params["p"]}\n\n\n')

        sleep(3)
    saveData(result_json, title)


import os
import json
config_path = 'user_config.json'
def loadConfig():
    # 加载入参
    if not os.path.exists(config_path):
        raise Exception(f"没有配置文件 {config_path}")
    with open(config_path, 'r', encoding='utf-8-sig') as f:
        config_json = json.loads(f.read())
    return config_json


def saveConfig():
    # 保存配置
    with open(config_path, 'w', encoding='utf-8-sig') as f:
        f.write(json.dumps(config_json, indent=2, ensure_ascii=False))


data_path = 'output'
if not os.path.exists(data_path):
    os.mkdir(data_path)
def saveData(data, title):
    data_file = os.path.join(data_path, f'{title}.json')
    with open(data_file, 'w+', encoding='utf-8-sig') as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    global config_json, cur_user_index, cur_user_cur_page_index
    config_json = loadConfig()
    # 待爬取的用户列表
    users = config_json.get('users', None)
    # 当前爬取到哪一个用户了
    cur_user_index = config_json.get('cur_user_index', None)
    # 当前爬取的用户到哪一页了
    cur_user_cur_page_index = config_json.get('cur_user_cur_page_index', None)
    # 用户列表还没爬完
    while cur_user_index <= len(users):
        cur_user = users[cur_user_index]
        try:
            get_user_status(cur_user)
            # get_user_status('https://www.douban.com/people/G16022222')
            cur_user_index += 1
        except:
            print(traceback.format_exc())
            config_json['cur_user_index'] = cur_user_index
            saveConfig()
            break
