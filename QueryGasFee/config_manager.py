#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具

提供配置检查、验证和管理功能
"""

import os
from pathlib import Path
from config import config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def check_env_file():
    """检查.env文件是否存在和配置"""
    env_file = Path('.env')
    
    if not env_file.exists():
        console.print("[red]❌ .env文件不存在[/red]")
        console.print("请复制.env.example为.env并配置API密钥")
        return False
    
    console.print("[green]✅ .env文件存在[/green]")
    return True

def check_api_keys():
    """检查API密钥配置"""
    console.print("\n[bold]API密钥配置检查:[/bold]")
    
    api_keys = config.api_config.get_api_keys()
    
    table = Table(title="API密钥状态")
    table.add_column("链名称", style="cyan")
    table.add_column("API密钥", style="magenta")
    table.add_column("状态", style="green")
    
    for chain, key in api_keys.items():
        if key and key != "YOUR_API_KEY_HERE" and len(key) > 10:
            status = "✅ 已配置"
            masked_key = key[:8] + "..." + key[-4:]
        else:
            status = "❌ 未配置"
            masked_key = "未设置"
        
        table.add_row(chain, masked_key, status)
    
    console.print(table)
    
    # 检查是否有有效的API密钥
    valid_keys = [k for k in api_keys.values() if k and k != "YOUR_API_KEY_HERE" and len(k) > 10]
    
    if valid_keys:
        console.print(f"\n[green]✅ 发现 {len(valid_keys)} 个有效的API密钥[/green]")
        return True
    else:
        console.print("\n[red]❌ 没有发现有效的API密钥[/red]")
        return False

def show_config_guide():
    """显示配置指南"""
    guide_text = """
🔧 配置指南:

1. 确保.env文件存在:
   - 如果没有.env文件，请复制.env.example为.env
   
2. 获取API密钥:
   - Ethereum: https://etherscan.io/apis
   - BSC: https://bscscan.com/apis
   - Polygon: https://polygonscan.com/apis
   
3. 编辑.env文件:
   - 将获取的API密钥填入对应字段
   - 保存文件
   
4. 重新运行此脚本验证配置
"""
    
    console.print(Panel(guide_text, title="配置指南", border_style="blue"))

def show_file_management_info():
    """显示文件管理信息"""
    info_text = """
📁 文件管理改进:

✅ 已实现的改进:
• 自动文件命名: 包含时间戳和地址标识
• 自动清理: 保留最新10个分析文件
• 智能命名: 文件名包含地址后8位便于识别

🔧 文件管理选项:
• 可通过 auto_cleanup=False 禁用自动清理
• 可通过 max_files 参数调整保留文件数量
• 文件按修改时间排序，自动删除最旧的文件

💡 建议:
• 对于重要分析结果，可手动重命名保存
• 定期备份重要的分析数据
• 考虑使用数据库存储长期数据
"""
    
    console.print(Panel(info_text, title="文件管理说明", border_style="green"))

def main():
    """主函数"""
    console.print("[bold blue]🔧 Gas Fee Tracker 配置管理工具[/bold blue]\n")
    
    # 检查.env文件
    env_exists = check_env_file()
    
    if env_exists:
        # 检查API密钥
        keys_valid = check_api_keys()
        
        if keys_valid:
            console.print("\n[green]🎉 配置检查完成，所有配置正常！[/green]")
            console.print("现在可以正常使用Gas Fee Tracker了")
        else:
            console.print("\n[yellow]⚠️  需要配置API密钥[/yellow]")
            show_config_guide()
    else:
        show_config_guide()
    
    # 显示文件管理信息
    show_file_management_info()

if __name__ == "__main__":
    main()