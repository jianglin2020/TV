#coding=utf-8
#!/usr/bin/python
import sys
import os
import json

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

host_url = 'https://frodo.douban.com/api/v2'
apikey = "?apikey=0ac44ae016490db2204ce0a042db2916"

class Spider(Spider): 
  def getName(self):
    return "home"
  def init(self,extend=""):
    self.header = {
      "Host": "frodo.douban.com",
      "Connection": "Keep-Alive",
      "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html",
      "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat"
    }

  def getDoubanList(self):
    url = host_url + '/subject_collection/subject_real_time_hotest/items' + apikey
    rsp = self.fetch(url,headers=self.header)
    jo = json.loads(rsp.text)
    joList = jo.get("subject_collection_items")
    lists = []
    for item in joList:
      rating = item['rating']['value'] if item['rating'] else ""
      item = {
        "vod_id": f'msearch:{item.get("type", "")}__{item.get("id", "")}',
        "vod_name": item['title'],
        "vod_pic": f"http://101.42.13.92:5700/proxy?url={item['pic']['normal']}",
        "vod_remarks": rating
      }
      print(item)
      lists.append(item)

  def static_url(self, filename):
    return f'http://101.42.13.92:5700/static/{filename}'
  # 获取数据
  def get_list(self, type_id):
    rsp = self.fetch(self.static_url('home/data.json'))
    list = rsp.json()

    return list.get(type_id, [])

  def isVideoFormat(self,url):
    pass
  def manualVideoCheck(self):
    pass
  def homeContent(self, filter):
    return {
      "class": [
        {
          "type_id": "1",
          "type_name": "电视剧"
        },
        {
          "type_id": "2",
          "type_name": "综艺"
        },
        {
          "type_id": "3",
          "type_name": "电影"
        },
        {
          "type_id": "4",
          "type_name": "短剧"
        }
      ],
      "filters": {},
      "list": [],
      "parse": 0,
      "jx": 0
    }

  def homeVideoContent(self):
    # 获取推荐列表
    lists = self.get_list('0')

    for item in lists:
        if not item.get('vod_pic'):
            item['vod_pic'] = self.static_url(f"images/{item['vod_name']}.jpg")
    
    result = {
      'list': lists
    }
    return result
  def categoryContent(self,tid,pg,filter,extend={}):	
    # 获取列表
    lists = self.get_list(tid)

    for item in lists:
        if not item.get('vod_pic'):
            item['vod_pic'] = self.static_url(f"images/{item['vod_name']}.jpg")
    
    if int(pg) > 1:
      lists = [] 
    return {
      'list': lists,
      'page': int(pg),
      'pagecount': 9999,
      'limit': 30,
      'total': 999999
    }

  def detailContent(self,array):
    pass
  def searchContent(self,key,quick):
    pass
  def playerContent(self,flag,id,vipFlags):
    pass

  def localProxy(self,param):
    pass

if __name__ == '__main__':
    spider = Spider()
    formatJo = spider.init([]) # 初始化
    formatJo = spider.homeContent(False)
    formatJo = spider.homeVideoContent()
    formatJo = spider.categoryContent('3', 1, False)
    formatJo = spider.getDoubanList()

    print(formatJo)