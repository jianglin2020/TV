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
file_with_new_addresses = "ipv6.m3u"  # 第二个文件路径（包含新地址的文件）
output_file = "iptv_update.m3u"  # 输出文件路径

# 检查文件是否存在
if not os.path.exists(file_to_update):
    print(f"文件 {file_to_update} 不存在。")
    exit(1)

if not os.path.exists(file_with_new_addresses):
    print(f"文件 {file_with_new_addresses} 不存在。")
    exit(1)

# 读取新地址文件并构建频道名称到地址的映射
channel_address_map = {}
with open(file_with_new_addresses, "r", encoding="utf-8") as file:
    lines = file.readlines()
    for i in range(len(lines)):
        # 找到频道描述行
        match = re.match(r"#EXTINF:-1.*?,(.*)", lines[i])
        if match and i + 1 < len(lines):  # 确保下一行为地址行
            channel_name = match.group(1).strip()
            channel_address_map[channel_name] = lines[i + 1].strip()  # 下一行是地址

# 读取需要更新的文件并替换地址，去掉原地址
updated_lines = []
with open(file_to_update, "r", encoding="utf-8") as file:
    lines = file.readlines()
    skip_next_line = False  # 跳过下一行的标记
    for i in range(len(lines)):
        if skip_next_line:
            skip_next_line = False
            continue

        match = re.match(r"#EXTINF:-1.*?,(.*)", lines[i])
        if match:  # 找到频道描述行
            channel_name = match.group(1).strip()
            updated_lines.append(lines[i])  # 保留频道描述行

            # 如果在新地址文件中找到该频道的地址，替换为新地址
            if channel_name in channel_address_map:
                updated_lines.append(channel_address_map[channel_name] + "\n")  # 添加新地址
                skip_next_line = True  # 跳过下一行的原地址
        else:
            updated_lines.append(lines[i])  # 非描述行直接保留

# 写入更新后的文件
with open(output_file, "w", encoding="utf-8") as file:
    file.writelines(updated_lines)

print(f"地址更新完成，结果已保存到 {output_file}")