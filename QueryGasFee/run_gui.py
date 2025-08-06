#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gas Fee Tracker GUI启动器

简单的启动脚本，用于启动GUI应用
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """主启动函数"""
    try:
        # 检查必要的依赖
        required_modules = ['tkinter', 'asyncio', 'aiohttp', 'requests']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print(f"❌ 缺少必要的模块: {', '.join(missing_modules)}")
            print("请运行以下命令安装依赖:")
            print("pip install aiohttp requests")
            input("按回车键退出...")
            return
        
        # 检查项目文件
        required_files = ['main.py', 'config.py', 'config_manager.py']
        missing_files = []
        
        for file in required_files:
            if not (current_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ 缺少必要的项目文件: {', '.join(missing_files)}")
            print("请确保在正确的项目目录中运行此脚本")
            input("按回车键退出...")
            return
        
        print("🚀 启动 Gas Fee Tracker GUI...")
        
        # 导入并启动GUI
        from gui_app import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有必要的模块都已安装")
        input("按回车键退出...")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()