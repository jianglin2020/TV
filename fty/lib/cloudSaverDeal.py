# cloudSaver处理数据脚本
import requests
from bs4 import BeautifulSoup
import json
import time

CHANNEL_IDS = [
    "ucwpzy", "yunpanuc", "yunpanshare", "Quark_Movies", "kuakeyun",
    "NewQuark", "pankuake_share", "jdjdn1111", "yunpanall", "alyp_1",
    "tyypzhpd", "tianyirigeng", "cloudtianyi", "yunpan189", "txtyzy",
    "zyzhpd123", "xx123pan", "yingshifenxiang123", "yp123pan", "zaihuayun",
    "NewAliPan", "shareAliyun", "ydypzyfx", "yunpan139", "xunleibl",
    "yunpanxunlei", "xlshare", "shares_115", "Channel_Shares_115",
    "ResourceUniverse", "peccxinpd", "ucquark", "leoziyuan", "kuakeclound",
    "XiangxiuNB", "vip115hot", "PikPakShareChannel", "alyp_Animation",
    "yggpan", "yunpansall", "Q66Share", "Oscar_4Kmovies",
    "Aliyun_4K_Movies", "taoxgzy", "BaiduCloudDisk", "tyysypzypd",
    "ucpanpan", "yydf_hzl", "zyfb123", "clouddriveresources",
    "tgsearchers", "yunpanpan", "pan123pan", "kuakezyfb", "MCPH860",
    "MCPH608", "MCPH01", "quanziyuanshe", "ydyp888", "hao115",
    "oneonefivewpfx", "guaguale115"
]

def get_title(channel_id, session=None):
    url = f"https://t.me/s/{channel_id}"
    print(url)
    s = session or requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        resp = s.get(url, timeout=10)
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"
        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", {"property": "og:title"})
        if meta and meta.has_attr("content"):
            print(meta["content"].strip())
            return meta["content"].strip(), None
        return None, "名称标签未找到"
    except Exception as e:
        return None, str(e)

def main():
    session = requests.Session()
    results = []
    for cid in CHANNEL_IDS:
        title, err = get_title(cid, session)
        record = {"id": cid, "name": title if title else cid}
        if err:
            record["error"] = err
        results.append(record)
        time.sleep(1.0)  # 礼貌访问、避免封 IP
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
