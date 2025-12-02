from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime


app = Flask(__name__)

HEADERS = {
  'Authorization': '',
  'Content-Type': 'application/json;'
}

HOST_API = 'http://192.168.1.120:8040'

def openlist_login():
    data = {
      "username":"guan","password":"1ba5064eeecf855752b8678f3d3de0926f2adc11e8c3139a944b274c8b52c619","otp_code":""
    }
    res = requests.post(f'{HOST_API}/api/auth/login/hash', data=json.dumps(data), headers={'Content-Type': 'application/json'})

    res = res.json()
    data = res.get('data', {})
    print(res)
    HEADERS["Authorization"] = data['token']

def openlist_list(path, page):
    print(path, 'path')
    res =  requests.post(f'{HOST_API}/api/fs/list', data = json.dumps({"path": path,"password":"", 'page': page}), headers=HEADERS)
    res = res.json()
    return res.get('data', {})

def openlist_get(path):
    res =  requests.post(f'{HOST_API}/api/fs/get', data = json.dumps({"path": path,"password":""}), headers=HEADERS)
    res = res.json()
    return res.get('data', {}) 

def openlist_search(keywords):
    res =  requests.post(f'{HOST_API}/api/fs/search', data=json.dumps({
    "parent":"/","keywords": keywords,"scope":0,"page":1,"per_page":100,"password":""}), headers=HEADERS)
    res = res.json()

    return res.get('data', {})  

# 首页
def home():
    # /spider?site=test&filter=true
    title_list = [
      { 'parent': '/天翼/临时文件' , 'name': '凡人修仙传 (2020)'},
      { 'parent': '/天翼/临时文件' , 'name': '大生意人'},
      { 'parent': '/天翼/nas/综艺' , 'name': '现在就出发 第三季'},
      { 'parent': '/天翼/nas/综艺' , 'name': '森林进化论 第三季'},
      { 'parent': '/天翼/nas/综艺' , 'name': '奔跑吧 天路篇'},
      { 'parent': '/天翼/nas/综艺' , 'name': '声生不息 华流季'},
      { 'parent': '/天翼/nas/综艺' , 'name': '喜人奇妙夜 第二季'},
      { 'parent': '/天翼/nas/综艺' , 'name': '向往的生活 第八季'},
      { 'parent': '/天翼/nas/综艺' , 'name': '你好星期六 2025'},
    ]

    list = []

    for item in title_list:
      list.append({
          'vod_id': f"{item['parent']}/{item['name']}",
          'vod_name': item['name'], 
          'vod_pic': f"http://192.168.1.120:8010/images/{item['name']}.jpg", 'vod_remarks': ''
      })
      
    return {
      "class": [
        {
          "type_id": "/天翼/nas/电视剧",
          "type_name": "电视剧"
        },
        {
          "type_id": "/天翼/nas/综艺",
          "type_name": "综艺"
        },
        {
          "type_id": "/天翼/nas/电影",
          "type_name": "电影"
        },
        {
          "type_id": "/其它",
          "type_name": "其它"
        }
      ],
      "filters": {},
      "list": list,
      "parse": 0,
      "jx": 0
    }

# 分类列表
def list_page(t, page):
    print(t)
  
    type = t.split('/')[-1]

    data = openlist_list(t, page)

    list = []
    title_list = []

    if data is not None:
        content = data['content'] or []  # 使用 get 更安全
    else:
        content = []

    # content = data['content'] or []
    # print(content, 'content')

    # 按时间排序（从晚到早）
    # sorted_items = sorted(content, key=lambda x: datetime.fromisoformat(x["modified"]), reverse=True)
    sorted_items = sorted(content, key=lambda x: 
        datetime.fromisoformat(x["modified"][:19]), 
        reverse=True
    )

    for item in sorted_items:
      # print(f"http://192.168.1.120:8010/images/{item['name']}.jpg")
      # 电影特殊处理
      if type in {'电影', '其它'}:
          name = item['name'].split('.')[-2]
      else:
          name = item['name']

      list_item = {
        "vod_id": f"{t}/{name}",
        "vod_name": name,
        "vod_pic": f"http://192.168.1.120:8010/images/{name}.jpg",
        "vod_remarks": ""
      }

      # 根据类型添加额外字段
      if type in {'其它'}:
          list_item.update({
              "vod_pic": f"http://192.168.1.120:8010/images/maoww/{name}.jpg",
              "style": {
                  "type": "rect",
                  "ratio": 1.5
              }
          })
      list.append(list_item)
      title_list.append(name)

    # print(list)
    print(title_list)
    return {
      'list': list,
      "parse": 0,
      "jx": 0
    }

