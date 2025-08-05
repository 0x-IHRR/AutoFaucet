# 🔥 Web3 钱包 Gas Fee 查询统计工具

一个功能强大的Web3钱包链上gas费用查询和统计分析工具，支持多链、多钱包、自定义时间范围的gas费用统计分析。

## ✨ 功能特性

- 🔗 **多链支持**: 支持 Ethereum、BSC、Polygon、Arbitrum、Optimism、Avalanche
- 👛 **多钱包查询**: 同时查询多个钱包地址的gas费用
- 📅 **自定义时间范围**: 支持指定时间段的数据查询
- 📊 **多维度统计**: 按链、按日期、按交易类型、按地址等多种维度统计
- 💰 **实时价格**: 自动获取代币实时价格，计算USD费用
- 🎯 **交易分类**: 自动识别普通转账、合约交互、合约调用等交易类型
- 💾 **结果导出**: 支持JSON格式结果导出
- 📈 **数据可视化**: 提供丰富的图表展示，包括趋势图、对比图、分布图等
- 🖥️ **友好界面**: 提供交互式命令行界面
- ⚡ **异步处理**: 高效的异步API调用，支持并发查询

## 📋 支持的区块链

| 区块链 | 原生代币 | API提供商 | 免费额度 |
|--------|----------|-----------|----------|
| Ethereum | ETH | Etherscan | 100,000次/日 |
| BSC | BNB | BscScan | 100,000次/日 |
| Polygon | MATIC | PolygonScan | 100,000次/日 |
| Arbitrum | ETH | Arbiscan | 100,000次/日 |
| Optimism | ETH | Optimistic Etherscan | 100,000次/日 |
| Avalanche | AVAX | Snowtrace | 100,000次/日 |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/ihrr/Code/python/test/QueryGasFee/
pip install -r requirements.txt
```

### 2. 配置API密钥

复制环境变量模板文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：
```bash
ETHERSCAN_API_KEY=你的Etherscan_API密钥
BSCSCAN_API_KEY=你的BscScan_API密钥
POLYGONSCAN_API_KEY=你的PolygonScan_API密钥
# ... 其他API密钥
```

### 3. 获取API密钥

访问以下链接获取免费API密钥：

- **Ethereum**: [https://etherscan.io/apis](https://etherscan.io/apis)
- **BSC**: [https://bscscan.com/apis](https://bscscan.com/apis)
- **Polygon**: [https://polygonscan.com/apis](https://polygonscan.com/apis)
- **Arbitrum**: [https://arbiscan.io/apis](https://arbiscan.io/apis)
- **Optimism**: [https://optimistic.etherscan.io/apis](https://optimistic.etherscan.io/apis)
- **Avalanche**: [https://snowtrace.io/apis](https://snowtrace.io/apis)

### 4. 测试配置
```bash
python test_config.py
```

### 5. 运行程序

#### 方式一：快速启动（推荐）
```bash
python run.py
```

#### 方式二：交互式界面
```bash
python run.py cli
# 或者
python cli.py
```

#### 方式三：查看示例
```bash
python run.py example
# 或者
python example_usage.py
```

#### 方式四：可视化现有数据
```bash
python run.py visualize <stats_file.json>
# 或者
python visualizer.py <stats_file.json>
```

#### 方式五：直接使用API
```python
import asyncio
from main import GasFeeTracker
from datetime import datetime, timedelta

async def main():
    addresses = ["0x你的钱包地址"]
    chains = ['ethereum', 'polygon']
    api_keys = {
        'ethereum': '你的API密钥',
        'polygon': '你的API密钥'
    }
    
    async with GasFeeTracker() as tracker:
        stats = await tracker.analyze_gas_fees(
            addresses=addresses,
            chains=chains,
            api_keys=api_keys,
            start_date=datetime.now() - timedelta(days=30)
        )
        
        tracker.print_summary(stats)
        tracker.save_results(stats)

asyncio.run(main())
```

## 📊 统计维度

### 总体统计
- 交易总数
- 总gas费用 (ETH/USD)
- 平均gas费用
- 查询时间范围

### Gas价格分析
- 最低/最高/平均/中位数gas价格
- Gas价格趋势分析

### 按链统计
- 各链交易数量和费用
- 各链平均gas价格
- 链使用频率分析

### 按日期统计
- 每日交易数量和费用
- 日均gas价格变化
- 使用频率时间分布

### 按交易类型统计
- 普通转账 vs 合约交互
- 不同类型交易的费用分布
- 交易复杂度分析

### 按地址统计
- 各地址的交易活跃度
- 各地址的费用消耗
- 地址使用的链分布

## 📁 项目结构

```
QueryGasFee/
├── main.py              # 核心Gas费用追踪器
├── config.py            # 配置管理
├── cli.py               # 交互式命令行界面
├── example_usage.py     # 使用示例
├── visualizer.py        # 数据可视化模块
├── run.py               # 快速启动脚本
├── test_config.py       # 配置测试工具
├── requirements.txt     # 依赖包列表
├── .env.example         # 环境变量模板
├── README.md           # 项目文档
└── gas_fee_tracker.log # 日志文件 (运行时生成)
```

## 🔧 高级配置

### 环境变量配置

在 `.env` 文件中可以配置以下参数：

```bash
# 默认查询时间范围 (天)
DEFAULT_TIME_RANGE_DAYS=30

