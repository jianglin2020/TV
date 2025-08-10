import requests
from pathlib import Path

def download_m3u(url, save_path=None):
    """
    下载M3U文件并保存到本地
    
    参数:
    url (str): M3U文件的URL
    save_path (str/Path): 可选，自定义保存路径
    """
    try:
        # 发送HTTP GET请求
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 设置默认保存路径（当前目录）
        if save_path is None:
            save_path = Path("mursor.m3u")
        else:
            save_path = Path(save_path)
        
        # 写入文件
        save_path.write_text(response.text, encoding='utf-8')
        
        print(f"文件已成功下载到: {save_path.resolve()}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
        return False

if __name__ == "__main__":
    # 需要下载的URL
    m3u_url = "https://raw.githubusercontent.com/Mursor/LIVE/refs/heads/main/iptv.m3u"
    
    # 自定义保存路径（可选）
    custom_path = r"./fty/lib/mursor.m3u"
    
    # 调用下载函数
    # download_m3u(m3u_url)  # 使用默认路径
    download_m3u(m3u_url, custom_path)  # 使用自定义路径