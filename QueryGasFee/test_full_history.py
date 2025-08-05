#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：查询钱包地址自创建以来的所有gas费用
"""

import asyncio
from datetime import datetime
from main import GasFeeTracker

async def test_full_history():
    """测试查询钱包地址的完整历史gas费用"""
    
    # 测试地址 - 使用之前测试成功的地址
    address = "0x01d9abcc0dB5A18df6b75b3a3745779cd2C674e3"
    
    # API密钥配置 - 使用之前测试成功的API密钥
    api_keys = {
        'ethereum': 'KYAMZXD18DNYV6X7GRDW79B3SWDTRX8AU3'
    }
    
    # 如果没有有效的API密钥，使用演示模式
    print("⚠️  注意: 当前使用的是演示地址和API密钥")
    print("请在实际使用时替换为真实的地址和API密钥")
    print("如果您有有效的API密钥，请修改test_full_history.py文件中的配置")
    print()
    
    print(f"开始查询地址 {address} 自创建以来的所有gas费用...")
    print("="*80)
    
    try:
        async with GasFeeTracker() as tracker:
            # 不设置时间范围，查询所有历史记录
            result = await tracker.analyze_gas_fees(
                addresses=[address],
                chains=['ethereum'],
                api_keys=api_keys,
                start_date=None,  # 不限制开始时间
                end_date=None     # 不限制结束时间
            )
            
            # 检查是否有统计数据
            if 'statistics' in result and 'summary' in result['statistics']:
                summary = result['statistics']['summary']
                
                print("\n📊 查询结果:")
                print(f"总交易数: {summary.get('total_transactions', 0)}")
                print(f"总Gas费用(ETH): {summary.get('total_gas_fee_eth', 0):.6f}")
                
                if summary.get('total_gas_fee_usd'):
                    print(f"总Gas费用(USD): ${summary.get('total_gas_fee_usd', 0):.2f}")
                
                print(f"平均Gas费用(ETH): {summary.get('avg_gas_fee_eth', 0):.6f}")
                
                if summary.get('avg_gas_fee_usd'):
                    print(f"平均Gas费用(USD): ${summary.get('avg_gas_fee_usd', 0):.2f}")
                
                date_range = summary.get('date_range', {})
                if date_range.get('start') and date_range.get('end'):
                    print(f"时间范围: {date_range['start']} 至 {date_range['end']}")
                
                # 显示详细统计
                tracker.print_summary(result['statistics'])
                
                # 保存结果
                filename = f"gas_fee_full_history_{address[-8:]}.json"
                tracker.save_results(result, filename)
                print(f"\n结果已保存到: {filename}")
                
            else:
                print("❌ 未找到交易数据或统计信息")
                if 'statistics' in result and 'error' in result['statistics']:
                    print(f"错误信息: {result['statistics']['error']}")
                    
    except Exception as e:
        print(f"❌ 查询过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Gas费用完整历史查询工具")
    print("注意: 请确保已配置正确的API密钥")
    print("="*80)
    
    asyncio.run(test_full_history())