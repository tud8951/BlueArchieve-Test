#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
蔚蓝档案抽卡机器人启动脚本
"""

import os
import sys
import time

def main():
    """主函数"""
    print("🎮 蔚蓝档案抽卡机器人启动器")
    print("=" * 50)
    
    print("✅ Token已配置")
    print("🚀 启动机器人...")
    
    try:
        from bot import main as bot_main
        print("✅ 机器人启动成功！")
        print("📱 现在可以在Telegram中使用机器人了")
        print("💡 发送 /start 开始使用")
        print("\n按 Ctrl+C 停止机器人")
        
        bot_main()
        
    except KeyboardInterrupt:
        print("\n\n👋 机器人已停止")
    except ImportError as e:
        print(f"\n❌ 导入错误：{e}")
        print("请确保已安装所有依赖包：pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        print("请检查网络连接和Bot Token是否正确")
        sys.exit(1)

if __name__ == "__main__":
    main() 