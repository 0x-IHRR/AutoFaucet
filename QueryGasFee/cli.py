#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行交互界面
提供用户友好的交互式配置和查询功能
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from main import GasFeeTracker
from config import config

class GasFeeTrackerCLI:
    """Gas费用追踪器命令行界面"""
    
    def __init__(self):
        self.tracker = None
        self.addresses = []
        self.chains = []
        self.api_keys = {}
        self.start_date = None
        self.end_date = None
    
    def print_banner(self):
        """打印欢迎横幅"""
        print("\n" + "="*70)
        print("           🔥 Web3 钱包 Gas Fee 查询统计工具 🔥")
        print("="*70)
        print("支持多链、多钱包、自定义时间范围的gas费用统计分析")
        print("支持的区块链: Ethereum, BSC, Polygon, Arbitrum, Optimism, Avalanche")
        print("="*70)
    
    def print_menu(self):
        """打印主菜单"""
        print("\n📋 主菜单:")
        print("1. 配置钱包地址")
        print("2. 选择区块链网络")
        print("3. 配置API密钥")
        print("4. 设置查询时间范围")
        print("5. 开始分析")
        print("6. 查看当前配置")
        print("7. 帮助信息")
        print("0. 退出")
        print("-" * 50)
    
    def configure_addresses(self):
        """配置钱包地址"""
        print("\n📝 配置钱包地址")
        print("请输入要查询的钱包地址 (每行一个，输入空行结束):")
        
        addresses = []
        while True:
            address = input("地址: ").strip()
            if not address:
                break
            
            # 简单验证地址格式
            if not address.startswith('0x') or len(address) != 42:
                print("⚠️  警告: 地址格式可能不正确，请确认")
            
            addresses.append(address)
            print(f"✅ 已添加地址: {address}")
        
        if addresses:
            self.addresses = addresses
            print(f"\n✅ 已配置 {len(addresses)} 个钱包地址")
        else:
            print("❌ 未添加任何地址")
    
    def select_chains(self):
        """选择区块链网络"""
        print("\n🔗 选择区块链网络")
        supported_chains = config.get_supported_chains()
        display_names = config.get_chain_display_names()
        
        print("支持的区块链:")
        for i, chain in enumerate(supported_chains, 1):
            print(f"{i}. {display_names[chain]}")
        
        print("\n请选择要查询的区块链 (输入数字，用逗号分隔，如: 1,2,3):")
        selection = input("选择: ").strip()
        
        if not selection:
            print("❌ 未选择任何区块链")
            return
        
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_chains = []
            
            for idx in indices:
                if 0 <= idx < len(supported_chains):
                    chain = supported_chains[idx]
                    selected_chains.append(chain)
                    print(f"✅ 已选择: {display_names[chain]}")
                else:
                    print(f"⚠️  无效选择: {idx + 1}")
            
            if selected_chains:
                self.chains = selected_chains
                print(f"\n✅ 已选择 {len(selected_chains)} 条区块链")
            
        except ValueError:
            print("❌ 输入格式错误，请输入数字")
    
    def configure_api_keys(self):
        """配置API密钥"""
        print("\n🔑 配置API密钥")
        
        if not self.chains:
            print("❌ 请先选择区块链网络")
            return
        
        registration_links = config.get_api_registration_links()
        
        print("\n📖 API密钥获取指南:")
        for chain in self.chains:
            print(f"{chain}: {registration_links[chain]}")
        
        print("\n请输入各链的API密钥:")
        
        for chain in self.chains:
            current_key = self.api_keys.get(chain, '')
            if current_key:
                print(f"{chain} (当前: {current_key[:8]}...): ", end='')
            else:
                print(f"{chain}: ", end='')
            
            key = input().strip()
            if key:
                self.api_keys[chain] = key
                print(f"✅ 已设置 {chain} API密钥")
            elif not current_key:
                print(f"⚠️  跳过 {chain}")
        
        # 验证配置
        missing = []
        for chain in self.chains:
            if chain not in self.api_keys or not self.api_keys[chain]:
                missing.append(chain)
        
        if missing:
            print(f"\n⚠️  缺少以下链的API密钥: {', '.join(missing)}")
        else:
            print("\n✅ 所有API密钥配置完成")
    
    def configure_time_range(self):
        """配置时间范围"""
        print("\n📅 设置查询时间范围")
        print("1. 最近7天")
        print("2. 最近30天")
        print("3. 最近90天")
        print("4. 自定义时间范围")
        print("5. 全部时间 (不推荐，可能很慢)")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        now = datetime.now()
        
        if choice == '1':
            self.start_date = now - timedelta(days=7)
            self.end_date = now
            print("✅ 已设置为最近7天")
        elif choice == '2':
            self.start_date = now - timedelta(days=30)
            self.end_date = now
            print("✅ 已设置为最近30天")
        elif choice == '3':
            self.start_date = now - timedelta(days=90)
            self.end_date = now
            print("✅ 已设置为最近90天")
        elif choice == '4':
            print("\n请输入开始日期 (格式: YYYY-MM-DD):")
            start_str = input("开始日期: ").strip()
            print("请输入结束日期 (格式: YYYY-MM-DD):")
            end_str = input("结束日期: ").strip()
            
            try:
                self.start_date = datetime.strptime(start_str, '%Y-%m-%d')
                self.end_date = datetime.strptime(end_str, '%Y-%m-%d')
                
                if self.start_date >= self.end_date:
                    print("❌ 开始日期必须早于结束日期")
                    self.start_date = self.end_date = None
                else:
                    print(f"✅ 已设置时间范围: {start_str} 至 {end_str}")
            except ValueError:
                print("❌ 日期格式错误")
        elif choice == '5':
            self.start_date = None
            self.end_date = None
            print("✅ 已设置为全部时间")
        else:
            print("❌ 无效选择")
    
    def show_current_config(self):
        """显示当前配置"""
        print("\n📋 当前配置:")
        print("-" * 50)
        
        print(f"钱包地址 ({len(self.addresses)} 个):")
        for i, addr in enumerate(self.addresses, 1):
            print(f"  {i}. {addr}")
        
        print(f"\n区块链网络 ({len(self.chains)} 个):")
        display_names = config.get_chain_display_names()
        for chain in self.chains:
            status = "✅" if chain in self.api_keys and self.api_keys[chain] else "❌"
            print(f"  {status} {display_names[chain]}")
        
        print(f"\n时间范围:")
        if self.start_date and self.end_date:
            print(f"  从 {self.start_date.strftime('%Y-%m-%d')} 到 {self.end_date.strftime('%Y-%m-%d')}")
        elif self.start_date is None and self.end_date is None:
            print(f"  全部时间")
        else:
            print(f"  未设置")
        
        print("-" * 50)
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📖 帮助信息")
        print("-" * 50)
        print("\n🔧 使用步骤:")
        print("1. 首先配置要查询的钱包地址")
        print("2. 选择要查询的区块链网络")
        print("3. 为选择的区块链配置API密钥")
        print("4. 设置查询的时间范围 (可选)")
        print("5. 开始分析并查看结果")
        
        print("\n🔑 API密钥获取:")
        registration_links = config.get_api_registration_links()
        for chain, link in registration_links.items():
            print(f"{chain}: {link}")
        
        print("\n💡 提示:")
        print("- 大多数API服务提供免费套餐")
        print("- 建议从小时间范围开始测试")
        print("- 查询大量数据可能需要较长时间")
        print("- 结果会自动保存为JSON文件")
        print("-" * 50)
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        
        if not self.addresses:
            errors.append("未配置钱包地址")
        
        if not self.chains:
            errors.append("未选择区块链网络")
        
        missing_keys = []
        for chain in self.chains:
            if chain not in self.api_keys or not self.api_keys[chain]:
                missing_keys.append(chain)
        
        if missing_keys:
            errors.append(f"缺少API密钥: {', '.join(missing_keys)}")
        
        return errors
    
    async def start_analysis(self):
        """开始分析"""
        print("\n🚀 开始分析")
        
        # 验证配置
        errors = self.validate_config()
        if errors:
            print("❌ 配置错误:")
            for error in errors:
                print(f"  - {error}")
            return
        
        print("\n📊 分析配置:")
        print(f"  钱包地址: {len(self.addresses)} 个")
        print(f"  区块链: {', '.join(self.chains)}")
        if self.start_date and self.end_date:
            print(f"  时间范围: {self.start_date.strftime('%Y-%m-%d')} 至 {self.end_date.strftime('%Y-%m-%d')}")
        else:
            print(f"  时间范围: 全部时间")
        
        confirm = input("\n确认开始分析? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 已取消分析")
            return
        
        print("\n⏳ 正在分析，请稍候...")
        
        try:
            async with GasFeeTracker() as tracker:
                stats = await tracker.analyze_gas_fees(
                    addresses=self.addresses,
                    chains=self.chains,
                    api_keys=self.api_keys,
                    start_date=self.start_date,
                    end_date=self.end_date
                )
                
                if 'error' in stats:
                    print(f"\n❌ 分析失败: {stats['error']}")
                    return
                
                # 显示结果
                tracker.print_summary(stats)
                
                # 保存结果
                filename = tracker.save_results(stats)
                print(f"\n💾 详细结果已保存到: {filename}")
                
                # 询问是否查看详细数据
                view_details = input("\n是否查看详细统计数据? (y/N): ").strip().lower()
                if view_details == 'y':
                    self.show_detailed_stats(stats)
                
        except Exception as e:
            print(f"\n❌ 分析过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    def show_detailed_stats(self, stats: Dict):
        """显示详细统计数据"""
        print("\n" + "="*60)
        print("           详细统计数据")
        print("="*60)
        
        # 按日期统计
        if stats.get('by_date'):
            print("\n📅 按日期统计 (最近10天):")
            dates = sorted(stats['by_date'].keys(), reverse=True)[:10]
            for date in dates:
                data = stats['by_date'][date]
                print(f"  {date}:")
                print(f"    交易数: {data['transaction_count']}")
                print(f"    总费用: {data['total_gas_fee_eth']:.6f} ETH")
                if 'total_gas_fee_usd' in data:
                    print(f"    总费用: ${data['total_gas_fee_usd']:.2f} USD")
                print(f"    平均Gas价格: {data['avg_gas_price_gwei']:.2f} Gwei")
                print()
        
        # 按地址统计
        if stats.get('by_address'):
            print("\n👤 按地址统计:")
            for address, data in stats['by_address'].items():
                print(f"  {address[:10]}...{address[-8:]}:")
                print(f"    交易数: {data['transaction_count']}")
                print(f"    总费用: {data['total_gas_fee_eth']:.6f} ETH")
                if data['total_gas_fee_usd']:
                    print(f"    总费用: ${data['total_gas_fee_usd']:.2f} USD")
                print(f"    使用的链: {', '.join(data['chains_used'])}")
                print()
    
    async def run(self):
        """运行CLI"""
        self.print_banner()
        
        while True:
            self.print_menu()
            choice = input("请选择操作 (0-7): ").strip()
            
            if choice == '0':
                print("\n👋 感谢使用 Gas Fee 查询工具!")
                break
            elif choice == '1':
                self.configure_addresses()
            elif choice == '2':
                self.select_chains()
            elif choice == '3':
                self.configure_api_keys()
            elif choice == '4':
                self.configure_time_range()
            elif choice == '5':
                await self.start_analysis()
            elif choice == '6':
                self.show_current_config()
            elif choice == '7':
                self.show_help()
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")

async def main():
    """主函数"""
    cli = GasFeeTrackerCLI()
    await cli.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()