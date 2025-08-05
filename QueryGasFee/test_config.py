#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置测试脚本
用于验证API密钥和配置是否正确
"""

import sys
import asyncio
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from main import GasFeeTracker

async def test_api_connections():
    """测试API连接"""
    print("🔧 开始测试API连接...")
    print("=" * 50)
    
    config = Config()
    tracker = GasFeeTracker(config)
    
    # 测试地址 (Vitalik的地址)
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    # 测试各个链的API
    test_chains = ['ethereum', 'bsc', 'polygon']
    
    results = {}
    
    for chain in test_chains:
        print(f"\n🔗 测试 {chain.upper()} API...")
        
        try:
            # 获取最近的几笔交易进行测试
            transactions = await tracker.get_transactions(
                address=test_address,
                chain=chain,
                start_block=None,
                end_block=None
            )
            
            if transactions:
                print(f"✅ {chain.upper()} API 连接成功")
                print(f"   📊 获取到 {len(transactions)} 笔交易")
                if transactions:
                    latest_tx = transactions[0]
                    print(f"   🔍 最新交易: {latest_tx.get('hash', 'N/A')[:10]}...")
                results[chain] = {'status': 'success', 'count': len(transactions)}
            else:
                print(f"⚠️  {chain.upper()} API 连接成功但无交易数据")
                results[chain] = {'status': 'no_data', 'count': 0}
        
        except Exception as e:
            print(f"❌ {chain.upper()} API 连接失败: {str(e)[:100]}...")
            results[chain] = {'status': 'error', 'error': str(e)}
    
    # 测试代币价格API
    print(f"\n💰 测试代币价格API...")
    try:
        eth_price = await tracker.get_token_price('ethereum')
        if eth_price > 0:
            print(f"✅ 代币价格API连接成功")
            print(f"   💎 ETH当前价格: ${eth_price:.2f}")
            results['price_api'] = {'status': 'success', 'eth_price': eth_price}
        else:
            print(f"⚠️  代币价格API连接成功但价格为0")
            results['price_api'] = {'status': 'no_data'}
    except Exception as e:
        print(f"❌ 代币价格API连接失败: {str(e)[:100]}...")
        results['price_api'] = {'status': 'error', 'error': str(e)}
    
    return results

def test_config_loading():
    """测试配置加载"""
    print("⚙️  测试配置加载...")
    print("=" * 50)
    
    try:
        config = Config()
        
        print("✅ 配置加载成功")
        print(f"   📁 配置文件: .env")
        
        # 检查API密钥
        api_keys = {
            'Etherscan': config.api_config.etherscan_api_key,
            'BSCScan': config.api_config.bscscan_api_key,
            'PolygonScan': config.api_config.polygonscan_api_key,
            'Arbiscan': config.api_config.arbiscan_api_key,
            'Optimism': config.api_config.optimism_api_key,
            'Snowtrace': config.api_config.snowtrace_api_key
        }
        
        print("\n🔑 API密钥状态:")
        configured_count = 0
        for name, key in api_keys.items():
            if key and key != 'your_api_key_here':
                print(f"   ✅ {name}: 已配置")
                configured_count += 1
            else:
                print(f"   ❌ {name}: 未配置")
        
        print(f"\n📊 已配置 {configured_count}/{len(api_keys)} 个API密钥")
        
        if configured_count == 0:
            print("\n⚠️  警告: 没有配置任何API密钥!")
            print("   请复制 .env.example 为 .env 并填入API密钥")
            return False
        elif configured_count < len(api_keys):
            print("\n💡 提示: 配置更多API密钥可以支持更多区块链")
        
        # 显示其他配置
        print("\n🔧 其他配置:")
        print(f"   📅 默认查询天数: {config.default_days}")
        print(f"   🚀 请求间隔: {config.request_delay}秒")
        print(f"   📊 每次最大交易数: {config.max_transactions_per_request}")
        print(f"   📝 日志级别: {config.log_level}")
        
        return True
    
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_setup_guide():
    """显示设置指南"""
    print("\n📖 设置指南")
    print("=" * 50)
    
    print("\n1️⃣ 安装依赖:")
    print("   pip install -r requirements.txt")
    
    print("\n2️⃣ 配置API密钥:")
    print("   • 复制 .env.example 为 .env")
    print("   • 编辑 .env 文件，填入API密钥")
    
    print("\n3️⃣ 获取API密钥:")
    print("   • Etherscan: https://etherscan.io/apis")
    print("   • BSCScan: https://bscscan.com/apis")
    print("   • PolygonScan: https://polygonscan.com/apis")
    print("   • Arbiscan: https://arbiscan.io/apis")
    print("   • Optimism: https://optimistic.etherscan.io/apis")
    print("   • Snowtrace: https://snowtrace.io/apis")
    print("   • FTMScan: https://ftmscan.com/apis")
    
    print("\n4️⃣ 运行程序:")
    print("   python run.py cli")
    
    print("\n💡 提示:")
    print("   • 大多数API提供免费套餐")
    print("   • 至少需要配置一个API密钥")
    print("   • 建议配置Etherscan API密钥(使用最频繁)")

async def main():
    """主函数"""
    print("🧪 Gas Fee 配置测试工具")
    print("=" * 50)
    
    # 测试配置加载
    config_ok = test_config_loading()
    
    if not config_ok:
        show_setup_guide()
        return
    
    # 询问是否测试API连接
    print("\n❓ 是否测试API连接? (这将发送实际的API请求)")
    choice = input("输入 y/yes 继续，其他键跳过: ").strip().lower()
    
    if choice in ['y', 'yes']:
        results = await test_api_connections()
        
        # 显示测试总结
        print("\n📋 测试总结")
        print("=" * 50)
        
        success_count = 0
        total_count = 0
        
        for service, result in results.items():
            total_count += 1
            if result['status'] == 'success':
                success_count += 1
                print(f"✅ {service.upper()}: 正常")
            elif result['status'] == 'no_data':
                print(f"⚠️  {service.upper()}: 连接正常但无数据")
            else:
                print(f"❌ {service.upper()}: 失败")
        
        print(f"\n📊 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        if success_count > 0:
            print("\n🎉 恭喜! 配置测试通过，可以开始使用了!")
            print("   运行 'python run.py cli' 开始查询")
        else:
            print("\n😞 所有API测试都失败了")
            print("   请检查网络连接和API密钥配置")
            show_setup_guide()
    
    else:
        print("\n✅ 配置检查完成")
        print("   如需测试API连接，请重新运行此脚本")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()