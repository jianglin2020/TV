#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import base64, json, sys, requests, re
from urllib import parse

# 设置目标目录
target_dir = os.path.dirname(__file__)

# 如果当前不在目标目录，则切换
if os.getcwd() != os.path.abspath(target_dir):
    try:
        os.chdir(target_dir)
        print(f"切换到: {os.getcwd()}")
    except Exception as e:
        print(f"切换失败: {e}")

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        super().__init__()
        self.debug = False
        self.name = '采集去广模板'
        self.error_play_url = 'https://kjjsaas-sh.oss-cn-shanghai.aliyuncs.com/u/3401405881/20240818-936952-fc31b16575e80a7562cdb1f81a39c6b0.mp4'
        self.home_url = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'
        }
        self.a = []

    def getName(self):
        return self.name

    def del_ads(self, url):
        """M3U8去广告函数"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
        }
        try:
            session = requests.session()
            # 获取m3u8根路径
            root_url1 = url.rsplit('/', maxsplit=1)[0] + '/'
            # 第一次请求获取重定向的m3u8
            response = session.get(url, headers=headers)
            url2 = root_url1 + response.text.splitlines()[-1]
            
            # 第二次请求获取实际的播放列表
            root_url2 = url2.rsplit('/', maxsplit=1)[0] + '/'
            response2 = session.get(url2, headers=headers)

            # with open('1.m3u', 'w', encoding='utf-8') as f:
            #   f.write(response2.text)
            
            # 去广告处理
            # 移除包含1-10行内容的DISCONTINUITY片段（广告）
            text = re.sub(r'#EXT-X-DISCONTINUITY\n((.*?\n){1,10})#EXT-X-DISCONTINUITY\n', '', response2.text)
            # 处理结尾处的DISCONTINUITY
            text = re.sub(r'#EXT-X-DISCONTINUITY\n((.*?\n){2})#EXT-X-ENDLIST\n', '#EXT-X-ENDLIST', text)
            # 移除单独的DISCONTINUITY标记
            text = re.sub(r'#EXT-X-DISCONTINUITY\n', '', text)
            # 修复.ts文件路径（相对路径转绝对路径）
            text = re.sub(r'(.*\.ts.*)', root_url2 + '\\1', text)
            # with open('2.m3u', 'w', encoding='utf-8') as f:
            #   f.write(text)
            return text
        except Exception as e:
            print(e)
        return None

    def init(self, extend='{}'):
        """初始化，从外部传入配置"""
        try:
            self.extend = json.loads(extend)
            self.home_url = self.extend['url']
            self.a = self.extend['a']
        except Exception as e:
            print(e)
            exit('')

    def homeContent(self, filter):
        """获取首页分类"""
        return_data = {
            'class': [],
            'filters': {},
            'list': [],
            'parse': 0,
            'jx': 0
        }
        try:
            response = requests.get(self.home_url + '?ac=list', headers=self.headers)
            for i in response.json()['class']:
                if i['type_id'] in self.a:  # 排除指定分类
                    continue
                return_data['class'].append({
                    'type_id': i['type_id'],
                    'type_name': i['type_name']
                })
        except Exception as e:
            print(e)
        return return_data

    def homeVideoContent(self):
        """首页推荐视频"""
        return_data = {
            'list': [],
            'parse': 0,
            'jx': 0
        }
        try:
            response = requests.get(self.home_url + '?ac=detail', headers=self.headers)
            for i in response.json()['list']:
                return_data['list'].append({
                    'vod_id': i['vod_id'],
                    'vod_name': i['vod_name'],
                    'vod_pic': i['vod_pic'],
                    'vod_remarks': i['vod_remarks'],
                    'vod_year': i['vod_year']
                })
        except Exception as e:
            print(e)
        return return_data

    def categoryContent(self, cid, page, filter, ext):
        """分类视频列表"""
        return_data = {
            'list': [],
            'parse': 0,
            'jx': 0
        }
        try:
            response = requests.get(self.home_url + f"?t={cid}&pg={page}&ac=detail", headers=self.headers)
            for i in response.json()['list']:
                return_data['list'].append({
                    'vod_id': i['vod_id'],
                    'vod_name': i['vod_name'],
                    'vod_pic': i['vod_pic'],
                    'vod_remarks': i['vod_remarks'],
                    'vod_year': i['vod_year']
                })
        except Exception as e:
            print(e)
        return return_data

    def detailContent(self, did):
        """视频详情"""
        return_data = {
            'list': [],
            'parse': 0,
            'jx': 0
        }
        ids = did[0]
        try:
            response = requests.get(self.home_url + f"?ids={ids}&ac=detail", headers=self.headers)

            i = response.json()['list'][0]
            return_data['list'].append({
                'type_name': i['type_name'],
                'vod_id': ids,
                'vod_name': i['vod_name'],
                'vod_remarks': i['vod_remarks'],
                'vod_year': i['vod_year'],
                'vod_area': i['vod_area'],
                'vod_actor': i['vod_actor'],
                'vod_director': i['vod_director'],
                'vod_content': i['vod_content'],
                'vod_play_from': '去广告',
                'vod_play_url': i['vod_play_url']
            })
        except Exception as e:
            print(e)
        return return_data

    def searchContent(self, wd, quick, page='1'):
        """搜索视频"""
        return_data = {
            'list': [],
            'parse': 0,
            'jx': 0
        }
        try:
            response = requests.get(self.home_url + f"?wd={wd}&pg={page}&ac=detail", headers=self.headers)
            for i in response.json()['list']:
                print(i['vod_name'])
                if i['type_id'] in self.a:  # 排除指定分类
                    continue
                return_data['list'].append({
                    'vod_id': i['vod_id'],
                    'vod_name': i['vod_name'],
                    'vod_pic': i['vod_pic'],
                    'vod_remarks': i['vod_remarks'],
                    'vod_year': i['vod_year']
                })
        except Exception as e:
            print(e)
        return return_data

    def playerContent(self, flag, pid, vipFlags):
        """播放地址处理"""
        return_data = {
            'url': self.error_play_url,
            'parse': 0,
            'jx': 0,
            'header': self.headers
        }
        # 将播放地址包装为代理地址，通过localProxy处理
        return_data['url'] = 'proxy://do=py&url=' + parse.quote_plus(pid)
        return return_data

    def localProxy(self, params):
        """本地代理，处理去广告"""
        m3u8_text = self.del_ads(parse.unquote(params['url']))
        if m3u8_text:
            return [200, 'application/vnd.apple.mpegurl', m3u8_text]


if __name__ == '__main__':
    spider = Spider()
    # formatJo = spider.init('{"url":"http://ffzy.tv/api.php/provide/vod/from/ffm3u8/at/json/","a":[1,2,3,34]}') # 非凡初始化
    formatJo = spider.init('{"url":"http://caiji.dyttzyapi.com/api.php/provide/vod/from/dyttm3u8/at/json/","a":[1, 2, 3, 4, 5, 33, 34]}') # 电影天堂初始化
    # formatJo = spider.homeContent(False)
    # formatJo = spider.categoryContent('34', 1, False, {})
    # formatJo = spider.detailContent(['2701'])
    # formatJo = spider.playerContent('', 'https://vip.ffzy-play6.com/20221021/584_f6dedf19/index.m3u8', False)
    # formatJo = spider.localProxy({'url': 'https://vip.ffzy-play6.com/20221021/584_f6dedf19/index.m3u8'})
    formatJo = spider.searchContent('小城大事', False)

    print(formatJo)