# API请求速率限制 (秒)
RATE_LIMIT_DELAY=0.2

# 每次请求最大交易数量
MAX_TRANSACTIONS_PER_REQUEST=1000

# 日志级别
LOG_LEVEL=INFO
```

### 自定义链配置

可以在 `main.py` 中的 `_init_chains()` 方法中添加新的区块链支持。

## 📈 输出示例

### 📊 控制台统计报告

```
============================================================
           GAS FEE 统计报告
============================================================

📊 总体统计:
   交易总数: 1,234
   总Gas费用: 2.456789 ETH
   总Gas费用: $4,567.89 USD
   平均Gas费用: 0.001991 ETH
   平均Gas费用: $3.70 USD
   时间范围: 2024-12-04 至 2025-01-03

⛽ Gas价格分析:
   最低Gas价格: 8.50 Gwei
   最高Gas价格: 45.20 Gwei
   平均Gas价格: 18.75 Gwei
   中位数Gas价格: 16.30 Gwei

🔗 按链统计:
   Ethereum:
     交易数: 856
     总费用: 2.123456 ETH
     总费用: $3,945.67 USD
     平均费用: 0.002481 ETH
     平均Gas价格: 19.45 Gwei

   Polygon:
     交易数: 378
     总费用: 0.333333 ETH
     总费用: $622.22 USD
     平均费用: 0.000882 ETH
     平均Gas价格: 15.20 Gwei
```

### 📄 JSON格式统计报告
```json
{
  "summary": {
    "total_transactions": 150,
    "total_gas_fee_eth": 0.245,
    "total_gas_fee_usd": 456.78,
    "avg_gas_fee_eth": 0.00163,
    "avg_gas_fee_usd": 3.04
  },
  "by_chain": {
    "ethereum": {
      "transaction_count": 120,
      "total_gas_fee_eth": 0.198,
      "avg_gas_fee_eth": 0.00165
    }
  },
  "by_date": {
    "2024-01-15": {
      "transaction_count": 25,
      "total_gas_fee_eth": 0.045
    }
  }
}
```

### 📈 可视化图表

工具会自动生成以下类型的图表：

1. **📅 每日Gas费用趋势图**
   - 每日Gas费用变化（ETH和USD）
   - 每日交易数量统计
   - 平均Gas价格趋势

2. **🔗 各链对比分析图**
   - 各区块链交易数量对比
   - 各区块链总费用对比
   - 各区块链平均费用对比

3. **📝 交易类型分布图**
   - 交易类型数量分布饼图
   - 交易类型费用分布饼图

4. **⛽ Gas价格分析图**
   - Gas价格统计分布
   - 最低、平均、中位数、最高价格对比

5. **👤 地址对比图** (多地址查询时)
   - 各地址交易数量对比
   - 各地址总费用对比
   - 各地址平均费用对比

6. **📊 综合仪表板**
   - 集成所有图表的HTML仪表板
   - 交互式图表展示
   - 一键查看所有统计信息

图表支持多种格式：
- 📄 **HTML格式**: 交互式图表，可缩放、悬停查看详情
- 🖼️ **PNG格式**: 静态图片，便于分享和报告
- 📱 **响应式设计**: 自适应不同屏幕尺寸

## 🛠️ 开发指南

### 添加新的区块链支持

1. 在 `main.py` 的 `_init_chains()` 方法中添加新链配置
2. 在 `config.py` 中添加对应的API配置
3. 更新 `.env.example` 文件

### 扩展统计功能

1. 在 `_generate_statistics()` 方法中添加新的统计逻辑
2. 在 `print_summary()` 方法中添加新的显示格式

### 添加新的数据源

1. 实现新的API客户端类
2. 在 `GasFeeTracker` 中集成新的数据源
3. 更新配置文件

## ⚠️ 注意事项

1. **API限制**: 免费API有调用频率和次数限制，大量查询可能需要付费套餐
2. **数据准确性**: 数据来源于各链的官方区块浏览器API，准确性较高
3. **查询时间**: 大量历史数据查询可能需要较长时间
4. **网络稳定性**: 需要稳定的网络连接
5. **API密钥安全**: 请妥善保管API密钥，不要提交到公共代码仓库

## 🐛 故障排除

### 常见问题

**Q: API调用失败**
A: 检查API密钥是否正确，是否超出调用限制

**Q: 查询速度慢**
A: 减少查询时间范围或地址数量，检查网络连接

**Q: 数据不完整**
A: 某些链可能有API限制，尝试分批查询

**Q: 价格获取失败**
A: CoinGecko API可能有限制，稍后重试

### 日志查看

程序运行时会生成 `gas_fee_tracker.log` 日志文件，包含详细的运行信息和错误信息。

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题或建议，请创建 Issue 或联系开发者。

---

**免责声明**: 本工具仅用于数据查询和分析，不构成任何投资建议。使用者需自行承担使用风险。