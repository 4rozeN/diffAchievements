# diffAchievements

项目地址Github：[diffAchievements](https://github.com/4rozeN/diffAchievements)

## 关于

diffAchievements 是一个获取 Steam 某一个特定的游戏的已解锁成就与全成就列表进行比对得到未解锁成就列表的工具脚本。

旨在帮助玩家更好的达成某游戏的全成就，或是进行查漏补缺。

## 我为什么需要它

由于 Steam 会根据你的游戏进度或者说成就进度，将一些成就隐藏起来，这导致你无法查看全部成就详情，哪怕能查看，**如果游戏成就项足够多，玩家想要知道自己还剩具体的哪些成就没完成将是一个工作负担较大的事。**

该脚本可以帮你省去查找已解锁成就和比对环节，你只需为脚本提供你的某个游戏的当前成就进度页面地址。

该地址应当是：

```bash
https://steamcommunity.com/id/430426/stats/2358720/?tab=achievements
```

示例图如下：
<img src="https://gitee.com/CSJ021005/f0ur_lin_-picgo/raw/master/202501181826412.png" alt="image-20250118182611298" style="zoom:50%;" />

该页面可以在`个人资料->所有最近玩过的->我的游戏统计数据->我的成就`中找到：
<img src="https://gitee.com/CSJ021005/f0ur_lin_-picgo/raw/master/202501181841996.png" alt="image-20250118184103953" style="zoom:50%;" />
<img src="https://gitee.com/CSJ021005/f0ur_lin_-picgo/raw/master/202501181841155.png" alt="image-20250118184157100" style="zoom:50%;" />
<img src="https://gitee.com/CSJ021005/f0ur_lin_-picgo/raw/master/202501181843856.png" alt="image-20250118184303810" style="zoom:50%;" />

## 设置成就可见性

为了可以通过网络请求访问到你的游戏成就详情，请在 Steam 的隐私设置中将游戏详情一项设置为公开。

这将使得你的某个游戏成就进度可以通过以下链接进行访问：

```bash
https://steamcommunity.com/id/yourId/edit/settings
```

该设置示例图为：
<img src="https://gitee.com/CSJ021005/f0ur_lin_-picgo/raw/master/202501181828813.png" alt="image-20250118182813774" style="zoom:50%;" />

## 准备全成就文档

此项废弃，现在并不需要你准备一份全成就的列表，脚本将自动通过全球玩家成就表进行解析。

**请注意！**==某些游戏在全球成就表下部分成就的说明**会被隐藏**，故脚本保存的部分也会隐藏。若有需要，只得自行进行搜索成就详情说明。==

## 使用

将仓库 clone 或下载到本地目录中，例如：

```bash
git clone https://github.com/4rozeN/diffAchievements.git
```

若无法下载，可以[点这里](https://wwte.lanzouu.com/i1Xyv2la600f)使用蓝奏云进行下载。

进入项目目录，使用python命令运行：

```shell
python diffAchievements.py
```

**该命令要求 python 拥有环境变量。**

根据提示输入必要信息即可。

## 一份使用示例

```shell
PS E:\Coding\py\diffAchievements> python .\diffAchievements.py
请选择steam响应语言（Chinese/English）：c
已选择中文作为Steam响应语言。
请输入游戏的个人成就进度页面地址URL（例如：https://steamcommunity.com/id/43xxx123/stats/2358720/achievements/）：https://steamcommunity.com/id/430426/stats/578080/?tab=achievements
是否开启代理？(y/n): y
请输入代理地址（例如：http://127.0.0.1:7897）：http://127.0.0.1:7897
已开启代理：http://127.0.0.1:7897

请求成功，正在解析页面...

正在将 unlocked_achievements 保存到当前目录下的 unlocked_achievements.txt 文件中...
unlocked_achievements.txt 文件已保存。
将保存的成就总数为: 19 项。

请求成功，正在解析页面...

正在将 all_achievements 保存到当前目录下的 all_achievements.txt 文件中...
all_achievements.txt 文件已保存。
将保存的成就总数为: 36 项。

找到的差异成就总数为: 17 项。

正在将 diff_achievements 保存到当前目录下的 diff_achievements.txt 文件中...
diff_achievements.txt 文件已保存。
将保存的成就总数为: 17 项。

程序终了。
PS E:\Coding\py\diffAchievements>
```

最终将生成三份txt文件于脚本同目录下：

1. `all_achievements.txt`
2. `diff_achievements.txt`
3. `unlocked_achievements.txt`
