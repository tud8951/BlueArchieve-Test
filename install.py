#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
蔚蓝档案抽卡机器人安装脚本
"""

import os
import sys
import subprocess
import shutil

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本检查通过：{version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    
    if success:
        print("✅ 依赖包安装成功")
        return True
    else:
        print("❌ 依赖包安装失败")
        print("错误信息：", stderr)
        return False

def setup_env_file():
    """设置环境变量文件"""
    if os.path.exists('.env'):
        print("✅ .env 文件已存在")
        return True
    
    if os.path.exists('env_example.txt'):
        try:
            shutil.copy('env_example.txt', '.env')
            print("✅ 已创建 .env 文件")
            print("⚠️  请编辑 .env 文件，设置你的 Telegram Bot Token")
            return True
        except Exception as e:
            print(f"❌ 创建 .env 文件失败：{e}")
            return False
    else:
        print("❌ 未找到 env_example.txt 文件")
        return False

def main():
    """主函数"""
    print("🎮 蔚蓝档案抽卡机器人安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("\n💡 请手动运行：pip install -r requirements.txt")
        sys.exit(1)
    
    # 设置环境文件
    if not setup_env_file():
        print("\n💡 请手动创建 .env 文件并设置 Bot Token")
        sys.exit(1)
    
    print("\n🎉 安装完成！")
    print("\n📋 接下来的步骤：")
    print("1. 编辑 .env 文件，设置你的 Telegram Bot Token")
    print("2. 运行 python run_bot.py 启动机器人")
    print("3. 在Telegram中发送 /start 开始使用")
    
    print("\n📖 更多信息请查看 README.md")

if __name__ == "__main__":
    main() 