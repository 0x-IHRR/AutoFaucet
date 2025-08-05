#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
提供简单的命令行接口来运行Gas费用查询
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """主函数"""
    print("🚀 Web3 Gas Fee 查询工具")
    print("=" * 50)
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "cli":
            # 启动交互式CLI
            from cli import main as cli_main
            import asyncio
            asyncio.run(cli_main())
        
        elif command == "example":
            # 运行示例
            from example_usage import main as example_main
            example_main()
        
        elif command == "visualize":
            # 可视化现有数据
            if len(sys.argv) > 2:
                stats_file = sys.argv[2]
                from visualizer import visualize_from_file
                visualize_from_file(stats_file)
            else:
                print("❌ 请提供统计文件路径")
                print("使用方法: python run.py visualize <stats_file.json>")
        
        elif command == "help" or command == "-h" or command == "--help":
            show_help()
        
        else:
            print(f"❌ 未知命令: {command}")
            show_help()
    
    else:
        # 默认显示菜单
        show_menu()

def show_menu():
    """显示主菜单"""
    print("\n📋 请选择操作:")
    print("1. 🎯 交互式CLI (推荐新手)")
    print("2. 📝 运行示例代码")
    print("3. 📊 可视化现有数据")
    print("4. ❓ 显示帮助")
    print("5. 🚪 退出")
    
    while True:
        try:
            choice = input("\n请输入选项 (1-5): ").strip()
            
            if choice == "1":
                from cli import main as cli_main
                import asyncio
                asyncio.run(cli_main())
                break
            
            elif choice == "2":
                from example_usage import main as example_main
                example_main()
                break
            
            elif choice == "3":
                stats_file = input("请输入统计文件路径: ").strip()
                if os.path.exists(stats_file):
                    from visualizer import visualize_from_file
                    visualize_from_file(stats_file)
                else:
                    print(f"❌ 文件不存在: {stats_file}")
                break
            
            elif choice == "4":
                show_help()
                break
            
            elif choice == "5":
                print("👋 再见!")
                break
            
            else:
                print("❌ 无效选项，请输入 1-5")
        
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            break

def show_help():
    """显示帮助信息"""
    print("\n📖 使用帮助")
    print("=" * 50)
    print("\n🎯 命令行用法:")
    print("  python run.py                    # 显示主菜单")
    print("  python run.py cli                # 启动交互式CLI")
    print("  python run.py example            # 运行示例代码")
    print("  python run.py visualize <file>   # 可视化统计文件")
    print("  python run.py help               # 显示此帮助")
    
    print("\n📁 项目文件说明:")
    print("  main.py          # 核心Gas费用追踪器")
    print("  cli.py           # 交互式命令行界面")
    print("  config.py        # 配置文件")
    print("  example_usage.py # 使用示例")
    print("  visualizer.py    # 数据可视化")
    print("  requirements.txt # 依赖包列表")
    print("  .env.example     # 环境变量模板")
    
    print("\n🔧 快速开始:")
    print("  1. 安装依赖: pip install -r requirements.txt")
    print("  2. 配置API: 复制 .env.example 为 .env 并填入API密钥")
    print("  3. 运行程序: python run.py cli")
    
    print("\n🌐 支持的区块链:")
    print("  • Ethereum (ETH)")
    print("  • Binance Smart Chain (BSC)")
    print("  • Polygon (MATIC)")
    print("  • Arbitrum (ARB)")
    print("  • Optimism (OP)")
    print("  • Avalanche (AVAX)")
    print("  • Fantom (FTM)")
    
    print("\n📊 输出功能:")
    print("  • JSON格式统计报告")
    print("  • Excel表格导出")
    print("  • 交互式图表")
    print("  • 综合仪表板")
    
    print("\n❓ 需要帮助?")
    print("  • 查看 README.md 获取详细文档")
    print("  • 运行 python run.py example 查看使用示例")
    print("  • 检查 .env.example 了解配置要求")

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = {
        'requests': 'requests',
        'pandas': 'pandas', 
        'python-dotenv': 'dotenv',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'plotly': 'plotly'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("⚠️  缺少以下依赖包:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        print("或者:")
        print("pip install -r requirements.txt")
        return False
    
    return True

if __name__ == "__main__":
    try:
        # 检查依赖
        if not check_dependencies():
            sys.exit(1)
        
        # 运行主程序
        main()
    
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()