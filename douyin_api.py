import json

import requests

from a_b import get_ab

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'


def dump(data):
    return json.dumps(data, separators=(',', ':'))


class DouyinApi:
    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'cookie': '__ac_nonce=06738834c0057a4abbc23; __ac_signature=_02B4Z6wo00f01BTzCJgAAIDDRgwog6O9-PQU0wwAAGIKd7;',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.douyin.com/search/%E6%B6%88%E5%A4%B1%E7%9A%84%E5%90%8C%E6%A1%8C%EF%BC%8C%E5%8F%AA%E6%9C%89%E6%88%91%E8%BF%98%E8%AE%B0%E5%BE%97%E5%A5%B9?aid=cf4ce2ed-f808-4457-81bc-1d21e4bf6484&type=general',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'uifid': '0173c8f974a1c07577a40e1ddb6347b1804450ad458bea7bd35bf3d7a8ab5901133beba3f7beae34788e66f6c8cff5476a6fc280238abcd20f41c7474dbe29aab0a694b5a09b13ac3c36aed93c9d9f7410d4a874a526e1019e93ff15e20739e9d0a94917b8321b9e3f0c08452bacc9f27c0e62d7fdf67aac3d6847c32db6a00e9ac071bee8a3ec0a1c06403c0e84b54cf2400d3899d9fbe4ef1d289bacbbf538',
            'user-agent': UA
        }

    def search(self, keywords: str, recent=False):
        params = 'device_platform=webapp&aid=6383&channel=channel_pc_web&search_channel=aweme_general&enable_history=1&filter_selected={filter_selected}&keyword={keywords}&search_source=tab_search&query_correct_type=1&is_filter_search={is_filter_search}&from_group_id=&offset={offset}&count=10&need_filter_settings=0&list_type=single&search_id=202411171516538506EC0E5BF456FE824E&update_version_code=170400&pc_client_type=1&pc_libra_divert=Mac&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1792&screen_height=1120&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=129.0.0.0&browser_online=true&engine_name=Blink&engine_version=129.0.0.0&os_name=Mac+OS&os_version=10.15.7&cpu_core_num=6&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=100&webid=7436023804469528074&uifid=63dd93172fb5fdaa8078f33ae0ba1106c8e3f1f870eecbc4b54b497d452c3517db481603fc871236214111b319e89ea03a2b86d269ba098f3e9cba8ffb34b9ed87854340671ac40462a77cd411b678a461023cc9340812944c9e01acbd5777d3a74f26c981e27e4815cebb1152c0e835561ef302fcc4bd77909f28f150251862bff215cd50fc3e9fdc1df100099e9b6698d240db048e6f9a4f2aaee2ec961f14&msToken=tCdVMrWkHh3szLQ0pfr-K35PY56-L6m5Lwt4usifn3BVzOULLNprU5KZh5Iflq72VBzIMEu_Lp1ZIyPFbe1ajztTCh3FtraPHV0UxJG7aeMWsLUCDsys6D3DX9ELylkOMWgyM-EMIpQMEpWOn_1yFJwjdd3T0_52Jk_gODmehoas2VROt_Aa9w%3D%3D'
        url = 'https://www.douyin.com/aweme/v1/web/general/search/single/?'
        params = params.format_map({
            'keywords': keywords,
            'offset': 0,
            'filter_selected': '{"sort_type":"0","publish_time":"1"}' if recent else '',
            'is_filter_search': 1 if recent else 0
        })
        ab = get_ab(params, None, UA)
        url_ab = f'{url}{params}&a_bogus={ab}'
        response = self.session.get(url_ab, headers=self.headers)
        return response.json()['data']
