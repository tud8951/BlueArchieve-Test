import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class UserDatabase:
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.users = self._load_users()
        # 兑换码配置
        self.redeem_codes = {
            "090828": {
                "reward": 10000,
                "description": "新手兑换码"
            }
        }
    
    def _load_users(self) -> Dict:
        """加载用户数据"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """保存用户数据"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def _migrate_user_data(self, user: Dict) -> Dict:
        """迁移用户数据，添加新字段"""
        # 添加last_signin字段
        if "last_signin" not in user:
            user["last_signin"] = None
        
        # 添加redeemed_codes字段
        if "redeemed_codes" not in user:
            user["redeemed_codes"] = []
        
        return user
    
    def get_user(self, user_id: int) -> Dict:
        """获取用户信息，如果不存在则创建"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            self.users[user_id_str] = {
                "user_id": user_id,
                "diamonds": 10000,  # 初始钻石
                "total_pulls": 0,
                "pulls_since_3star": 0,  # 距离上次3星的抽数
                "pulls_since_2star": 0,  # 距离上次2星的抽数
                "stats": {
                    "3星": 0,
                    "2星": 0,
                    "1星": 0
                },
                "history": [],
                "created_at": datetime.now().isoformat(),
                "last_signin": None,  # 新增签到时间
                "redeemed_codes": []  # 新增已兑换的兑换码
            }
            self._save_users()
        else:
            # 迁移现有用户数据
            self.users[user_id_str] = self._migrate_user_data(self.users[user_id_str])
            self._save_users()
        
        return self.users[user_id_str]
    
    def update_user(self, user_id: int, updates: Dict):
        """更新用户信息"""
        user_id_str = str(user_id)
        if user_id_str in self.users:
            self.users[user_id_str].update(updates)
            self._save_users()
    
    def add_pull_history(self, user_id: int, rarity: str, character_name: str):
        """添加抽卡历史"""
        user = self.get_user(user_id)
        history_entry = {
            "rarity": rarity,
            "character": character_name,
            "timestamp": datetime.now().isoformat()
        }
        user["history"].append(history_entry)
        
        # 更新统计
        user["stats"][rarity] += 1
        user["total_pulls"] += 1
        
        # 更新保底计数
        if rarity == "3星":
            user["pulls_since_3star"] = 0
        else:
            user["pulls_since_3star"] += 1
            
        if rarity == "2星":
            user["pulls_since_2star"] = 0
        else:
            user["pulls_since_2star"] += 1
        
        self._save_users()
    
    def spend_diamonds(self, user_id: int, amount: int) -> bool:
        """消费钻石，返回是否成功"""
        user = self.get_user(user_id)
        if user["diamonds"] >= amount:
            user["diamonds"] -= amount
            self._save_users()
            return True
        return False
    
    def get_user_stats(self, user_id: int) -> Dict:
        """获取用户统计信息"""
        user = self.get_user(user_id)
        return {
            "diamonds": user["diamonds"],
            "total_pulls": user["total_pulls"],
            "stats": user["stats"],
            "pulls_since_3star": user["pulls_since_3star"],
            "pulls_since_2star": user["pulls_since_2star"]
        }

    def daily_signin(self, user_id: int, reward: int = 10000) -> (bool, int):
        """每日签到，返回(是否成功, 当前钻石数)"""
        user = self.get_user(user_id)
        now = datetime.now()
        
        # 确保last_signin字段存在
        if "last_signin" not in user:
            user["last_signin"] = None
            
        last_signin = user["last_signin"]
        if last_signin:
            last_time = datetime.fromisoformat(last_signin)
            if last_time.date() == now.date():
                return False, user["diamonds"]  # 今天已签到
        # 发放奖励
        user["diamonds"] += reward
        user["last_signin"] = now.isoformat()
        self._save_users()
        return True, user["diamonds"]

    def redeem_code(self, user_id: int, code: str) -> (bool, str, int):
        """兑换码兑换，返回(是否成功, 消息, 当前钻石数)"""
        user = self.get_user(user_id)
        code = code.upper().strip()
        
        # 确保redeemed_codes字段存在
        if "redeemed_codes" not in user:
            user["redeemed_codes"] = []
        
        # 检查兑换码是否存在
        if code not in self.redeem_codes:
            return False, "❌ 兑换码不存在！", user["diamonds"]
        
        # 检查是否已经兑换过
        if code in user["redeemed_codes"]:
            return False, "❌ 你已经使用过这个兑换码了！", user["diamonds"]
        
        # 发放奖励
        reward = self.redeem_codes[code]["reward"]
        user["diamonds"] += reward
        user["redeemed_codes"].append(code)
        self._save_users()
        
        return True, f"✅ 兑换成功！获得{reward}钻石！", user["diamonds"] 