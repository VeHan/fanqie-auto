import json
import threading
import time
import traceback
from datetime import datetime, timedelta

from config import config
from douyin_api import DouyinApi
from fanqie_api import FanqieApi, ApplyWordLimitException, content_tab_config
from log_config import logger

douyin_api = DouyinApi()


def main():
    for content_tab_config_item in content_tab_config:
        genre_map = content_tab_config_item['genre']
        platform = content_tab_config_item['platform']
        content_tab = content_tab_config_item['content_tab']
        worker = Worker()
        worker.login(config['username'], config['password'])
        for genre in genre_map:
            apply_word_thread = threading.Thread(target=Worker.apply_words,
                                                 name=f'ApplyWordThread-{platform}-{genre_map[genre]}',
                                                 args=(worker, {
                                                     'content_tab': content_tab,
                                                     'genre': genre,
                                                 },)
                                                 )
            apply_word_thread.start()

        huitian_thread = threading.Thread(target=Worker.huitian, name='HuiTianThread',
                                          args=(worker, {
                                              'content_tab': content_tab,
                                          },)
                                          )
        huitian_thread.start()


def relogin():
    pass


class Worker:
    def __init__(self):
        self.fanqie_api = FanqieApi()
        pass

    def login(self, username, password):
        self.fanqie_api.login(username, password)

    def apply_words(self, config):
        logger.info(config)
        page_index = 1
        while True:
            try:
                books = self.fanqie_api.get_content_tab(config['content_tab'], config['genre'], page_index)
                for book in books:
                    time.sleep(5)
                    self.apply_work_for_book(book, config['content_tab'])
                if books:
                    page_index += 1
                else:
                    # 从头开始
                    page_index = 1
            except ApplyWordLimitException:
                sleep_seconds = tomorrow().timestamp() - datetime.now().timestamp()
                logger.info("申词被限制，将在明日凌晨继续申词, sleep %s 秒", sleep_seconds)
                time.sleep(sleep_seconds)
            except Exception as e:
                logger.error("apply words 出错")
                traceback.print_exc()
            finally:
                time.sleep(60)

    def apply_work_for_book(self, book, content_tab):
        logger.info("------------------------")
        logger.info(f'扫描到内容 book_id={book["book_id"]} book_name={book["book_name"]}')
        try:
            book_split = book['book_name'].split("，")
            videos = []
            for book_split_item in book_split:
                videos.extend(douyin_api.search(book_split_item))
            logger.info("搜索到视频数量 %s", len(videos))
            all_keywords = set()
            for video in videos:
                if 'aweme_info' not in video:
                    continue
                desc = video['aweme_info']['desc']
                keywords = filter_keywords(list(t for t in desc.split('#')), book['book_name'])
                if not keywords:
                    continue
                all_keywords = all_keywords.union(keywords)
            self.fanqie_api.apply(book, all_keywords, content_tab)
        except ApplyWordLimitException:
            raise
        except Exception as e:
            traceback.print_exc()
            logger.error("apply_work_for_book出错", )
        finally:
            logger.info("------------------------")

    def huitian(self, config):
        page_index = 0
        while True:
            try:
                promotions = self.fanqie_api.get_promotions(config['content_tab'], page_index)
                if not promotions:
                    page_index = 1
                    continue
                for promotion in promotions:
                    self.huitian_promotion(promotion)
                    time.sleep(3)
                page_index += 1
            except Exception as e:
                traceback.print_exc()
                logger.error("huitian error")
            finally:
                time.sleep(10)

    def huitian_promotion(self, promotion):
        try:
            logger.info("----------------------")
            alias_name = promotion['alias_name']
            book_name = promotion['book_name']
            alias_id = promotion['alias_id']
            book_id = promotion['book_id']
            alias_type = promotion['task_type']
            logger.info(
                f'尝试回填 alias_id:{alias_id}, alias_name:{alias_name}, book_id:{book_id},book_name:{book_name}')
            alias_ctime = datetime.strptime(promotion['create_time'], '%Y-%m-%d %H:%M:%S').timestamp()
            target_video = None
            videos = douyin_api.search(book_name, recent=True)
            if not videos:
                videos = douyin_api.search(alias_name, recent=True)

            for video in videos:
                # 回填发文时间必须晚于申词时间
                if ('aweme_info' in video and video['aweme_info']
                        and video['aweme_info'] and video['aweme_info']['create_time'] < alias_ctime):
                    continue
                target_video = video
                break
            if target_video is None:
                logger.info('未找到符合条件的视频')
            else:
                logger.info("已找到符合条件的视频")
                self.fanqie_api.huitian(alias_id,
                                        f'https://www.douyin.com/video/{target_video['aweme_info']['aweme_id']}',
                                        alias_type)
        except Exception as e:
            traceback.print_exc()
            logger.info('回填出错')
        finally:
            logger.info("----------------------")


def filter_keywords(keywords: [], book_name):
    result = []
    for keyword in keywords:
        keyword = remove_non_chinese(keyword)
        if keyword is None or keyword == '':
            continue
        if is_black(keyword):
            continue
        if len(keyword) > 8 or len(keyword) < 4:
            continue
        if keyword.startswith(book_name[0:3]):
            continue
        result.append(keyword)
    return result


def is_black(keyword):
    blacklist = ['短剧', '小说', '推文', '漫画', '抖音', '新剧', '动画', '一口气看完', "剧场", "好剧", "影视"]
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


def tomorrow():
    now = datetime.now()

    # 计算明天的时间，并设置为凌晨0点
    tomorrow = now + timedelta(days=1)
    midnight_tomorrow = tomorrow.replace(hour=1, minute=0, second=0, microsecond=0)
    return midnight_tomorrow


if __name__ == '__main__':
    main()
