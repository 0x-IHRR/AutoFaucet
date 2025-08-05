#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进功能演示脚本

展示.env文件加载和文件管理功能
"""

import asyncio
import os
from datetime import datetime, timedelta
from main import GasFeeTracker
from config import config
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import glob

console = Console()

async def demo_env_loading():
    """演示.env文件加载功能"""
    console.print("[bold blue]🔧 演示.env文件加载功能[/bold blue]\n")
    
    # 显示从.env文件加载的配置
    api_keys = config.api_config.get_api_keys()
    
    console.print("[green]✅ 成功从.env文件加载以下配置:[/green]")
    for chain, key in api_keys.items():
        if key and key != "YOUR_API_KEY_HERE" and len(key) > 10:
            masked_key = key[:8] + "..." + key[-4:]
            console.print(f"  • {chain}: {masked_key}")
        else:
            console.print(f"  • {chain}: [red]未配置[/red]")
    
    console.print("\n[cyan]💡 现在无需在脚本中硬编码API密钥了！[/cyan]")

async def demo_file_management():
    """演示文件管理功能"""
    console.print("\n[bold blue]📁 演示文件管理功能[/bold blue]\n")
    
    # 显示当前目录中的分析文件
    existing_files = glob.glob("gas_fee_analysis_*.json")
    console.print(f"[yellow]当前目录中有 {len(existing_files)} 个分析文件[/yellow]")
    
    if existing_files:
        console.print("现有文件:")
        for file in existing_files[-5:]:  # 只显示最新的5个
            file_path = Path(file)
            size = file_path.stat().st_size
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            console.print(f"  • {file} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # 演示分析功能（使用有效的API密钥）
    console.print("\n[cyan]🚀 运行一个快速分析来演示文件管理...[/cyan]")
    
    # 获取有效的API密钥
    api_keys = config.api_config.get_api_keys()
    valid_key = None
    for chain, key in api_keys.items():
        if key and key != "YOUR_API_KEY_HERE" and len(key) > 10:
            valid_key = key
            break
    
    if not valid_key:
        console.print("[red]❌ 没有有效的API密钥，跳过演示[/red]")
        return
    
    # 运行分析
    address = "0x01d9abcc0dB5A18df6b75b3a3745779cd2C674e3"
    
    async with GasFeeTracker() as tracker:
        # 设置较短的时间范围以快速完成
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # 最近7天
        
        console.print(f"分析地址: {address}")
        console.print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        
        try:
            stats = await tracker.analyze_gas_fees(
                addresses=[address],
                chains=['ethereum'],
                api_keys={'ethereum': valid_key},
                start_date=start_date,
                end_date=end_date
            )
            
            if stats:
                # 保存结果（会自动管理文件）
                filepath = tracker.save_results(stats)
                console.print(f"[green]✅ 分析完成，结果保存到: {filepath}[/green]")
                
                # 显示文件管理效果
                new_files = glob.glob("gas_fee_analysis_*.json")
                console.print(f"\n[yellow]现在目录中有 {len(new_files)} 个分析文件[/yellow]")
                
                if len(new_files) > len(existing_files):
                    console.print("[green]✅ 新文件已创建[/green]")
                
                if len(existing_files) > 10:
                    console.print("[blue]🧹 自动清理功能会保留最新的10个文件[/blue]")
                
            else:
                console.print("[red]❌ 分析失败[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ 分析过程中出错: {e}[/red]")

def show_improvements_summary():
    """显示改进总结"""
    summary_text = """
🎉 主要改进总结:

1. 📋 .env文件自动加载:
   • 无需在代码中硬编码API密钥
   • 支持所有主流区块链的API密钥配置
   • 自动从.env文件读取配置

2. 📁 智能文件管理:
   • 自动生成有意义的文件名（包含时间戳和地址标识）
   • 自动清理旧文件（默认保留最新10个）
   • 可配置的清理策略

3. 🔧 配置管理工具:
   • config_manager.py 用于检查配置状态
   • 验证API密钥是否正确配置
   • 提供配置指南

4. 💡 使用建议:
   • 重要分析结果可手动重命名保存
   • 定期备份重要数据
   • 考虑使用数据库存储长期数据
"""
    
    console.print(Panel(summary_text, title="改进功能总结", border_style="green"))

async def main():
    """主演示函数"""
    console.print("[bold magenta]🚀 Gas Fee Tracker 改进功能演示[/bold magenta]\n")
    
    # 演示.env文件加载
    await demo_env_loading()
    
    # 演示文件管理
    await demo_file_management()
    
    # 显示改进总结
    show_improvements_summary()
    
    console.print("\n[bold green]✨ 演示完成！现在您可以更方便地使用Gas Fee Tracker了[/bold green]")

if __name__ == "__main__":
    asyncio.run(main())