# ---- 详情 ac=detail ----
def detail(ids):
    # /spider?site=Miss&t=%2Fdm169%2Fweekly-hot&ac=detail&pg=1&ext=e30%3D HTTP/2
    print(ids)
    type = ids.split('/')[-2]
    all_content = []
    if type in {'电影', '其它'}:
        vod_name = ids.split('/')[-1]
        ids = os.path.dirname(ids)
        data = openlist_list(ids, 1)

        # 过滤出 name 的数据1
        content = [
            item for item in data['content'] 
            if os.path.splitext(item["name"])[0] == vod_name
        ]
        all_content.append({
            'content': content,
            'play_from': 'alist',
            'ids': ids,
        })

    else: # 电视剧、综艺
        data = openlist_list(ids, 1)
        vod_name = ids.split('/')[-1]

        # 多层结构
        if data['content'] and data['content'][0]['is_dir']:
            print('多线路')
            for item in data['content']:
                play_list = []
                newIds = f"{ids}/{item['name']}"
                data = openlist_list(newIds, 1)
                all_content.append({
                  'content': data['content'],
                  'play_from': item['name'],
                  'ids': newIds
                })
        # 单层结构          
        else:  
            all_content.append({
              'content': data['content'],
              'play_from': 'alist',
              'ids': ids,
            })

    all_play_list = []
    all_from_list = []

    for all_item in all_content:
        ids = all_item['ids']
        # 使用列表推导式优化内部循环
        play_list = [
            f"{it['name']}${ids}/{it['name']}" 
            for it in all_item['content']
        ]
        all_play_list.append('#'.join(play_list))
        all_from_list.append(all_item['play_from'])

    return {
      "list": [
        {
          "type_name": "",
          "vod_id": ids,
          "vod_name": vod_name,
          "vod_remarks": "",
          "vod_year": "",
          "vod_area": "",
          "vod_actor": "",
          "vod_director": "",
          "vod_content": "",
          "vod_play_from": '$$$'.join(all_from_list),
          "vod_play_url": '$$$'.join(all_play_list)
        }
      ],
      "parse": 0,
      "jx": 0
    }


# 播放
def play_detail(play):

  data = openlist_get(play)

  return {
    "url": data['raw_url'],
    "header": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    },
    "parse": 0,
    "jx": 0
  }

# 搜索
def search(wd):
    data = openlist_search(wd)

    print(data)

    list = []
    for item in data['content']:
      print(item, '=======================')
      if item['parent'] in {'/天翼/nas/综艺', '/天翼/nas/电视剧'}:
          list.append({
            "vod_id": f"{item['parent']}/{item['name']}",
            "vod_name": item['name'],
            "vod_pic": f"http://192.168.1.120:8010/images/{item['name']}.jpg",
            "vod_remarks": ""
          })
      else:
          if item['parent'] in {'/天翼/nas/电影'}:
            name = item['name'].split('.')[-2]
            list.append({
              "vod_id": f"{item['parent']}/{name}",
              "vod_name": name,
              "vod_pic": f"http://192.168.1.120:8010/images/{name}.jpg",
              "vod_remarks": ""
            })

    return {
      "list": list
  }


# ---- 主入口 spider ----
@app.route("/spider")
def spider():
    # 1. 参数验证
    if request.args.get("site") != "test":
        return jsonify({"error": "unknown site"})
    
    # 2. 获取所有参数
    filter_param = request.args.get("filter")
    ac = request.args.get("ac")
    t = request.args.get("t")
    ids = request.args.get("ids")
    play = request.args.get("play") 
    wd = request.args.get("wd")
    pg = int(request.args.get("pg", "1"))
    
    # 3. 路由分发
    # 主页
    if filter_param:
        return jsonify(home())
    
    # 详情页（列表或具体详情）
    if ac == "detail":
        if t:  # 列表页
            return jsonify(list_page(t, pg))
        if ids:  # 详情页
            return jsonify(detail(ids))
    
    # 播放页
    if play:
        print(play, 'play')
        return jsonify(play_detail(play))
    
    # 搜索
    if wd:
        return jsonify(search(wd))
    
    # 4. 默认错误响应
    return jsonify({"error": "bad request"})


if __name__ == "__main__":
  openlist_login()
  app.run(host="0.0.0.0", port=5700, debug=True)
