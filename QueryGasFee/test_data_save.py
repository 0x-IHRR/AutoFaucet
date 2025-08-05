#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Data_Save目录功能
验证分析结果文件是否正确保存到Data_Save文件夹中
"""

import asyncio
from pathlib import Path
from main import GasFeeTracker
from config import Config

async def test_data_save_directory():
    """测试Data_Save目录功能"""
    print("🧪 测试Data_Save目录功能...")
    
    # 检查Data_Save目录
    data_save_dir = Path("Data_Save")
    print(f"📁 Data_Save目录路径: {data_save_dir.absolute()}")
    
    if data_save_dir.exists():
        print("✅ Data_Save目录已存在")
        files = list(data_save_dir.glob("*.json"))
        print(f"📄 当前文件数量: {len(files)}")
        for file in files[-3:]:  # 显示最新的3个文件
            print(f"   - {file.name}")
    else:
        print("❌ Data_Save目录不存在")
    
    # 创建一个简单的测试分析
    tracker = GasFeeTracker()
    
    # 创建测试数据
    test_stats = {
        'summary': {
            'addresses': ['0x1234567890abcdef1234567890abcdef12345678'],
            'total_transactions': 5,
            'total_gas_fee_eth': 0.001,
            'total_gas_fee_usd': 3.58,
            'avg_gas_fee_eth': 0.0002,
            'avg_gas_fee_usd': 0.72
        },
        'test_data': True,
        'timestamp': '2025-08-06 00:30:00'
    }
    
    print("\n💾 保存测试数据...")
    tracker.save_results(test_stats, auto_cleanup=False)  # 不清理，方便查看
    
    # 再次检查目录
    print("\n📁 保存后的Data_Save目录状态:")
    if data_save_dir.exists():
        files = list(data_save_dir.glob("*.json"))
        print(f"📄 文件数量: {len(files)}")
        if files:
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            print(f"🆕 最新文件: {latest_file.name}")
            print(f"📏 文件大小: {latest_file.stat().st_size} bytes")
    
    print("\n✨ 测试完成！")
    print("💡 提示: 所有分析结果现在都会保存到Data_Save文件夹中")

if __name__ == "__main__":
    asyncio.run(test_data_save_directory())