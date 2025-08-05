#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
用于管理API密钥、链配置和其他设置
"""

import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class APIConfig:
    """API配置类"""
    etherscan_api_key: str = ""
    bscscan_api_key: str = ""
    polygonscan_api_key: str = ""
    arbiscan_api_key: str = ""
    optimism_api_key: str = ""
    snowtrace_api_key: str = ""
    
    def get_api_keys(self) -> Dict[str, str]:
        """获取所有API密钥"""
        return {
            'ethereum': self.etherscan_api_key,
            'bsc': self.bscscan_api_key,
            'polygon': self.polygonscan_api_key,
            'arbitrum': self.arbiscan_api_key,
            'optimism': self.optimism_api_key,
            'avalanche': self.snowtrace_api_key
        }
    
    def validate(self) -> List[str]:
        """验证API密钥配置"""
        missing = []
        api_keys = self.get_api_keys()
        for chain, key in api_keys.items():
            if not key or key == "YOUR_API_KEY_HERE":
                missing.append(chain)
        return missing

class Config:
    """主配置类"""
    
    def __init__(self):
        self.api_config = self._load_api_config()
        self.default_chains = ['ethereum', 'bsc', 'polygon']
        self.default_time_range_days = 30
        self.max_transactions_per_request = 1000
        self.rate_limit_delay = 0.2  # 秒
        
    def _load_api_config(self) -> APIConfig:
        """从环境变量或配置文件加载API配置"""
        return APIConfig(
            etherscan_api_key=os.getenv('ETHERSCAN_API_KEY', ''),
            bscscan_api_key=os.getenv('BSCSCAN_API_KEY', ''),
            polygonscan_api_key=os.getenv('POLYGONSCAN_API_KEY', ''),
            arbiscan_api_key=os.getenv('ARBISCAN_API_KEY', ''),
            optimism_api_key=os.getenv('OPTIMISM_API_KEY', ''),
            snowtrace_api_key=os.getenv('SNOWTRACE_API_KEY', '')
        )
    
    def get_supported_chains(self) -> List[str]:
        """获取支持的区块链列表"""
        return ['ethereum', 'bsc', 'polygon', 'arbitrum', 'optimism', 'avalanche']
    
    def get_chain_display_names(self) -> Dict[str, str]:
        """获取链的显示名称"""
        return {
            'ethereum': 'Ethereum (ETH)',
            'bsc': 'Binance Smart Chain (BNB)',
            'polygon': 'Polygon (MATIC)',
            'arbitrum': 'Arbitrum (ETH)',
            'optimism': 'Optimism (ETH)',
            'avalanche': 'Avalanche (AVAX)'
        }
    
    def get_api_documentation(self) -> Dict[str, str]:
        """获取各链API文档链接"""
        return {
            'ethereum': 'https://docs.etherscan.io/api-endpoints/accounts',
            'bsc': 'https://docs.bscscan.com/api-endpoints/accounts',
            'polygon': 'https://docs.polygonscan.com/api-endpoints/accounts',
            'arbitrum': 'https://docs.arbiscan.io/api-endpoints/accounts',
            'optimism': 'https://docs.optimism.etherscan.io/api-endpoints/accounts',
            'avalanche': 'https://docs.snowtrace.io/api-endpoints/accounts'
        }
    
    def get_api_registration_links(self) -> Dict[str, str]:
        """获取API注册链接"""
        return {
            'ethereum': 'https://etherscan.io/apis',
            'bsc': 'https://bscscan.com/apis',
            'polygon': 'https://polygonscan.com/apis',
            'arbitrum': 'https://arbiscan.io/apis',
            'optimism': 'https://optimistic.etherscan.io/apis',
            'avalanche': 'https://snowtrace.io/apis'
        }

# 全局配置实例
config = Config()