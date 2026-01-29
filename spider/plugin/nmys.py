#coding=utf-8
#!/usr/bin/python
import json
import re
import sys
import os
import requests
from base64 import b64decode, b64encode
from pyquery import PyQuery as pq
from lxml import etree

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

    def init(self, extend=""):
        self.host = "https://vip.wwgz.cn:5200"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Referer': self.host + '/',
            'Accept': 'text/html'
        }
        self.cateConfig = {
            "12": [{"key": "cateId", "name": "类型", "value": [{"n": "国产剧", "v": "12"}]}],
            "4-dm": [{"key": "cateId", "name": "类型", "value": [{"n": "动漫", "v": "4-dm"}]}],
            "1": [{"key": "cateId", "name": "类型", "value": [{"n": "电影", "v": "1"}]}],
            "2": [{"key": "cateId", "name": "类型", "value": [{"n": "电视剧", "v": "2"}]}],
            "3": [{"key": "cateId", "name": "类型", "value": [{"n": "综艺", "v": "3"}]}],
            "26": [{"key": "cateId", "name": "类型", "value": [{"n": "短剧", "v": "26"}]}]
        }
        self.filterConfig = {}

    def getName(self):
        return "农民影视"

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

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        result = {}
        classes = [
            {'type_name': '国产剧', 'type_id': '12'},
            {'type_name': '动漫', 'type_id': '4-dm'},
            {'type_name': '电影', 'type_id': '1'},
            {'type_name': '电视剧', 'type_id': '2'},
            {'type_name': '综艺', 'type_id': '3'},
            {'type_name': '短剧', 'type_id': '26'}
        ]
        try:
            data = self.fetch(self.host, headers=self.headers).text
            doc = pq(data)
            videos = []
            # 修改选择器并添加去重逻辑
            seen_ids = set()  # 用于记录已处理的影片ID
            for item in doc('.globalPicList li:has(img)').items():
                vod_id = self.host + item('a').attr('href')
                if vod_id not in seen_ids:  # 检查是否已处理过
                    seen_ids.add(vod_id)  # 记录已处理的ID
                    pic_url = item('img').attr('data-echo') or item('img').attr('data-src') or item('img').attr('src')
                    # 替换图片域名
                    if pic_url and 'pic.lzzypic.com' in pic_url:
                        pic_url = pic_url.replace('https://pic.lzzypic.com', 'https://img.lzzyimg.com')
                    videos.append({
                        'vod_id': vod_id,
                        'vod_name': item('.sTit').text(),
                        'vod_pic': pic_url,
                        'vod_remarks': item('.sBottom').text()
                    })
            result['class'] = classes
            result['filters'] = self.cateConfig
            result['list'] = videos
        except Exception as e:
            print(f"首页数据获取失败: {str(e)}")
            result['class'] = classes
            result['filters'] = self.cateConfig
            result['list'] = []
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        try:
            if tid == "4-dm":
                # 处理大陆人气动漫分类
                url = "https://www.wwgz.cn/vod-list-id-4-pg-{}-order--by-hits-class-0-year-0-letter--area-大陆-lang-.html".format(pg)
            else:
                cateId = tid
                url = f"{self.host}/vod-list-id-{cateId}-pg-{pg}.html"
                
            data = self.fetch(url, headers=self.headers).text
            doc = pq(data)
            
            videos = []
            for item in doc('.globalPicList li').items():
                pic_url = item('img').attr('data-echo') or item('img').attr('data-src') or item('img').attr('src')
                # 替换图片域名
                if pic_url and 'pic.lzzypic.com' in pic_url:
                    pic_url = pic_url.replace('https://pic.lzzypic.com', 'https://img.lzzyimg.com')
                videos.append({
                    'vod_id': self.host + item('a').attr('href'),
                    'vod_name': item('.sTit').text(),
                    'vod_pic': pic_url,
                    'vod_remarks': item('.sBottom').text()
                })
            
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 90
            result['total'] = 999999
        except Exception as e:
            print(f"分类数据获取失败: {str(e)}")
            result['list'] = []
            result['page'] = pg
            result['pagecount'] = 1
            result['limit'] = 90
            result['total'] = 0
        return result

    def detailContent(self, ids):
        result = {}
        try:
            url = ids[0]
            data = self.fetch(url, headers=self.headers).text
            doc = pq(data)
            
            # 获取播放线路和剧集
            play_from = []
            play_url = []
            
            tab_box = doc('#leftTabBox')
            if tab_box:
                for tab in tab_box('ul li').items():
                    play_from.append(tab.text())
                
                play_lists = []
                for num_list in tab_box('.numList').items():
                    episodes = []
                    # 修改这里：将items()转换为列表后反转顺序
                    for ep in list(num_list('li').items())[::-1]:  # 反转列表顺序
                        episodes.append(f"{ep('a').text()}${self.host}{ep('a').attr('href')}")
                    play_lists.append('#'.join(episodes))
                
                play_url = play_lists
            
            # 获取详情信息
            vod = {
                'vod_name': doc('h1 a').text(),
                'vod_year': doc('span:contains("年代：")').text().replace('年代：', ''),
                'vod_area': '',
                'vod_actor': doc('.sDes:contains("主演:")').text().replace('主演:', ''),
                'vod_director': '',
                'vod_content': doc('.detail-con p').text().replace('简介:', ''),
                'vod_play_from': '$$$'.join(play_from),
                'vod_play_url': '$$$'.join(play_url)
            }
            result['list'] = [vod]
        except Exception as e:
            print(f"详情数据获取失败: {str(e)}")
            result['list'] = []
        return result

    def searchContent(self, key, quick, pg="1"):
        result = {}
        try:
            url = f"{self.host}/index.php?m=vod-search"
            data = {'wd': key}
            headers = {
                'User-Agent': self.headers['User-Agent'],
                'Referer': self.host + '/'
            }
            html = self.post(url, data=data, headers=headers).text
            doc = pq(html)
            
            videos = []
            for item in doc('#data_list li').items():
                pic_url = item('.lazyload').attr('data-src')
                # 替换图片域名
                if pic_url and 'pic.lzzypic.com' in pic_url:
                    pic_url = pic_url.replace('https://pic.lzzypic.com', 'https://img.lzzyimg.com')
                videos.append({
                    'vod_id': self.host + item('a').attr('href'),
                    'vod_name': item('.sTit').text(),
                    'vod_pic': pic_url,
                    'vod_remarks': item('.sDes').eq(-1).text()
                })
            
            result['list'] = videos
            result['page'] = pg
        except Exception as e:
            print(f"搜索数据获取失败: {str(e)}")
            result['list'] = []
            result['page'] = pg
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        try:
            # 获取配置key
            js_data = self.fetch(url=id, headers=self.headers).text

            target_href = id.split('/')[-1]

            print(target_href)

            # 解析 HTML
            html = etree.HTML(js_data)

            # 方法1: 使用 XPath 查找指定 href 的 a 标签
            a_elements = html.xpath(f'//a[@href="/{target_href}"]')

            if a_elements:
                text = a_elements[0].text
                print(f"找到文本: {text}")
            else:
                print("未找到指定 href 的链接")

            # 方法1：直接找到对应键（推荐）
            match = re.search(rf'\$([^#]+)#{re.escape(text)}(?=\$|$)', js_data)

            if match:
                key = match.group(1)
                print(f"找到的键: {key}")
            else:
                print("未找到指定名称")  
            
            m3u_url = f'https://api.wwgz.cn:520/player/?url={key}'

            js_data2 = self.fetch(url=m3u_url, headers=self.headers).text

            # 方法1：直接匹配url的值
            pattern = r'"url":\s*"([^"]+)"'
            match = re.search(pattern, js_data2)

            if match:
                url_value = match.group(1)
                print(f"找到url值: {url_value}")
            else:
                print("未找到url值")

            p, url = 0, f'proxy://do=py&url={url_value}'
            
            result['parse'] = p
            result['url'] = url
            result['header'] = self.headers
        except Exception as e:
            print(f"播放数据获取失败: {str(e)}")
            result['parse'] = 1
            result['url'] = id
            result['header'] = self.headers
        return result

    def localProxy(self, param):
        """本地代理，处理去广告"""
        m3u8_text = self.del_ads(param['url'])

        if m3u8_text:
            return [200, 'application/vnd.apple.mpegurl', m3u8_text]

    def liveContent(self, url):
        pass

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""


if __name__ == '__main__':
    spider = Spider()
    formatJo = spider.init([]) # 初始化
    # formatJo = spider.homeContent(False)
    # formatJo = spider.categoryContent('2', 1, False, {})
    # formatJo = spider.detailContent(['https://vip.wwgz.cn:5200/vod-detail-id-83775.html'])
    # formatJo = spider.playerContent('', 'https://vip.wwgz.cn:5200/vod-play-id-65872-src-1-num-55.html', False)

    # formatJo = spider.localProxy({'url': 'https://v.lzcdn28.com/20260110/7118_da64fcba/index.m3u8'})

    # formatJo = spider.searchContent('生命树', False)
        
    print(formatJo)