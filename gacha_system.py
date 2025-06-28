import random
from typing import List, Dict, Tuple
from config import CHARACTERS, GACHA_SETTINGS

class GachaSystem:
    def __init__(self):
        self.characters = CHARACTERS
        self.settings = GACHA_SETTINGS
    
    def single_pull(self, user_stats: Dict) -> Tuple[str, str]:
        """
        单抽逻辑
        返回: (稀有度, 角色名称)
        """
        pulls_since_3star = user_stats.get("pulls_since_3star", 0)
        pulls_since_2star = user_stats.get("pulls_since_2star", 0)
        
        # 检查保底机制
        if pulls_since_3star >= self.settings["保底机制"]["3星保底"] - 1:
            # 触发3星保底
            rarity = "3星"
        elif pulls_since_2star >= self.settings["保底机制"]["2星保底"] - 1:
            # 触发2星保底
            rarity = "2星"
        else:
            # 正常抽卡
            rarity = self._determine_rarity()
        
        # 随机选择角色
        character = self._select_character(rarity)
        
        return rarity, character["名称"]
    
    def ten_pull(self, user_stats: Dict) -> List[Tuple[str, str]]:
        """
        十连抽逻辑
        返回: [(稀有度, 角色名称), ...]
        """
        results = []
        pulls_since_3star = user_stats.get("pulls_since_3star", 0)
        pulls_since_2star = user_stats.get("pulls_since_2star", 0)
        
        # 十连抽保证至少有一个2星或以上
        guaranteed_rarity = "2星" if pulls_since_2star >= 9 else None
        
        for i in range(10):
            if i == 9 and guaranteed_rarity:
                # 最后一抽触发保底
                rarity = guaranteed_rarity
            elif pulls_since_3star >= self.settings["保底机制"]["3星保底"] - 1:
                # 触发3星保底
                rarity = "3星"
            else:
                # 正常抽卡
                rarity = self._determine_rarity()
            
            character = self._select_character(rarity)
            results.append((rarity, character["名称"]))
        
        return results
    
    def _determine_rarity(self) -> str:
        """根据概率确定稀有度"""
        rand = random.random()
        cumulative_prob = 0
        
        for rarity, data in self.characters.items():
            cumulative_prob += data["概率"]
            if rand <= cumulative_prob:
                return rarity
        
        # 默认返回1星
        return "1星"
    
    def _select_character(self, rarity: str) -> Dict:
        """从指定稀有度中随机选择角色"""
        characters = self.characters[rarity]["角色"]
        return random.choice(characters)
    
    def get_character_image(self, rarity: str, character_name: str) -> str:
        """获取角色图片URL"""
        characters = self.characters[rarity]["角色"]
        for character in characters:
            if character["名称"] == character_name:
                return character.get("图片", "")
        return ""
    
    def get_rarity_emoji(self, rarity: str) -> str:
        """获取稀有度对应的表情符号"""
        emoji_map = {
            "3星": "⭐⭐⭐",
            "2星": "⭐⭐",
            "1星": "⭐"
        }
        return emoji_map.get(rarity, "⭐")
    
    def format_pull_result(self, rarity: str, character_name: str) -> str:
        """格式化单抽结果"""
        emoji = self.get_rarity_emoji(rarity)
        return f"{emoji} {character_name} ({rarity})"
    
    def format_ten_pull_results(self, results: List[Tuple[str, str]]) -> str:
        """格式化十连抽结果"""
        lines = ["🎉 十连抽结果："]
        
        # 按稀有度排序显示
        sorted_results = sorted(results, key=lambda x: {"3星": 3, "2星": 2, "1星": 1}[x[0]], reverse=True)
        
        for rarity, character_name in sorted_results:
            emoji = self.get_rarity_emoji(rarity)
            lines.append(f"{emoji} {character_name}")
        
        # 统计信息
        rarity_counts = {}
        for rarity, _ in results:
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        lines.append("\n📊 统计：")
        for rarity in ["3星", "2星", "1星"]:
            count = rarity_counts.get(rarity, 0)
            if count > 0:
                emoji = self.get_rarity_emoji(rarity)
                lines.append(f"{emoji} {rarity}: {count}个")
        
        return "\n".join(lines) 