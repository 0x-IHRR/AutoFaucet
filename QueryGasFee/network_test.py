#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络连接测试脚本
用于诊断API请求异常的具体原因
"""

import asyncio
import aiohttp
import ssl
import certifi

async def test_network_connection():
    """测试网络连接"""
    print("🌐 网络连接测试")
    print("=" * 50)
    
    # 创建SSL上下文
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    # 测试URL列表
    test_urls = [
        {
            'name': 'CoinGecko API (价格数据)',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd',
            'timeout': 10
        },
        {
            'name': 'Etherscan API (区块链数据)',
            'url': 'https://api.etherscan.io/api?module=stats&action=ethprice&apikey=YourApiKeyToken',
            'timeout': 10
        },
        {
            'name': 'Google DNS (基础连接)',
            'url': 'https://dns.google/resolve?name=google.com&type=A',
            'timeout': 5
        }
    ]
    
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=10,
        limit_per_host=5,
        ttl_dns_cache=300,
        use_dns_cache=True,
    )
    
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={'User-Agent': 'Gas-Fee-Tracker/1.0'}
    ) as session:
        
        for test in test_urls:
            print(f"\n🔍 测试: {test['name']}")
            print(f"   URL: {test['url']}")
            
            try:
                async with session.get(test['url']) as response:
                    print(f"   ✅ 状态码: {response.status}")
                    print(f"   📊 响应头: {dict(response.headers)}")
                    
                    if response.status == 200:
                        content = await response.text()
                        print(f"   📝 响应内容: {content[:200]}...")
                    else:
                        print(f"   ❌ HTTP错误: {response.status}")
                        
            except asyncio.TimeoutError:
                print(f"   ⏰ 连接超时 (>{test['timeout']}秒)")
            except aiohttp.ClientConnectorError as e:
                print(f"   🔌 连接错误: {e}")
            except aiohttp.ClientSSLError as e:
                print(f"   🔒 SSL错误: {e}")
            except Exception as e:
                print(f"   ❌ 其他错误: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 诊断建议:")
    print("1. 检查网络连接是否正常")
    print("2. 检查防火墙设置")
    print("3. 检查代理设置")
    print("4. 尝试使用VPN")
    print("5. 检查DNS设置")

if __name__ == "__main__":
    asyncio.run(test_network_connection())