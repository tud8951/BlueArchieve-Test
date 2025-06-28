#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
蔚蓝档案抽卡系统测试脚本
"""

import random
from gacha_system import GachaSystem
from database import UserDatabase

def test_gacha_system():
    """测试抽卡系统"""
    print("🎮 蔚蓝档案抽卡系统测试")
    print("=" * 50)
    
    # 初始化系统
    gacha = GachaSystem()
    db = UserDatabase("test_users.json")
    
    # 创建测试用户
    test_user_id = 12345
    user_stats = db.get_user_stats(test_user_id)
    
    print(f"💰 初始钻石余额：{user_stats['diamonds']:,}")
    print(f"📊 初始抽数：{user_stats['total_pulls']}")
    print()
    
    # 测试单抽
    print("🎲 测试单抽：")
    for i in range(5):
        rarity, character = gacha.single_pull(user_stats)
        emoji = gacha.get_rarity_emoji(rarity)
        print(f"  第{i+1}抽：{emoji} {character} ({rarity})")
        db.add_pull_history(test_user_id, rarity, character)
        user_stats = db.get_user_stats(test_user_id)
    print()
    
    # 测试十连抽
    print("🎉 测试十连抽：")
    results = gacha.ten_pull(user_stats)
    result_text = gacha.format_ten_pull_results(results)
    print(result_text)
    
    # 记录十连抽结果
    for rarity, character in results:
        db.add_pull_history(test_user_id, rarity, character)
    
    print()
    
    # 显示最终统计
    final_stats = db.get_user_stats(test_user_id)
    print("📊 最终统计：")
    print(f"💰 剩余钻石：{final_stats['diamonds']:,}")
    print(f"🎯 总抽数：{final_stats['total_pulls']}")
    print(f"⭐⭐⭐ 3星：{final_stats['stats']['3星']}个")
    print(f"⭐⭐ 2星：{final_stats['stats']['2星']}个")
    print(f"⭐ 1星：{final_stats['stats']['1星']}个")
    
    # 计算概率
    if final_stats['total_pulls'] > 0:
        rate_3star = (final_stats['stats']['3星'] / final_stats['total_pulls']) * 100
        rate_2star = (final_stats['stats']['2星'] / final_stats['total_pulls']) * 100
        rate_1star = (final_stats['stats']['1星'] / final_stats['total_pulls']) * 100
        print(f"📈 实际概率：")
        print(f"   3星：{rate_3star:.1f}% (理论2.5%)")
        print(f"   2星：{rate_2star:.1f}% (理论18.5%)")
        print(f"   1星：{rate_1star:.1f}% (理论79%)")
    
    print("\n✅ 测试完成！")

def test_probability_simulation():
    """测试概率模拟"""
    print("\n🎯 概率模拟测试 (1000次抽卡)")
    print("=" * 50)
    
    gacha = GachaSystem()
    db = UserDatabase("test_prob.json")
    test_user_id = 99999
    
    # 重置用户数据
    user_stats = {
        "diamonds": 1000000,
        "total_pulls": 0,
        "pulls_since_3star": 0,
        "pulls_since_2star": 0,
        "stats": {"3星": 0, "2星": 0, "1星": 0}
    }
    
    # 模拟1000次抽卡
    for i in range(1000):
        rarity, character = gacha.single_pull(user_stats)
        user_stats["stats"][rarity] += 1
        user_stats["total_pulls"] += 1
        
        # 更新保底计数
        if rarity == "3星":
            user_stats["pulls_since_3star"] = 0
        else:
            user_stats["pulls_since_3star"] += 1
            
        if rarity == "2星":
            user_stats["pulls_since_2star"] = 0
        else:
            user_stats["pulls_since_2star"] += 1
    
    # 显示结果
    total = user_stats["total_pulls"]
    print(f"📊 模拟结果：")
    print(f"   总抽数：{total}")
    print(f"   ⭐⭐⭐ 3星：{user_stats['stats']['3星']}个 ({(user_stats['stats']['3星']/total)*100:.2f}%)")
    print(f"   ⭐⭐ 2星：{user_stats['stats']['2星']}个 ({(user_stats['stats']['2星']/total)*100:.2f}%)")
    print(f"   ⭐ 1星：{user_stats['stats']['1星']}个 ({(user_stats['stats']['1星']/total)*100:.2f}%)")
    
    print("\n✅ 概率模拟测试完成！")

if __name__ == "__main__":
    test_gacha_system()
    test_probability_simulation() 