import json

import requests


def dump(data):
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)


class FanqieApi:
    def __init__(self):
        self.session = requests.session()
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
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }

    def login(self):
        # 定义请求的URL和查询参数
        url = 'https://promoter.fanqieopen.com/api/platform/user/invite_code/log_in/v:version?app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=9P0QEeqlkQ_5o-iXDSRJXp8aSMYVeM_P-jZCsxIGHaL4oCYbNP1hk7fxH-vx6cZtl67LCZ_RHx2gI6mp9tNe-04lJWq5If23hspCjDuio9nHeST2_nU-QsT3z4O3_U6RfU_BRr3vGCPSGDb0OIz7tqVz072RMd4yHAG92DM2&a_bogus=EJW0Bfg6mEDP6DS45-ALfY3quNsjYhmJ0cye%2FD2WX5QlYg39HMYr9exYTkw15BgjNG%2FpIebjy4hcO3HMiOCGA3vXHuDKW95k-ggpKle%2Fso0j53inC6SmE0hN-iu3SFNd5XNAEOh0y7VrF8RZWoBe-7qvPE9jLojAYim7epJ5'

        # 定义请求的数据体
        data = {
            'share_token': 'Wg6DsvGE',
            'invite_code': 'guBTTKWP'
        }
        # 发送POST请求
        response = self.session.post(url, headers=self.headers, data=dump(data))

        if response.json()['code'] != 0:
            raise Exception("登录失败")
        print("登录成功")

    def get_content_tab(self):
        # 定义请求的URL和查询参数
        url = 'https://promoter.fanqieopen.com/api/platform/content/book/list/v:version?content_tab={content_tab}&genre=0&page_index={page_index}&page_size={page_size}&app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=pa0dxaomNn3nJ-a0kNH9XOh2tO1M-YSQuu0X3gVAqf80sQijY1QfpFO1VvDFZuHvhcDI0OwNpslorB-S8GVTZnvgmBmwYh1HiQM-x3CiE3SvA5MPzLqNWpwHeKgy3DR0L-5she-Y13j79iaPZEK8v02HmzA94t-FrY2qB6L5&a_bogus=Ejmh%2FmzhmEgBgDWm5-dLfY3quEa3Yhs80cye%2FD2W6nVlPy39HMPk9exYY9v14ryjNG%2FpIeSjy4hSTraMiOCGA3vXHuDKW95k-ggpKle%2Fso0j53inC6SmE0wE-hsAtl-Qsv1licfkowQnSYjmWxAj-kIAP62kFobyifELtAD%3D'

        url = url.format_map({
            'content_tab': 10,
            'page_index': 0,
            'page_size': 10,
        })

        # 定义请求的数据体
        data = {
            'share_token': 'Wg6DsvGE',
            'invite_code': 'guBTTKWP'
        }
        # 发送POST请求
        response = self.session.get(url, headers=self.headers, data=dump(data))

        json = response.json()
        if json['code'] != 0:
            print("获取失败")
        else:
            book_list = json['data']['book_list']
            return book_list

    def apply(self, book, keywords):
        print("开始申词", book, keywords)
        url = 'https://promoter.fanqieopen.com/api/platform/promotion/plan/create/v:version?app_id=457699&aid=457699&origin_app_id=457699&host_app_id=457699&msToken=-HEQnThcgIlshkCgIOlqGgzI6A5TAjx3XOfMa1TmCGpK5TTbTxsfet06LLsxZ_sR6FebnWq1nlbt9DaUjDd_QyBBz2gQPXbI7ALVUVagMRDliYc5T7QERILtiK8aTJZxBvraWVxOdbxqitAuiR20ruMmaLOeaZQ%3D&a_bogus=OXRZ%2FfwhdDdkDfy05-2LfY3quiJmYhsJ0cye%2FD2W8jAlz639HMO59exYYww1lvujNG%2FpIejjy4hSTNFMiOCGA3vXHuDKW95k-gT0te%2FQ59Wes1XHeDusn0vNmkw1CaBB-vplrO70qJKCKmz0AIc74kIAP6ZeaHgjxiSmtn3FvX6%3D'
        for keyword in keywords:
            data = {"book_id": f"{book['book_id']}",
                    "alias_type": 8,
                    "alias_name": keyword,
                    "metrics_data": {"app_id": "457699", "create_entrance": "book_list", "app_name": "danhua",
                                     "sub_page_name": "全部内容", "genre": "203", "is_recommend": "0"}
                    }
            print(dump(data))
            response = self.session.post(url, headers=self.headers, data=dump(data))
            print(response.headers)
            json = response.json()
            if json['code'] != 0:
                print('申词失败', json)
            else:
                print('申词成功')
