#! /usr/bin/python3
# coding:utf-8

#  修改自：
#  免登录下载微博图片 爬虫 Download Weibo Images without Logging-in
#  https://github.com/yAnXImIN/weiboPicDownloader

import json
import os
from multiprocessing import Pool

import requests

NICKNAMES_FILE = 'weibo_nicknames.txt'
URL_TEMPLATE_PAGE = 'https://m.weibo.cn/api/container/getIndex?count=100&containerid={}&page={}'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


def get(url, stream=False, allow_redirects=True):
    print(url)
    return requests.get(url=url, headers=HEADERS, allow_redirects=allow_redirects)


def save_image(nickname, url):
    save_path = os.path.join('WeiboAlbum', "WeiboAlbum_" + nickname)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    image_path = os.path.join(save_path, nickname + '_' + url.split('/')[-1])
    if os.path.isfile(image_path):
        print("File already exists: " + image_path)
        return
    response = get(url=url, stream=True)
    image = response.content
    try:
        with open(image_path, "wb") as image_object:
            image_object.write(image)
    except IOError as err:
        print("IO Error\n:", str(err))


def get_urls(containerid, page):
    url = URL_TEMPLATE_PAGE.format(containerid, page)
    resp_text = get(url=url).text
    json_data = json.loads(resp_text)
    cards = json_data['cards']
    if not cards:
        return None
    photos = []
    for card in cards:
        mblog = card.get('mblog')
        if mblog:
            pics = mblog.get('pics')
            if pics:
                photos.extend([pic.get('large').get('url') for pic in pics])
    return photos


def nickname_to_containerid(nickname):
    url = "http://m.weibo.com/n/{}".format(nickname)
    resp = get(url, allow_redirects=False)
    cid = resp.headers['Location'][27:]
    return '107603{}'.format(cid)


def read_nicknames():
    nicknames = []
    with open(NICKNAMES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            nicknames.extend(line.split(' '))
    return nicknames


def handle_user(nickname):
    cid = nickname_to_containerid(nickname)
    if not cid:
        return
    all = []
    page = 0
    has_more = True
    while has_more:
        page += 1
        urls = get_urls(containerid=cid, page=page)
        has_more = bool(urls)
        if has_more:
            all.extend(urls)
    count = len(all)
    for index, url in enumerate(all):
        print('{} {}/{}'.format(nickname, index, count))
        pool.apply_async(save_image, args=(nickname, url))


def main():
    for nickname in read_nicknames():
        handle_user(nickname.strip())


if __name__ == '__main__':
    pool = Pool()
    try:
        main()
    except Exception as err:
        print('Exception:\n', str(err))
    finally:
        pool.close()
        pool.join()
