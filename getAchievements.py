import os
import requests
from bs4 import BeautifulSoup

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.realpath(__file__))

# 询问语言选择
while True:
    language = input("请选择steam响应语言（Chinese/English）：").strip().lower()
    if language in ['chinese', 'c']:
        headers = {
            "Accept-Language": "zh-CN"  # 设置简体中文
        }
        print("已选择中文作为Steam响应语言。")
        break
    elif language in ['english', 'e']:
        headers = {
            "Accept-Language": "en-US"  # 设置英文
        }
        print("English language selected for Steam display.")
        break
    else:
        print("无效的输入，请选择 'Chinese' 或 'English'，即 'c' 或 'e'。")

# 通过终端输入获取Steam个人资料URL，默认值为一个示例URL
url = input("请输入Steam个人资料URL（例如：https://steamcommunity.com/id/430426/stats/2358720/achievements/）：")

# 询问是否使用代理
while True:
    use_proxy = input("是否开启代理？(y/n): ").strip().lower()
    if use_proxy in ['y', 'n']:
        break
    else:
        print("请输入 'y' 或 'n' 来选择是否开启代理。")

# 设置代理，若直连请求失败，则启用，否则请注释或删去
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

# 发送请求，获取页面内容
response = requests.get(url, headers=headers, proxies=proxies)

# 确保请求成功
if response.status_code == 200:
    print("\n请求成功，正在解析页面...")

    # 使用 BeautifulSoup 解析页面内容
    soup = BeautifulSoup(response.content, "html.parser")

    # 查找所有的成就容器
    achieve_containers = soup.find_all("div", class_="achieveTxtHolder")

    # 用于存储已解锁的成就字典
    unlocked_achievements = {}
    # 用于存储读取文档获得的全成就的字典
    all_achievements = {}
    # 用于存储差集字典，即未解锁的成就
    diff_achievements = {}

    # 遍历每个成就容器
    for container in achieve_containers:
        # 获取成就名称
        achievement_name = container.find("h3", class_="ellipsis").get_text(strip=True)
        
        # 查找是否有解锁时间元素
        unlock_time = container.find("div", class_="achieveUnlockTime")
        
        # 判断是否有解锁时间元素，只有有解锁时间的才是已解锁的成就
        if unlock_time:
            # 获取成就描述（h5 标签内容）
            achievement_desc = container.find("h5").get_text(strip=True)
            
            # 将已解锁的成就以字典形式存储
            unlocked_achievements[achievement_name] = achievement_desc

    # 将已解锁成就保存到当前目录下的 unlocked_achievements.txt 文件中，若无解锁成就则不创建文件
    if not unlocked_achievements:
        print("\n您似乎还没有解锁任何成就，或者检查您 Steam 个人资料的隐私设置。")
    else:
        print("\n正在将已解锁的成就保存到当前目录下的 unlocked_achievements.txt 文件中...")
        with open(os.path.join(script_dir, "unlocked_achievements.txt"), "w", encoding="utf-8") as f:
            for name, description in unlocked_achievements.items():
                f.write(f"{name}：{description}\n")
        # 输出已解锁成就的总数
        print("unlocked_achievements.txt 文件已保存。")
        print(f"找到已解锁的成就总数为: {len(unlocked_achievements)} 项。")


    # 判断已解锁成就的字典是否为空，如果为空，说明还没有解锁任何成就
    if not unlocked_achievements:
        print("\n您似乎还没有解锁任何成就，或者检查您 Steam 个人资料的隐私设置。")
    else:
        print("\n全成就列表应在当前目录下的 all_achievements.txt 文件中，内容格式预期为\"成就名：成就描述\"（：为中文冒号，\"\"为英文双引号仅作标识，无实际意义。），每行一个成就。")
        print("开始读取文档...")

        # 检查文件是否存在且是否为有效的文件
        all_achievements_file = os.path.join(script_dir, "all_achievements.txt")
        if not os.path.exists(all_achievements_file):
            print(f"\n· 警告：文件 '{all_achievements_file}' 不存在！程序将终止。")
            exit(1)  # 文件不存在，程序终止

        # 尝试打开并读取文件
        try:
            with open(all_achievements_file, "r", encoding="utf-8") as f:
                for line in f:
                    # 确保每行包含分隔符 "："
                    if "：" in line:
                        achievement_name, achievement_desc = line.strip().split("：", 1)  # 只拆分第一次出现的 "："
                        all_achievements[achievement_name] = achievement_desc
                    else:
                        print(f"· 警告：文件 '{all_achievements_file}' 中的一行不符合预期格式，已跳过: {line.strip()}")

        except Exception as e:
            print(f"· 警告：读取文件 '{all_achievements_file}' 时发生错误：{e}")
            exit(1)  # 发生错误时退出程序

        # 输出全成就的字典
        # print("\n读取到文档内容为:")
        # for name, description in all_achievements.items():
        #     print(f"成就名称: {name}, 描述: {description}")

        # 输出全成就的总数
        print(f"\n文档内有效计数为: {len(all_achievements)} 项。")

        '''
        比对逻辑：
        将已解锁成就的字典(unlocked_achievements)键名和全成就的字典(all_achievements)键名进行比较，
        如果二者相同，则说明该成就已解锁，不做任何操作；
        反之则将文档中剩下未解锁的成就添加到差集字典(diff_achievements)中。
        '''
        # 开始比对已解锁的成就和文档内的全成就
        print("\n开始比对已解锁的成就和文档内的全成就...")

        # 找出未解锁的成就
        for achievement_name, achievement_desc in all_achievements.items():
            if achievement_name not in unlocked_achievements:
                diff_achievements[achievement_name] = achievement_desc

        # 输出未解锁成就的字典
        if diff_achievements:
            print("\n比对终了。")
            print("\n未解锁的成就:")
            for name, description in diff_achievements.items():
                print(f"成就名称: {name}, 描述: {description}")
            print(f"\n未解锁的成就总数: {len(diff_achievements)} 项。")
            print(f"\n正在将未解锁的成就保存到当前目录下的 diff_achievements.txt 文件中...")
            # 将未解锁的成就保存到当前目录下的 diff_achievements.txt 文件中
            with open(os.path.join(script_dir, "diff_achievements.txt"), "w", encoding="utf-8") as f:
                for name, description in diff_achievements.items():
                    f.write(f"{name}：{description}\n")
            print("\ndiff_achievements.txt 文件已保存。")
        else:
            print("\n恭喜您，所有成就都已解锁！")

else:
    print("\n请求失败，状态码：" + str(response.status_code))

print("\n程序终了。")
