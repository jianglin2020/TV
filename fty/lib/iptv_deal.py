import re
import os

# 切换到 `./fty/lib` 目录
target_directory = "./fty/lib"
if not os.path.exists(target_directory):
    print(f"目录 {target_directory} 不存在。")
    exit(1)
os.chdir(target_directory)
print(f"当前工作目录切换到：{os.getcwd()}")

# 文件路径
file_to_update = "iptv_dome.m3u"  # 第一个文件路径（需要更新的文件）
file_with_new_addresses = "Sub_plus.m3u"  # 第二个文件路径（包含新地址的文件）
output_file = "iptv_update.m3u"  # 输出文件路径

# 读取新地址文件并构建频道名称到多个地址的映射
channel_address_map = {}
with open(file_with_new_addresses, "r", encoding="utf-8") as file:
    lines = file.readlines()
    for i in range(len(lines)):
        # 找到频道描述行
        match = re.match(r'#EXTINF:-1.*?tvg-name="(.*?)".*', lines[i])
        if match and i + 1 < len(lines):  # 确保下一行为地址行
            raw_channel_name = match.group(1).strip()
            # 将频道名称转换为大写，以便匹配
            normalized_name = raw_channel_name.upper()
            if normalized_name not in channel_address_map:
                channel_address_map[normalized_name] = []  # 存储多个地址的列表
            channel_address_map[normalized_name].append(lines[i + 1].strip())  # 添加新的地址

# 读取需要更新的文件并替换地址
updated_lines = []
i = 0  # 线条索引
with open(file_to_update, "r", encoding="utf-8") as file:
    lines = file.readlines()
    
    # 保留文件头部的 #EXTM3U 以及其它非频道描述行
    if lines[0].startswith("#EXTM3U"):
        updated_lines.append(lines[0])  # 保留文件头部
    
    while i < len(lines):
        match = re.match(r'#EXTINF:-1.*?tvg-name="(.*?)".*', lines[i])
        if match and i + 1 < len(lines):  # 找到频道描述行并确保有地址行
            raw_channel_name = match.group(1).strip()
            # 将频道名称转换为大写，以便匹配
            normalized_name = raw_channel_name.upper()

            # 如果该频道有新地址，替换原地址
            if normalized_name in channel_address_map:
                updated_lines.append(lines[i])  # 保留频道描述行
                for address in channel_address_map[normalized_name]:  # 遍历所有新地址
                    # 定义需要过滤的关键词
                    filter_keywords = ["华数"]
                    # 如果地址包含任意一个过滤词，则跳过
                    if any(keyword in address for keyword in filter_keywords):
                        continue
                    updated_lines.append(address + "\n")  # 添加新地址
                i += 1  # 跳过原地址行
        i += 1

# 写入更新后的文件
with open(output_file, "w", encoding="utf-8") as file:
    file.writelines(updated_lines)

print(f"地址更新完成，结果已保存到 {output_file}")