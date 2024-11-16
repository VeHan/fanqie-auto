import re
import urllib.parse

import requests
import json

from douyin_api import DouyinApi
from fanqie_api import FanqieApi

douyin_api = DouyinApi()
fanqie_api = FanqieApi()

def main():
    fanqie_api.login()
    books = fanqie_api.get_content_tab()
    for book in books:
        videos = douyin_api.search(book['book_name'])
        for video in videos:
            desc = video['aweme_info']['desc']
            keywords = filter_keywords(list(t for t in desc.split('#')))
            fanqie_api.apply(book, keywords)

def filter_keywords(keywords: []):
    result = []
    for keyword in keywords:
        keyword = remove_non_chinese(keyword)
        if keyword is None or keyword == '':
            continue
        if is_black(keyword):
            continue
        result.append(keyword)
    return result


def is_black(keyword):
    blacklist = ['短剧', '小说', '推文', '漫画', '抖音', '新剧']
    for black in blacklist:
        if black in keyword:
            return True
    return False

def remove_non_chinese(text):
    # 创建一个空字符串来存储结果
    cleaned_text = ''

    # 遍历文本的每个字符
    for char in text:
        # 检查字符是否是中文字符（这里只检查了基本区的中文字符）
        # 你可以根据需要扩展这个范围，包括其他Unicode区块的中文字符
        if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4DBF':
            cleaned_text += char

    return cleaned_text

if __name__ == '__main__':
    main()
