# 蔚蓝档案抽卡机器人配置

# 角色数据
CHARACTERS = {
    "3星": {
        "概率": 0.025,  # 2.5%
        "角色": [
            {"名称": "阿露", "图片": "https://i.imgur.com/example1.jpg"},
            {"名称": "白子", "图片": "https://i.imgur.com/example2.jpg"},
            {"名称": "日富美", "图片": "https://i.imgur.com/example3.jpg"},
            {"名称": "优香", "图片": "https://i.imgur.com/example4.jpg"},
            {"名称": "星野", "图片": "https://i.imgur.com/example5.jpg"},
            {"名称": "千世", "图片": "https://i.imgur.com/example6.jpg"},
            {"名称": "明日奈", "图片": "https://i.imgur.com/example7.jpg"},
            {"名称": "花凛", "图片": "https://i.imgur.com/example8.jpg"},
            {"名称": "睦月", "图片": "https://i.imgur.com/example9.jpg"},
            {"名称": "芹香", "图片": "https://i.imgur.com/example10.jpg"},
        ]
    },
    "2星": {
        "概率": 0.185,  # 18.5%
        "角色": [
            {"名称": "小玉", "图片": "https://i.imgur.com/example11.jpg"},
            {"名称": "绿", "图片": "https://i.imgur.com/example12.jpg"},
            {"名称": "茜", "图片": "https://i.imgur.com/example13.jpg"},
            {"名称": "桃井", "图片": "https://i.imgur.com/example14.jpg"},
            {"名称": "野宫", "图片": "https://i.imgur.com/example15.jpg"},
            {"名称": "千夏", "图片": "https://i.imgur.com/example16.jpg"},
            {"名称": "佳代子", "图片": "https://i.imgur.com/example17.jpg"},
            {"名称": "铃美", "图片": "https://i.imgur.com/example18.jpg"},
            {"名称": "莲见", "图片": "https://i.imgur.com/example19.jpg"},
            {"名称": "泉", "图片": "https://i.imgur.com/example20.jpg"},
        ]
    },
    "1星": {
        "概率": 0.79,  # 79%
        "角色": [
            {"名称": "爱丽丝", "图片": "https://i.imgur.com/example21.jpg"},
            {"名称": "小春", "图片": "https://i.imgur.com/example22.jpg"},
            {"名称": "小满", "图片": "https://i.imgur.com/example23.jpg"},
            {"名称": "小桃", "图片": "https://i.imgur.com/example24.jpg"},
            {"名称": "小绿", "图片": "https://i.imgur.com/example25.jpg"},
            {"名称": "小蓝", "图片": "https://i.imgur.com/example26.jpg"},
            {"名称": "小红", "图片": "https://i.imgur.com/example27.jpg"},
            {"名称": "小黄", "图片": "https://i.imgur.com/example28.jpg"},
            {"名称": "小紫", "图片": "https://i.imgur.com/example29.jpg"},
            {"名称": "小白", "图片": "https://i.imgur.com/example30.jpg"},
        ]
    }
}

# 抽卡设置
GACHA_SETTINGS = {
    "单抽价格": 120,  # 钻石
    "十连价格": 1200,  # 钻石
    "保底机制": {
        "3星保底": 200,  # 200抽保底3星
        "2星保底": 10,   # 10抽保底2星
    }
}

# 欢迎消息
WELCOME_MESSAGE = """
🎮 欢迎来到蔚蓝档案抽卡模拟器！

可用命令：
/start - 开始使用
/gacha - 单抽 (120钻石)
/tenpull - 十连抽 (1200钻石)
/balance - 查看钻石余额
/stats - 查看抽卡统计
/sign - 每日签到 (10000钻石)
/code - 兑换码兑换
/help - 显示帮助信息

祝你抽卡欧气满满！✨
"""

# 帮助消息
HELP_MESSAGE = """
📖 蔚蓝档案抽卡机器人使用指南

🎯 抽卡概率：
• 3星角色：2.5%
• 2星角色：18.5%
• 1星角色：79%

💰 抽卡费用：
• 单抽：120钻石
• 十连：1200钻石

🎁 保底机制：
• 200抽内必定获得3星角色
• 10抽内必定获得2星角色

📊 统计功能：
• 查看抽卡历史
• 统计各稀有度获得数量
• 计算抽卡花费

🎁 每日签到：
• 使用 /sign 每日签到
• 每次签到获得10000钻石

🎫 兑换码功能：
• 使用 /code 输入兑换码
• 兑换码：群中获取
• 每个兑换码每个用户只能使用一次

开始你的抽卡之旅吧！🎲
""" 