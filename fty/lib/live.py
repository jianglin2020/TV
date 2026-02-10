import requests
import json

HOST_API = 'http://sxcmcc-live.playauth.gitv.tv'

HEADERS = {
  'cookie': 'JSESSIONID=059YHBZC7CEIE3Z05NUQTQD1PSWIYRS0;CSESSIONID=;CSRFSESSION=7eeb80c6fb729c0f85ab53f9a91b18ae67431503a09f436f',
  'X_CSRFToken': '7eeb80c6fb729c0f85ab53f9a91b18ae67431503a09f436f',
  'Content-Type': 'application/json',
  'Host': 'sxcmcc-live.playauth.gitv.tv'
}

def get_play_data(name):
  dataList = {
    'cctv1': {"businessType":"BTV","mediaID":"G_LINFEN-1_P","channelID":"G_LINFEN-1"},
    'cctv2': {"businessType":"BTV","mediaID":"G_CCTV-2-CQ-TV_P","channelID":"G_CCTV-2-CQ-TV"},
    'cctv3': {"businessType":"BTV","mediaID":"HS_CCTV-3-HD-265-8M_P","channelID":"HS_CCTV-3-HD-265-8M"},
    'cctv4': {"businessType":"BTV","mediaID":"G_CCTV-4-CQ-TV_P","channelID":"G_CCTV-4-CQ-TV"},
    'cctv5': {"businessType":"BTV","mediaID":"HS_CCTV-5-HD-265-8M_P","channelID":"HS_CCTV-5-HD-265-8M"},
    'cctv6': {"businessType":"BTV","mediaID":"HS_CCTV-6-HD-265-8M_P","channelID":"HS_CCTV-6-HD-265-8M"},
    'cctv7': {"businessType":"BTV","mediaID":"G_CCTV-7-CQ-TV_P","channelID":"G_CCTV-7-CQ-TV"},
    'cctv8': {"businessType":"BTV","mediaID":"HS_CCTV-8-HD-265-8M_P","channelID":"HS_CCTV-8-HD-265-8M"},
    'cctv9': {"businessType":"BTV","mediaID":"G_CCTV-9-CQ-TV_P","channelID":"G_CCTV-9-CQ-TV"},
    'cctv10': {"businessType":"BTV","mediaID":"G_CCTV-10-CQ-TV_P","channelID":"G_CCTV-10-CQ-TV"},
    'cctv11': {"businessType":"BTV","mediaID":"G_CCTV-11-HQ-TV_P","channelID":"G_CCTV-11-HQ-TV"},
    'cctv12': {"businessType":"BTV","mediaID":"G_CCTV-12-CQ-TV_P","channelID":"G_CCTV-12-CQ-TV"},
    'cctv13': {"businessType":"BTV","mediaID":"G_CCTV-13-HQ-TV_P","channelID":"G_CCTV-13-HQ-TV"},
    'cctv14': {"businessType":"BTV","mediaID":"G_CCTV-14-CQ-TV_P","channelID":"G_CCTV-14-CQ-TV"},
    'cctv15':{"businessType":"BTV","mediaID":"G_CCTV-15-TV_P","channelID":"G_CCTV-15-TV"},
    'cctv16':{"businessType":"BTV","mediaID":"G_CCTV-16-CQ-TV_P","channelID":"G_CCTV-16-CQ-TV"},
    'cctv17':{"businessType":"BTV","mediaID":"G_CCTV-17-CQ-TV_P","channelID":"G_CCTV-17-CQ-TV"},
    '湖南卫视':{"businessType":"BTV","mediaID":"G_HUNAN-CQ-TV_P","channelID":"G_HUNAN-CQ-TV"},
    '江苏卫视':{"businessType":"BTV","mediaID":"G_JIANGSU-CQ-TV_P","channelID":"G_JIANGSU-CQ-TV"},
    '东方卫视':{"businessType":"BTV","mediaID":"G_DONGFANG-CQ-TV_P","channelID":"G_DONGFANG-CQ-TV"},
    '浙江卫视':{"businessType":"BTV","mediaID":"G_ZHEJIANG-CQ-TV_P","channelID":"G_ZHEJIANG-CQ-TV"},
    '北京卫视':{"businessType":"BTV","mediaID":"G_BEIJING-CQ-TV_P","channelID":"G_BEIJING-CQ-TV"},
    '深圳卫视':{"businessType":"BTV","mediaID":"G_SHENZHEN-CQ-TV_P","channelID":"G_SHENZHEN-CQ-TV"},
   }
  return dataList[name]

def get_play_url(name):
  data = get_play_data(name)
  print(data)
  url = '/itv/playauth/MTgzLjIwMS4zLjIzNzozMzIwMA=='
  res = requests.post(f'{HOST_API}{url}', data=json.dumps(data),headers=HEADERS,timeout=10)
  res_data = res.json()
  print(res_data)
  print(res_data.get('data').get('playurl'))

if __name__ == '__main__':
  get_play_url('深圳卫视')