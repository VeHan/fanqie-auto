import json
import time
import traceback
import urllib
from threading import Lock

from proxy import proxies
from log_config import logger

import requests

from a_b import get_ab

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
content_tab_config = [
    # {
    #     'app_name': "danhua",
    #     'platform': "蛋花",
    #     'content_tab': 10,
    #     'genre': {
    #         203: '短剧',
    #         0: '网文',
    #         8: '短故事'
    #     },
    #     'alias_type': 8
    # },
    {
        "app_name": "novelread",
        "platform": "红果",
        'content_tab': 6,
        'genre': {
            203: '全部内容'
        },
        'alias_type': 5
    },
    {

        "app_name": "novel_fm",
        "platform": "番茄畅听",
        'content_tab': 3,
        'genre': {
            203: '短剧',
            0: '网文',
            4: '有声书',
        },
        'alias_type': 2
    },
    {
        'app_name': 'fanqie_novel',
        "platform": "番茄小说",
        'content_tab': 2,
        'genre': {
            203: '短剧',
            0: '网文',
            1: '漫画',
            4: '有声书',
        },
        'alias_type': 1
    }
]


def get_content_tab_config(content_tab):
    for config_item in content_tab_config:
        if config_item['content_tab'] == content_tab:
            return config_item


def dump(data):
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)


class ApplyWordLimitException(Exception):
    pass


