#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3钱包链上Gas Fee查询统计工具
支持多链、多钱包、自定义时间范围的gas费用统计分析

作者: AI Assistant
创建时间: 2025-01-03
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import aiohttp
import pandas as pd
from dataclasses import dataclass
from decimal import Decimal
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gas_fee_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ChainConfig:
    """区块链配置"""
    name: str
    chain_id: int
    api_base_url: str
    api_key_param: str
    native_token: str
    decimals: int = 18
    block_time: int = 12  # 平均出块时间(秒)

@dataclass
class TransactionData:
    """交易数据结构"""
    hash: str
    block_number: int
    timestamp: int
    from_address: str
    to_address: str
    gas_used: int
    gas_price: int
    gas_fee_wei: int
    gas_fee_eth: float
    gas_fee_usd: Optional[float]
    chain_name: str
    transaction_type: str

class GasFeeTracker:
    """Gas费用追踪器主类"""
    
    def __init__(self):
        self.chains = self._init_chains()
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits = {}  # 速率限制跟踪
        
    def _init_chains(self) -> Dict[str, ChainConfig]:
        """初始化支持的区块链配置"""
        return {
            'ethereum': ChainConfig(
                name='Ethereum',
                chain_id=1,
                api_base_url='https://api.etherscan.io/api',
                api_key_param='apikey',
                native_token='ETH'
            ),
            'bsc': ChainConfig(
                name='BSC',
                chain_id=56,
                api_base_url='https://api.bscscan.com/api',
                api_key_param='apikey',
                native_token='BNB'
            ),
            'polygon': ChainConfig(
                name='Polygon',
                chain_id=137,
                api_base_url='https://api.polygonscan.com/api',
                api_key_param='apikey',
                native_token='MATIC'
            ),
            'arbitrum': ChainConfig(
                name='Arbitrum',
                chain_id=42161,
                api_base_url='https://api.arbiscan.io/api',
                api_key_param='apikey',
                native_token='ETH'
            ),
            'optimism': ChainConfig(
                name='Optimism',
                chain_id=10,
                api_base_url='https://api-optimistic.etherscan.io/api',
                api_key_param='apikey',
                native_token='ETH'
            ),
            'avalanche': ChainConfig(
                name='Avalanche',
                chain_id=43114,
                api_base_url='https://api.snowtrace.io/api',
                api_key_param='apikey',
                native_token='AVAX'
            )
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit_wait(self, chain_name: str):
        """处理API速率限制"""
        current_time = time.time()
        if chain_name in self.rate_limits:
            time_diff = current_time - self.rate_limits[chain_name]
            if time_diff < 0.2:  # 每秒最多5次请求
                await asyncio.sleep(0.2 - time_diff)
        self.rate_limits[chain_name] = current_time
    
    async def _make_api_request(self, url: str, params: Dict) -> Optional[Dict]:
        """发起API请求"""
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == '1':
                        return data.get('result')
                    else:
                        logger.warning(f"API返回错误: {data.get('message')}")
                        return None
                else:
                    logger.error(f"HTTP错误: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
            logger.error(f"请求URL: {url}")
            logger.error(f"请求参数: {params}")
            return None
    
    async def get_transactions_by_address(self, 
                                        address: str, 
                                        chain_name: str, 
                                        api_key: str,
                                        start_block: int = 0,
                                        end_block: int = 99999999,
                                        page: int = 1,
                                        offset: int = 1000) -> List[Dict]:
        """获取地址的交易记录"""
        if chain_name not in self.chains:
            logger.error(f"不支持的链: {chain_name}")
            return []
        
        chain = self.chains[chain_name]
        await self._rate_limit_wait(chain_name)
        
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc',
            chain.api_key_param: api_key
        }
        
        result = await self._make_api_request(chain.api_base_url, params)
        return result if result else []
    
    async def get_internal_transactions(self, 
                                      address: str, 
                                      chain_name: str, 
                                      api_key: str,
                                      start_block: int = 0,
                                      end_block: int = 99999999) -> List[Dict]:
        """获取内部交易记录"""
        if chain_name not in self.chains:
            return []
        
        chain = self.chains[chain_name]
        await self._rate_limit_wait(chain_name)
        
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': 'desc',
            chain.api_key_param: api_key
        }
        
        result = await self._make_api_request(chain.api_base_url, params)
        return result if result else []
    
    async def get_token_price(self, token_symbol: str) -> Optional[float]:
        """获取代币价格(USD)"""
        try:
            # 使用CoinGecko免费API获取价格
            url = f"https://api.coingecko.com/api/v3/simple/price"
            token_map = {
                'ETH': 'ethereum',
                'BNB': 'binancecoin', 
                'MATIC': 'matic-network',
                'AVAX': 'avalanche-2'
            }
            
            if token_symbol not in token_map:
                return None
                
            params = {
                'ids': token_map[token_symbol],
                'vs_currencies': 'usd'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get(token_map[token_symbol], {}).get('usd')
        except Exception as e:
            logger.error(f"获取价格失败: {str(e)}")
            logger.error(f"请求URL: {url}")
            logger.error(f"代币符号: {token_symbol}")
        return None
    
    def _parse_transaction(self, tx: Dict, chain_name: str, token_price: Optional[float] = None) -> TransactionData:
        """解析交易数据"""
        gas_used = int(tx.get('gasUsed', 0))
        gas_price = int(tx.get('gasPrice', 0))
        gas_fee_wei = gas_used * gas_price
        gas_fee_eth = gas_fee_wei / (10 ** 18)
        gas_fee_usd = gas_fee_eth * token_price if token_price else None
        
        # 判断交易类型
        tx_type = "普通转账"
        if tx.get('input', '0x') != '0x':
            tx_type = "合约交互"
        if int(tx.get('value', 0)) == 0 and tx.get('input', '0x') != '0x':
            tx_type = "合约调用"
        
        return TransactionData(
            hash=tx.get('hash', ''),
            block_number=int(tx.get('blockNumber', 0)),
            timestamp=int(tx.get('timeStamp', 0)),
            from_address=tx.get('from', ''),
            to_address=tx.get('to', ''),
            gas_used=gas_used,
            gas_price=gas_price,
            gas_fee_wei=gas_fee_wei,
            gas_fee_eth=gas_fee_eth,
            gas_fee_usd=gas_fee_usd,
            chain_name=chain_name,
            transaction_type=tx_type
        )
    
    def _filter_by_time_range(self, transactions: List[TransactionData], 
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> List[TransactionData]:
        """按时间范围过滤交易"""
        if not start_date and not end_date:
            return transactions
        
        filtered = []
        for tx in transactions:
            tx_date = datetime.fromtimestamp(tx.timestamp)
            
            if start_date and tx_date < start_date:
                continue
            if end_date and tx_date > end_date:
                continue
                
            filtered.append(tx)
        
        return filtered
    
    async def analyze_gas_fees(self, 
                             addresses: List[str],
                             chains: List[str],
                             api_keys: Dict[str, str],
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict:
        """分析gas费用消耗"""
        logger.info(f"开始分析 {len(addresses)} 个地址在 {len(chains)} 条链上的gas费用")
        
        all_transactions = []
        
        # 获取所有交易数据
        for chain_name in chains:
            if chain_name not in self.chains:
                logger.warning(f"跳过不支持的链: {chain_name}")
                continue
                
            if chain_name not in api_keys:
                logger.warning(f"缺少 {chain_name} 的API密钥")
                continue
            
            chain = self.chains[chain_name]
            token_price = await self.get_token_price(chain.native_token)
            logger.info(f"{chain.native_token} 当前价格: ${token_price}")
            
            for address in addresses:
                logger.info(f"获取地址 {address} 在 {chain_name} 上的交易")
                
                # 获取普通交易
                normal_txs = await self.get_transactions_by_address(
                    address, chain_name, api_keys[chain_name]
                )
                
                # 获取内部交易
                internal_txs = await self.get_internal_transactions(
                    address, chain_name, api_keys[chain_name]
                )
                
                # 解析交易数据
                for tx in normal_txs + internal_txs:
                    if tx.get('from', '').lower() == address.lower():  # 只统计发出的交易
                        parsed_tx = self._parse_transaction(tx, chain_name, token_price)
                        all_transactions.append(parsed_tx)
                
                # 避免API限制
                await asyncio.sleep(0.1)
        
        # 按时间范围过滤
        filtered_transactions = self._filter_by_time_range(all_transactions, start_date, end_date)
        
        # 生成统计报告
        return self._generate_statistics(filtered_transactions)
    
    def _generate_statistics(self, transactions: List[TransactionData]) -> Dict:
        """生成统计报告"""
        if not transactions:
            return {"error": "没有找到交易数据"}
        
        # 转换为DataFrame便于分析
        df_data = []
        for tx in transactions:
            df_data.append({
                'hash': tx.hash,
                'chain': tx.chain_name,
                'timestamp': tx.timestamp,
                'date': datetime.fromtimestamp(tx.timestamp).strftime('%Y-%m-%d'),
                'gas_used': tx.gas_used,
                'gas_price_gwei': tx.gas_price / 10**9,
                'gas_fee_eth': tx.gas_fee_eth,
                'gas_fee_usd': tx.gas_fee_usd,
                'tx_type': tx.transaction_type,
                'from_address': tx.from_address
            })
        
        df = pd.DataFrame(df_data)
        
        # 基础统计
        stats = {
            'summary': {
                'total_transactions': len(transactions),
                'total_gas_fee_eth': df['gas_fee_eth'].sum(),
                'total_gas_fee_usd': df['gas_fee_usd'].sum() if df['gas_fee_usd'].notna().any() else None,
                'avg_gas_fee_eth': df['gas_fee_eth'].mean(),
                'avg_gas_fee_usd': df['gas_fee_usd'].mean() if df['gas_fee_usd'].notna().any() else None,
                'date_range': {
                    'start': df['date'].min(),
                    'end': df['date'].max()
                }
            },
            
            # 按链统计
            'by_chain': {},
            
            # 按交易类型统计
            'by_transaction_type': {},
            
            # 按日期统计
            'by_date': {},
            
            # 按地址统计
            'by_address': {},
            
            # Gas价格分析
            'gas_price_analysis': {
                'min_gwei': df['gas_price_gwei'].min(),
                'max_gwei': df['gas_price_gwei'].max(),
                'avg_gwei': df['gas_price_gwei'].mean(),
                'median_gwei': df['gas_price_gwei'].median()
            }
        }
        
        # 按链统计
        for chain in df['chain'].unique():
            chain_df = df[df['chain'] == chain]
            stats['by_chain'][chain] = {
                'transaction_count': len(chain_df),
                'total_gas_fee_eth': chain_df['gas_fee_eth'].sum(),
                'total_gas_fee_usd': chain_df['gas_fee_usd'].sum() if chain_df['gas_fee_usd'].notna().any() else None,
                'avg_gas_fee_eth': chain_df['gas_fee_eth'].mean(),
                'avg_gas_price_gwei': chain_df['gas_price_gwei'].mean()
            }
        
        # 按交易类型统计
        for tx_type in df['tx_type'].unique():
            type_df = df[df['tx_type'] == tx_type]
            stats['by_transaction_type'][tx_type] = {
                'transaction_count': len(type_df),
                'total_gas_fee_eth': type_df['gas_fee_eth'].sum(),
                'total_gas_fee_usd': type_df['gas_fee_usd'].sum() if type_df['gas_fee_usd'].notna().any() else None,
                'avg_gas_fee_eth': type_df['gas_fee_eth'].mean()
            }
        
        # 按日期统计
        daily_stats = df.groupby('date').agg({
            'gas_fee_eth': ['sum', 'mean', 'count'],
            'gas_fee_usd': ['sum', 'mean'],
            'gas_price_gwei': 'mean'
        }).round(6)
        
        for date in daily_stats.index:
            stats['by_date'][date] = {
                'transaction_count': int(daily_stats.loc[date, ('gas_fee_eth', 'count')]),
                'total_gas_fee_eth': float(daily_stats.loc[date, ('gas_fee_eth', 'sum')]),
                'avg_gas_fee_eth': float(daily_stats.loc[date, ('gas_fee_eth', 'mean')]),
                'avg_gas_price_gwei': float(daily_stats.loc[date, ('gas_price_gwei', 'mean')])
            }
            
            if not pd.isna(daily_stats.loc[date, ('gas_fee_usd', 'sum')]):
                stats['by_date'][date]['total_gas_fee_usd'] = float(daily_stats.loc[date, ('gas_fee_usd', 'sum')])
                stats['by_date'][date]['avg_gas_fee_usd'] = float(daily_stats.loc[date, ('gas_fee_usd', 'mean')])
        
        # 按地址统计
        for address in df['from_address'].unique():
            addr_df = df[df['from_address'] == address]
            stats['by_address'][address] = {
                'transaction_count': len(addr_df),
                'total_gas_fee_eth': addr_df['gas_fee_eth'].sum(),
                'total_gas_fee_usd': addr_df['gas_fee_usd'].sum() if addr_df['gas_fee_usd'].notna().any() else None,
                'avg_gas_fee_eth': addr_df['gas_fee_eth'].mean(),
                'chains_used': addr_df['chain'].unique().tolist()
            }
        
        return stats
    
    def save_results(self, stats: Dict, filename: str = None):
        """保存结果到文件"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'gas_fee_analysis_{timestamp}.json'
        
        filepath = Path(filename)
        
        # 处理不能JSON序列化的数据
        def json_serializer(obj):
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            elif isinstance(obj, Decimal):
                return float(obj)
            elif hasattr(obj, 'item'):
                return obj.item()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=json_serializer)
        
        logger.info(f"结果已保存到: {filepath}")
        return filepath
    
    def print_summary(self, stats: Dict):
        """打印统计摘要"""
        if 'error' in stats:
            print(f"错误: {stats['error']}")
            return
        
        summary = stats['summary']
        print("\n" + "="*60)
        print("           GAS FEE 统计报告")
        print("="*60)
        
        print(f"\n📊 总体统计:")
        print(f"   交易总数: {summary['total_transactions']:,}")
        print(f"   总Gas费用: {summary['total_gas_fee_eth']:.6f} ETH")
        if summary['total_gas_fee_usd']:
            print(f"   总Gas费用: ${summary['total_gas_fee_usd']:.2f} USD")
        print(f"   平均Gas费用: {summary['avg_gas_fee_eth']:.6f} ETH")
        if summary['avg_gas_fee_usd']:
            print(f"   平均Gas费用: ${summary['avg_gas_fee_usd']:.2f} USD")
        print(f"   时间范围: {summary['date_range']['start']} 至 {summary['date_range']['end']}")
        
        print(f"\n⛽ Gas价格分析:")
        gas_analysis = stats['gas_price_analysis']
        print(f"   最低Gas价格: {gas_analysis['min_gwei']:.2f} Gwei")
        print(f"   最高Gas价格: {gas_analysis['max_gwei']:.2f} Gwei")
        print(f"   平均Gas价格: {gas_analysis['avg_gwei']:.2f} Gwei")
        print(f"   中位数Gas价格: {gas_analysis['median_gwei']:.2f} Gwei")
        
        print(f"\n🔗 按链统计:")
        for chain, data in stats['by_chain'].items():
            print(f"   {chain}:")
            print(f"     交易数: {data['transaction_count']:,}")
            print(f"     总费用: {data['total_gas_fee_eth']:.6f} ETH")
            if data['total_gas_fee_usd']:
                print(f"     总费用: ${data['total_gas_fee_usd']:.2f} USD")
            print(f"     平均费用: {data['avg_gas_fee_eth']:.6f} ETH")
            print(f"     平均Gas价格: {data['avg_gas_price_gwei']:.2f} Gwei")
            print()
        
        print(f"\n📝 按交易类型统计:")
        for tx_type, data in stats['by_transaction_type'].items():
            print(f"   {tx_type}:")
            print(f"     交易数: {data['transaction_count']:,}")
            print(f"     总费用: {data['total_gas_fee_eth']:.6f} ETH")
            if data['total_gas_fee_usd']:
                print(f"     总费用: ${data['total_gas_fee_usd']:.2f} USD")
            print(f"     平均费用: {data['avg_gas_fee_eth']:.6f} ETH")
            print()


async def main():
    """主函数示例"""
    # 配置参数
    addresses = [
        "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",  # 示例地址
        # 添加更多地址...
    ]
    
    chains = ['ethereum', 'bsc', 'polygon']  # 要查询的链
    
    # API密钥配置 - 需要用户提供
    api_keys = {
        'ethereum': 'YOUR_ETHERSCAN_API_KEY',
        'bsc': 'YOUR_BSCSCAN_API_KEY', 
        'polygon': 'YOUR_POLYGONSCAN_API_KEY',
        # 添加更多API密钥...
    }
    
    # 时间范围 (可选)
    start_date = datetime.now() - timedelta(days=30)  # 最近30天
    end_date = datetime.now()
    
    # 执行分析
    async with GasFeeTracker() as tracker:
        stats = await tracker.analyze_gas_fees(
            addresses=addresses,
            chains=chains,
            api_keys=api_keys,
            start_date=start_date,
            end_date=end_date
        )
        
        # 显示结果
        tracker.print_summary(stats)
        
        # 保存结果
        tracker.save_results(stats)

if __name__ == "__main__":
    asyncio.run(main())