import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.realpath(__file__))

# 支持的语言列表
SUPPORTED_LANGUAGES = {
    'chinese': 'zh-CN',
    'c': 'zh-CN',
    'english': 'en-US',
    'e': 'en-US'
}

# 默认代理设置（可自动检测系统代理）
DEFAULT_PROXIES = {
    'http': os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy'),
    'https': os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
}

def get_language_headers():
    """获取用户选择的语言并返回对应的请求头"""
    while True:
        language = input("请选择Steam响应语言（Chinese/English，或输入 c/e）：").strip().lower()
        if language in SUPPORTED_LANGUAGES:
            headers = {
                "Accept-Language": SUPPORTED_LANGUAGES[language]
            }
            print(f"已选择 {language} 作为Steam响应语言。")
            return headers
        else:
            print("无效的输入，请选择 'Chinese' 或 'English'，即 'c' 或 'e'。")

def validate_steam_url(url):
    """验证Steam个人资料URL是否有效，并提取playerId和gameId"""
    pattern = r"/id/(\d+)/stats/(\d+)/"
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    else:
        print("无效的个人资料URL，请检查输入是否正确。")
        return None, None

def get_proxy_settings():
    """获取用户代理设置"""
    use_proxy = input("是否开启代理？(y/n): ").strip().lower()
    if use_proxy == 'y':
        proxy_address = input("请输入代理地址（例如：http://127.0.0.1:7897）：").strip()
        if not proxy_address.startswith(('http://', 'https://')):
            proxy_address = f"http://{proxy_address}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        print(f"已开启代理：{proxy_address}")
    else:
        proxies = DEFAULT_PROXIES if DEFAULT_PROXIES['http'] else {}
        print("未开启代理，使用系统默认代理设置。" if proxies else "未开启代理。")
    return proxies

def get_config():
    """获取用户配置"""
    headers = get_language_headers()
    while True:
        player_url = input("请输入游戏的个人成就进度页面地址URL（例如：https://steamcommunity.com/id/43xxx123/stats/2358720/achievements/）：").strip()
        player_id, game_id = validate_steam_url(player_url)
        if player_id and game_id:
            break
    proxies = get_proxy_settings()
    return {
        'game_id': game_id,
        'player_id': player_id,
        'headers': headers,
        'proxies': proxies
    }

def get_response(player_id, game_id, headers, proxies):
    """发送HTTP请求获取用户成就页面和全局成就页面"""
    player_url = f"https://steamcommunity.com/id/{player_id}/stats/{game_id}/"
    global_url = f"https://steamcommunity.com/stats/{game_id}/achievements/"
    try:
        player_response = requests.get(player_url, headers=headers, proxies=proxies, timeout=10)
        global_response = requests.get(global_url, headers=headers, proxies=proxies, timeout=10)
        player_response.raise_for_status()
        global_response.raise_for_status()
        return {
            'player_response': player_response,
            'global_response': global_response
        }
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return None

def write_achievements_to_file(achievements, file_name):
    """将成就信息保存到文件中"""
    if not achievements:
        print(f"\n{file_name} 为空，无成就可供保存。")
    else:
        file_path = os.path.join(script_dir, f"{file_name}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            for name, description in achievements.items():
                f.write(f"{name}：{description}\n")
        print(f"{file_name}.txt 文件已保存到 {file_path}。")
        print(f"保存的成就总数为: {len(achievements)} 项。")

def parse_achievements(response, is_global=False):
    """解析成就页面内容"""
    if response.status_code == 200:
        print("\n请求成功，正在解析页面...")
        soup = BeautifulSoup(response.content, "html.parser")
        achievements = {}
        if is_global:
            containers = soup.find_all("div", class_="achieveRow")
        else:
            containers = soup.find_all("div", class_="achieveTxtHolder")
        for container in containers:
            name = container.find("h3").get_text(strip=True)
            desc = container.find("h5").get_text(strip=True)
            if not is_global and not container.find("div", class_="achieveUnlockTime"):
                continue  # 仅保存已解锁的成就
            achievements[name] = desc
        return achievements
    else:
        print(f"\n请求失败，状态码：{response.status_code}")
        return None

def handle_response(player_response, global_response):
    """处理HTTP响应并保存成就信息"""
    player_achievements = parse_achievements(player_response)
    if player_achievements:
        write_achievements_to_file(player_achievements, "unlocked_achievements")

    global_achievements = parse_achievements(global_response, is_global=True)
    if global_achievements:
        write_achievements_to_file(global_achievements, "all_achievements")

    # 计算未解锁的成就
    if player_achievements and global_achievements:
        diff_achievements = {
            name: desc for name, desc in global_achievements.items()
            if name not in player_achievements
        }
        if not diff_achievements:
            print("\n没有找到任何未解锁的成就。")
        else:
            print(f"\n找到的未解锁成就总数为: {len(diff_achievements)} 项。")
            write_achievements_to_file(diff_achievements, "diff_achievements")

if __name__ == "__main__":
    print("Steam成就分析工具")
    config = get_config()
    if config:
        res = get_response(config['player_id'], config['game_id'], config['headers'], config['proxies'])
        if res:
            handle_response(res['player_response'], res['global_response'])
    print("\n程序结束。")