class FanqieApi:
    def __init__(self):
        self.session = requests.session()
        self.session.proxies.update(proxies)
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://promoter.fanqieopen.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://promoter.fanqieopen.com/page/affiliate/task?share_token=Wg6DsvGE',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UA
        }
        self.lock = Lock()

    def login(self, username, password):
        # 定义请求的URL和查询参数
        params = 'app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=9P0QEeqlkQ_5o-iXDSRJXp8aSMYVeM_P-jZCsxIGHaL4oCYbNP1hk7fxH-vx6cZtl67LCZ_RHx2gI6mp9tNe-04lJWq5If23hspCjDuio9nHeST2_nU-QsT3z4O3_U6RfU_BRr3vGCPSGDb0OIz7tqVz072RMd4yHAG92DM2'
        url = 'https://promoter.fanqieopen.com/api/platform/user/invite_code/log_in/v:version?'

        # 定义请求的数据体
        data = {
            'share_token': username,
            'invite_code': password
        }
        body = dump(data)
        ab = get_ab(params, body, UA)
        url_ab = f'{url}{params}&a_bogus={ab}'
        response = self.session.post(url_ab, headers=self.headers, data=body)

        if response.json()['code'] != 0:
            raise Exception("登录失败")
        logger.info("登录成功")

    def get_content_tab(self, content_tab, genre, index):
        # 定义请求的URL和查询参数
        params = 'content_tab={content_tab}&genre={genre}&page_index={page_index}&page_size={page_size}&app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=pa0dxaomNn3nJ-a0kNH9XOh2tO1M-YSQuu0X3gVAqf80sQijY1QfpFO1VvDFZuHvhcDI0OwNpslorB-S8GVTZnvgmBmwYh1HiQM-x3CiE3SvA5MPzLqNWpwHeKgy3DR0L-5she-Y13j79iaPZEK8v02HmzA94t-FrY2qB6L5'
        url = 'https://promoter.fanqieopen.com/api/platform/content/book/list/v:version?'
        params = params.format_map({
            'content_tab': content_tab,
            'page_index': index,
            'page_size': 10,
            'genre': genre
        })
        ab = get_ab(params, None, UA)
        url_ab = f'{url}{params}&a_bogus={ab}'
        response = self.session.get(url_ab, headers=self.headers)

        json = response.json()
        if json['code'] != 0:
            logger.info("获取失败 %s", json)
            return []
        else:
            book_list = json['data']['book_list']
            return book_list

    def apply(self, book, keywords, content_tab):
        self.lock.acquire()
        try:
            logger.info(
                "开始申词 book_id:{}, book_name={}, keywords:{}".format(book['book_id'], book['book_name'], keywords))
            for keyword in keywords:
                time.sleep(3)
                promotions = self.search_alias(content_tab, keyword)
                time.sleep(2)
                if promotions:
                    logger.info('已经申请该词: {}'.format(keyword))
                    continue
                self.apply_keyword(book, keyword, content_tab)
        finally:
            self.lock.release()

    def apply_keyword(self, book, keyword, content_tab):
        try:
            params = 'app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=-HEQnThcgIlshkCgIOlqGgzI6A5TAjx3XOfMa1TmCGpK5TTbTxsfet06LLsxZ_sR6FebnWq1nlbt9DaUjDd_QyBBz2gQPXbI7ALVUVagMRDliYc5T7QERILtiK8aTJZxBvraWVxOdbxqitAuiR20ruMmaLOeaZQ%3D'
            url = 'https://promoter.fanqieopen.com/api/platform/promotion/plan/create/v:version?' + params
            alias_type = get_content_tab_config(content_tab)['alias_type']
            data = {"book_id": f"{book['book_id']}",
                    "alias_type": alias_type,
                    "alias_name": keyword,
                    "metrics_data": {"app_id": "457699", "create_entrance": "book_list", "app_name": "danhua",
                                     "sub_page_name": "全部内容", "genre": f"{book['genre']}", "is_recommend": "0"}
                    }
            logger.info('申请别名: {}'.format(keyword))
            body = dump(data)
            ab = get_ab(params, body, UA)
            url_ab = f'{url}&a_bogus={ab}'
            response = self.session.post(url_ab, headers=self.headers, data=body)
            json = response.json()
            if json['code'] != 0:
                if json['data']:
                    reason = json['data']['reason']
                    logger.info('申词失败 message:{}, reason:{}'.format(json['message'], reason))
                    if reason and '当日次数已用完' in reason[0]:
                        raise ApplyWordLimitException()
            else:
                logger.info('申词成功')
        except ApplyWordLimitException as e:
            raise e
        except Exception as e:
            logger.info('请求失败')
            traceback.print_exc()

    def get_promotions(self, content_tab, page_index):

        alias_type = get_content_tab_config(content_tab)['alias_type']
        # 定义请求的URL和查询参数
        params = 'task_type={task_type}&alias_status=1&post_status=1&need_post_audit=true&page_index={page_index}&page_size=10&app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=eEGp0Ku7bIIzVSwlsKJfitbwmj-tJYy62HGpCv1RDpSdKp7O7WBc9w0xYWdIpgeLv7J16D_J21EAYOT0f3Tv16LyYLuhUmFb2f3kpfe_26mt8-lbys3F6bLiKpOQSfJgG_FpiXuuQs-YTVVzeLNTGoO6vx2pTwhtlI9ksH9QMA%3D%3D'
        url = 'https://promoter.fanqieopen.com/api/platform/promotion/plan/list/v:version?'
        params = params.format_map({
            'task_type': alias_type,
            'page_index': page_index,
        })
        ab = get_ab(params, None, UA)
        url_ab = f'{url}{params}&a_bogus={ab}'
        response = self.session.get(url_ab, headers=self.headers)

        json = response.json()
        if json['code'] != 0:
            logger.error("获取失败 %s", json)
            return []
        else:
            promotion_list = json['data']['promotion_list']
            return promotion_list

    def huitian(self, alias_id, post_link, alias_type):
        params = 'post_link={post_link}&alias_id={alias_id}&post_platform_type=1&promotion_type=1&app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=3-7ozUs6_ZHGfc_YwnqZnCscsBl12sbP1ncr2yqhiYIM8s4LKzh2Cx89X4a6nfRw8ic8CVkwCwfFu9CGJZydeh28E8V5QNMzw4UKDXwYcAGC11TKIQ8KcSjEudS6iqxD8n14FTGrc3KYBN9OVHEbWBUJJrFYa2_aXlNW3m-x'
        url = 'https://promoter.fanqieopen.com/api/platform/promotion/post/link/parse/v:version?'
        logger.info('回填: alias_id={}, post_link={}'.format(alias_id, post_link))

        params = params.format_map({
            'post_link': post_link,
            'alias_id': alias_id,
        })

        ab = get_ab(params, None, UA)
        url_ab = f'{url}{params}&a_bogus={ab}'
        response = self.session.get(url_ab, headers=self.headers)
        json = response.json()
        if json['code'] != 0:
            logger.error("parse失败 %s", json)
        else:
            self.huitian2(alias_id, post_link, alias_type)

    def huitian2(self, alias_id, post_link, alias_type):
        params = 'app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=JRxj9FpnX54tM31tziTz3WRAXnLHBQPQqfhV4jhxyNqHXiatkGxyYzeF8MepG7YrsOXS3eokSY8YlP7-kf0ldztO8H9CYQhbP5SNBcML_TGDBd7da3W7VFvDJJZ__g2uuP4MriYnrBUk_ap0TSIxUX0QxNWCaUokYQzwDDPB'
        url = 'https://promoter.fanqieopen.com/api/platform/promotion/post/create/v:version?'

        body = {"alias_id": alias_id,
                "post_records": [{"post_link": post_link}], "alias_type": alias_type,
                "promotion_type": 1
                }
        body = dump(body)
        ab = get_ab(params, body, UA)
        url_ab = f'{url}{params}&a_bogus={ab}'
        response = self.session.post(url_ab, headers=self.headers, data=body)
        json = response.json()
        if json['code'] != 0:
            logger.info("回填失败 %s", json)
        else:
            logger.info("回填成功")

    def search_alias(self, content_tab, alias_name):
        alias_type = get_content_tab_config(content_tab)['alias_type']
        # 定义请求的URL和查询参数
        params = 'alias_name={alias_name}&task_type={task_type}&need_post_audit=true&page_index={page_index}&page_size=10&app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=rxp98PbE8B9TLrAXdShg9hEEW8cFiCdCBJvd4l5P0AUid1rVG6zIRbvbvn2PizluxCcDcwRx0uiB8orCTxJTj-OzJCRyLzfbP3QnNnDTB2EuRyb0cCPbR2D8lia2OtDbWSsdBnJJNA2s0dy94vNqh4dX1Djp0pRluXSP7S2meA%3D%3D'
        url = 'https://promoter.fanqieopen.com/api/platform/promotion/plan/list/v:version?'
        params = params.format_map({
            'task_type': alias_type,
            'page_index': 0,
            'alias_name': urllib.parse.quote(alias_name, safe=''),
        })
        ab = get_ab(params, None, UA)
        url_ab = f'{url}{params}&a_bogus={ab}'
        response = self.session.get(url_ab, headers=self.headers)
        json = response.json()
        if json['code'] != 0:
            logger.error("search_alias失败 %s", json)
            return []
        else:
            promotion_list = json['data']['promotion_list']
            return promotion_list
