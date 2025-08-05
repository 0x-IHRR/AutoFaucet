#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试代理功能的自动化脚本
"""

import asyncio
import sys
from main import GasFeeTracker

async def test_proxy_functionality():
    """测试代理功能"""
    print("🚀 开始测试代理功能...")
    
    # 测试钱包地址和API密钥
    test_address = "0x01d9abcc0dB5A18df6b75b3a3745779cd2C674e3"
    api_key = "KYAMZXD18DNYV6X7GRDW79B3SWDTRX8AU3"
    
    try:
        async with GasFeeTracker() as tracker:
            print("✅ GasFeeTracker 初始化成功")
            
            # 测试获取ETH价格
            print("\n📊 测试获取ETH价格...")
            eth_price = await tracker.get_token_price('ETH')
            if eth_price:
                print(f"✅ ETH价格获取成功: ${eth_price}")
            else:
                print("❌ ETH价格获取失败")
            
            # 测试获取交易数据
            print("\n📋 测试获取交易数据...")
            transactions = await tracker.get_transactions_by_address(
                address=test_address,
                chain_name="ethereum",
                api_key=api_key,
                offset=10  # 只获取10条交易进行测试
            )
            
            if transactions:
                print(f"✅ 交易数据获取成功，共 {len(transactions)} 条交易")
                # 显示第一条交易的基本信息
                if len(transactions) > 0:
                    tx = transactions[0]
                    print(f"   - 交易哈希: {tx.get('hash', 'N/A')[:20]}...")
                    print(f"   - 区块号: {tx.get('blockNumber', 'N/A')}")
                    print(f"   - Gas Used: {tx.get('gasUsed', 'N/A')}")
            else:
                print("❌ 交易数据获取失败")
            
            # 测试完整分析功能
            print("\n🔍 测试完整分析功能...")
            from datetime import datetime, timedelta
            
            # 设置时间范围为最近30天
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            result = await tracker.analyze_gas_fees(
                addresses=[test_address],
                chains=["ethereum"],
                api_keys={"ethereum": api_key},
                start_date=start_date,
                end_date=end_date
            )
            
            if result and result.get('transactions'):
                print("✅ 完整分析成功")
                stats = result.get('statistics', {})
                summary = stats.get('summary', {})
                if summary:
                    print(f"   - 总交易数: {summary.get('total_transactions', 0)}")
                    print(f"   - 总Gas费用(ETH): {summary.get('total_gas_fee_eth', 0):.6f}")
                    if summary.get('total_gas_fee_usd'):
                        print(f"   - 总Gas费用(USD): ${summary.get('total_gas_fee_usd', 0):.2f}")
                else:
                    print(f"   - 过滤后交易数: {len(result.get('transactions', []))}")
            else:
                print("❌ 完整分析失败")
                
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 测试完成")

if __name__ == "__main__":
    asyncio.run(test_proxy_functionality())