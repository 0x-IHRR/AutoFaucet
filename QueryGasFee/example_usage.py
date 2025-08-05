#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例
演示如何使用Gas Fee追踪器的各种功能
"""

import asyncio
from datetime import datetime, timedelta
from main import GasFeeTracker
from config import config

# 示例配置
EXAMPLE_CONFIG = {
    # 示例钱包地址 (请替换为真实地址)
    'addresses': [
        "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",  # 示例地址1
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # 示例地址2 (Vitalik)
    ],
    
    # 要查询的区块链
    'chains': ['ethereum', 'polygon', 'bsc'],
    
    # API密钥 (需要用户提供真实密钥)
    'api_keys': {
        'ethereum': 'YOUR_ETHERSCAN_API_KEY',
        'polygon': 'YOUR_POLYGONSCAN_API_KEY', 
        'bsc': 'YOUR_BSCSCAN_API_KEY',
    }
}

async def example_basic_usage():
    """基础使用示例"""
    print("\n=== 基础使用示例 ===")
    
    # 检查API密钥配置
    missing_keys = []
    for chain, key in EXAMPLE_CONFIG['api_keys'].items():
        if not key or key.startswith('YOUR_'):
            missing_keys.append(chain)
    
    if missing_keys:
        print(f"❌ 请先配置以下链的API密钥: {', '.join(missing_keys)}")
        print("\n📖 API密钥获取链接:")
        registration_links = config.get_api_registration_links()
        for chain in missing_keys:
            print(f"{chain}: {registration_links[chain]}")
        return
    
    # 设置查询时间范围 (最近7天)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    async with GasFeeTracker() as tracker:
        print("🔍 开始查询gas费用数据...")
        
        stats = await tracker.analyze_gas_fees(
            addresses=EXAMPLE_CONFIG['addresses'],
            chains=EXAMPLE_CONFIG['chains'],
            api_keys=EXAMPLE_CONFIG['api_keys'],
            start_date=start_date,
            end_date=end_date
        )
        
        # 显示结果
        tracker.print_summary(stats)
        
        # 保存结果
        filename = tracker.save_results(stats, 'example_analysis.json')
        print(f"\n💾 结果已保存到: {filename}")

async def example_single_chain():
    """单链查询示例"""
    print("\n=== 单链查询示例 (仅Ethereum) ===")
    
    # 检查Ethereum API密钥
    eth_key = EXAMPLE_CONFIG['api_keys'].get('ethereum', '')
    if not eth_key or eth_key.startswith('YOUR_'):
        print("❌ 请先配置Ethereum API密钥")
        print("获取地址: https://etherscan.io/apis")
        return
    
    async with GasFeeTracker() as tracker:
        stats = await tracker.analyze_gas_fees(
            addresses=["0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"],  # Vitalik的地址
            chains=['ethereum'],
            api_keys={'ethereum': eth_key},
            start_date=datetime.now() - timedelta(days=30)  # 最近30天
        )
        
        tracker.print_summary(stats)

async def example_custom_analysis():
    """自定义分析示例"""
    print("\n=== 自定义分析示例 ===")
    
    async with GasFeeTracker() as tracker:
        # 获取单个地址的交易数据
        address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        chain = 'ethereum'
        api_key = EXAMPLE_CONFIG['api_keys'].get(chain, '')
        
        if not api_key or api_key.startswith('YOUR_'):
            print(f"❌ 请先配置{chain} API密钥")
            return
        
        print(f"🔍 获取地址 {address} 在 {chain} 上的交易...")
        
        transactions = await tracker.get_transactions_by_address(
            address=address,
            chain_name=chain,
            api_key=api_key,
            offset=100  # 只获取最近100笔交易
        )
        
        if transactions:
            print(f"✅ 获取到 {len(transactions)} 笔交易")
            
            # 分析最近的几笔交易
            recent_txs = transactions[:5]
            print("\n📊 最近5笔交易的gas费用:")
            
            for i, tx in enumerate(recent_txs, 1):
                gas_used = int(tx.get('gasUsed', 0))
                gas_price = int(tx.get('gasPrice', 0))
                gas_fee_eth = (gas_used * gas_price) / (10 ** 18)
                
                print(f"{i}. Hash: {tx['hash'][:10]}...")
                print(f"   Gas Used: {gas_used:,}")
                print(f"   Gas Price: {gas_price / 10**9:.2f} Gwei")
                print(f"   Gas Fee: {gas_fee_eth:.6f} ETH")
                print()
        else:
            print("❌ 未获取到交易数据")

def example_config_setup():
    """配置设置示例"""
    print("\n=== 配置设置示例 ===")
    
    print("📋 支持的区块链:")
    chains = config.get_supported_chains()
    display_names = config.get_chain_display_names()
    
    for chain in chains:
        print(f"  - {display_names[chain]}")
    
    print("\n🔑 API密钥获取链接:")
    registration_links = config.get_api_registration_links()
    for chain, link in registration_links.items():
        print(f"  {chain}: {link}")
    
    print("\n📖 API文档链接:")
    doc_links = config.get_api_documentation()
    for chain, link in doc_links.items():
        print(f"  {chain}: {link}")

async def example_price_check():
    """价格查询示例"""
    print("\n=== 代币价格查询示例 ===")
    
    async with GasFeeTracker() as tracker:
        tokens = ['ETH', 'BNB', 'MATIC', 'AVAX']
        
        print("💰 当前代币价格:")
        for token in tokens:
            price = await tracker.get_token_price(token)
            if price:
                print(f"  {token}: ${price:.2f}")
            else:
                print(f"  {token}: 获取失败")

def print_usage_guide():
    """打印使用指南"""
    print("\n" + "="*70)
    print("           🔥 Gas Fee 追踪器使用指南 🔥")
    print("="*70)
    
    print("\n🚀 快速开始:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 获取API密钥 (见下方链接)")
    print("3. 运行交互式界面: python cli.py")
    print("4. 或者修改本文件中的配置后运行示例")
    
    print("\n📁 文件说明:")
    print("  main.py     - 核心功能模块")
    print("  cli.py      - 交互式命令行界面")
    print("  config.py   - 配置管理")
    print("  example_usage.py - 使用示例 (本文件)")
    
    print("\n🔧 功能特性:")
    print("  ✅ 支持多个钱包地址同时查询")
    print("  ✅ 支持6条主流区块链")
    print("  ✅ 自定义时间范围查询")
    print("  ✅ 多维度统计分析")
    print("  ✅ 自动获取实时代币价格")
    print("  ✅ 结果导出为JSON格式")
    print("  ✅ 友好的命令行界面")
    
    print("\n💡 使用建议:")
    print("  - 首次使用建议从小时间范围开始")
    print("  - 大量数据查询可能需要较长时间")
    print("  - 注意API调用频率限制")
    print("  - 定期备份重要的分析结果")

async def main():
    """主函数"""
    print_usage_guide()
    
    print("\n" + "="*50)
    print("           运行示例")
    print("="*50)
    
    # 配置示例
    example_config_setup()
    
    # 价格查询示例
    await example_price_check()
    
    # 询问是否运行数据查询示例
    print("\n" + "-"*50)
    run_examples = input("是否运行数据查询示例? (需要配置API密钥) (y/N): ").strip().lower()
    
    if run_examples == 'y':
        # 基础使用示例
        await example_basic_usage()
        
        # 单链查询示例
        await example_single_chain()
        
        # 自定义分析示例
        await example_custom_analysis()
    else:
        print("\n💡 提示: 配置API密钥后可以运行完整示例")
        print("建议使用交互式界面: python cli.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 示例程序已退出")
    except Exception as e:
        print(f"\n❌ 示例运行错误: {e}")
        import traceback
        traceback.print_exc()