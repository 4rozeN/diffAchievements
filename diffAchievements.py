import os
import requests
import re
from bs4 import BeautifulSoup

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.realpath(__file__))

def getConfig():
    language = input("请选择steam响应语言（Chinese/English）：").strip().lower()
    if language in ['chinese', 'c']:
        headers = {
            "Accept-Language": "zh-CN"  # 设置简体中文
        }
        print("已选择中文作为Steam响应语言。")
    elif language in ['english', 'e']:
        headers = {
            "Accept-Language": "en-US"  # 设置英文
        }
        print("English language selected for Steam display.")
    else:
        print("无效的输入，请选择 'Chinese' 或 'English'，即 'c' 或 'e'。")
        return None, None

    # 通过终端输入获取Steam个人资料URL，默认值为一个示例URL
    playerURL = input("请输入游戏的个人成就进度页面地址URL（例如：https://steamcommunity.com/id/43xxx123/stats/2358720/achievements/）：")
    # 正则匹配
    pattern = r"/id/(\d+)/stats/(\d+)/"
    # 使用re.search进行匹配
    match = re.search(pattern, playerURL)
    if match:
        playerId = match.group(1)
        gameId = match.group(2)
    else:
        print("无效的个人资料URL，请检查输入是否正确。")
        return None, None

    use_proxy = input("是否开启代理？(y/n): ").strip().lower()
    proxies = {}
    if use_proxy == 'y':
        proxy_address = input("请输入代理地址（例如：http://127.0.0.1:7897）：").strip()
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        print(f"已开启代理：{proxy_address}")
    else:
        print("未开启代理。")

    config = {
        'gameId': gameId,
        'playerId': playerId,
        'headers': headers,
        'proxies': proxies
    }
    return config

def getResponse(playerId, gameId, headers, proxies):
    playerURL = f"https://steamcommunity.com/id/{playerId}/stats/{gameId}/"
    globalURL = f"https://steamcommunity.com/stats/{gameId}/achievements/"
    playerResponse = requests.get(playerURL, headers=headers, proxies=proxies)
    globalResponse = requests.get(globalURL, headers=headers, proxies=proxies)
    res = {
        'playerResponse': playerResponse,
        'globalResponse': globalResponse
    }
    return res

def wirteDown(achievements, fileName):
    if not achievements:
        print("\n传递的字典为空，无成就可供保存。")
    else:
        print(f"\n正在将 {fileName} 保存到当前目录下的 {fileName}.txt 文件中...")
        with open(os.path.join(script_dir, f"{fileName}.txt"), "w", encoding="utf-8") as f:
            for name, description in achievements.items():
                f.write(f"{name}：{description}\n")
        print(f"{fileName}.txt 文件已保存。")
        print(f"将保存的成就总数为: {len(achievements)} 项。")

def handlePlayer(playerResponse):
    if playerResponse.status_code == 200:
        print("\n请求成功，正在解析页面...")
        soup = BeautifulSoup(playerResponse.content, "html.parser")
        achieve_containers = soup.find_all("div", class_="achieveTxtHolder")
        unlocked_achievements = {}
        for container in achieve_containers:
            achievement_name = container.find("h3", class_="ellipsis").get_text(strip=True)
            unlock_time = container.find("div", class_="achieveUnlockTime")
            if unlock_time:
                achievement_desc = container.find("h5").get_text(strip=True)
                unlocked_achievements[achievement_name] = achievement_desc
        return unlocked_achievements
    else:
        print("\n请求失败，状态码：" + str(playerResponse.status_code))

def handleGlobal(globalResponse):
    if globalResponse.status_code == 200:
        print("\n请求成功，正在解析页面...")
        soup = BeautifulSoup(globalResponse.content, "html.parser")
        achieve_containers = soup.find_all("div", class_="achieveRow")
        all_achievements = {}
        for container in achieve_containers:
            achievement_name = container.find("h3").get_text(strip=True)
            achievement_desc = container.find("h5").get_text(strip=True)
            all_achievements[achievement_name] = achievement_desc
        return all_achievements
    else:
        print("\n请求失败，状态码：" + str(globalResponse.status_code))

def handleResponse(playerResponse, globalResponse):
    player_achievements = handlePlayer(playerResponse)
    wirteDown(player_achievements, "unlocked_achievements")

    global_achievements = handleGlobal(globalResponse)
    wirteDown(global_achievements, "all_achievements")

    # 计算差异
    diff_achievements = {}
    for name, desc in global_achievements.items():
        if name not in player_achievements:
            diff_achievements[name] = desc
    if not diff_achievements:
        print("\n没有找到任何差异成就。")
    else:
      print(f"\n找到的差异成就总数为: {len(diff_achievements)} 项。")
      wirteDown(diff_achievements, "diff_achievements")

if __name__ == "__main__":
    config = getConfig()
    if config:
        res = getResponse(config['playerId'], config['gameId'], config['headers'], config['proxies'])
        handleResponse(res['playerResponse'], res['globalResponse'])
    print("\n程序终了。")
