# QueryGasFee Project

一个用于查询和分析区块链Gas费用的Python工具，现已支持图形化界面！

## 🎯 功能特性

- 🔍 支持多个主流区块链的Gas费用查询
- 📊 提供详细的统计分析和可视化图表
- 💾 智能数据保存和管理
- ⚙️ 灵活的配置管理系统
- 🔄 异步处理，提高查询效率
- 🖥️ **新增：简洁直观的GUI界面**
- 📦 **新增：一键打包成Windows可执行文件**

## 🚀 快速开始

### 方式一：GUI图形界面（推荐）

1. **一键启动**
   ```bash
   # Windows用户可直接双击
   启动GUI.bat
   ```

2. **或手动启动**
   ```bash
   pip install -r requirements.txt
   python QueryGasFee/run_gui.py
   ```

3. **打包成可执行文件**
   ```bash
   python build_exe.py
   ```

### 方式二：命令行界面

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置API密钥**
   ```bash
   cp QueryGasFee/.env.example QueryGasFee/.env
   # 编辑 .env 文件，填入您的API密钥
   ```

3. **运行分析**
   ```bash
   cd QueryGasFee
   python main.py
   ```

## 🔧 支持的区块链

| 区块链 | 代码 | API服务商 | 获取密钥 |
|--------|------|-----------|----------|
| Ethereum | `ethereum` | Etherscan | [etherscan.io](https://etherscan.io/apis) |
| BSC | `bsc` | BscScan | [bscscan.com](https://bscscan.com/apis) |
| Polygon | `polygon` | PolygonScan | [polygonscan.com](https://polygonscan.com/apis) |
| Arbitrum | `arbitrum` | Arbiscan | [arbiscan.io](https://arbiscan.io/apis) |
| Optimism | `optimism` | Optimistic Etherscan | [optimistic.etherscan.io](https://optimistic.etherscan.io/apis) |
| Avalanche | `avalanche` | Snowtrace | [snowtrace.io](https://snowtrace.io/apis) |

## 📁 项目结构

```
QueryGasFee-Project/
├── QueryGasFee/
│   ├── main.py              # 主程序（命令行版本）
│   ├── gui_app.py           # GUI应用主文件
│   ├── run_gui.py           # GUI启动器
│   ├── config.py            # 配置管理
│   ├── config_manager.py    # 配置检查工具
│   ├── visualizer.py        # 数据可视化
│   ├── .env.example         # 环境变量示例
│   └── ...
├── Data_Save/               # 数据保存目录
├── charts/                  # 图表保存目录
├── requirements.txt         # Python依赖
├── build_exe.py            # 打包脚本
├── 启动GUI.bat             # Windows启动脚本
├── GUI_README.md           # GUI详细使用说明
└── README.md               # 项目说明
```

## 🖥️ GUI界面预览

GUI应用提供以下功能：

- **配置管理**：自动检查API密钥配置状态
- **参数设置**：钱包地址、区块链选择、时间范围
- **实时分析**：后台异步处理，支持中途停止
- **结果展示**：概览统计、详细数据、操作日志
- **图表生成**：一键生成可视化图表
- **数据导出**：保存分析结果到本地文件

## 📊 输出示例

### 统计报告
```
📊 Gas费用分析报告
==================================================

📈 总体统计:
• 总交易数量: 1,234
• 总Gas费用: 2.456789 ETH
• 平均Gas费用: 0.001991 ETH
• 总Gas费用: $4,567.89 USD
• 平均Gas费用: $3.70 USD
• 时间范围: 2024-01-01 到 2024-01-31

🔗 按区块链统计:
• ETHEREUM:
  - 交易数量: 856
  - 总费用: 1.789123 ETH
  - 平均费用: 0.002090 ETH
  - 平均Gas价格: 25.67 Gwei
```

### 可视化图表
- Gas费用趋势图
- 链间对比图
- Gas价格分布图
- 每日统计图

## 🔧 配置说明

### API密钥配置

在 `QueryGasFee/.env` 文件中配置：

```env
# Ethereum
ETHERSCAN_API_KEY=your_etherscan_api_key_here

# BSC
BSCSCAN_API_KEY=your_bscscan_api_key_here

# Polygon
POLYGONSCAN_API_KEY=your_polygonscan_api_key_here

# Arbitrum
ARBISCAN_API_KEY=your_arbiscan_api_key_here

# Optimism
OPTIMISM_API_KEY=your_optimism_api_key_here

# Avalanche
SNOWTRACE_API_KEY=your_snowtrace_api_key_here
```

### 高级配置

在 `QueryGasFee/config.py` 中可以调整：
- API请求间隔
- 数据保存格式
- 图表样式设置
- 缓存配置

## 📦 打包部署

### 生成Windows可执行文件

```bash
# 运行打包脚本
python build_exe.py

# 选择打包方式
# 1. 单文件可执行程序（推荐）
# 2. 文件夹形式（包含所有依赖）
```

打包完成后：
- 单文件版本：`release/GasFeeTracker.exe`
- 文件夹版本：`dist/GasFeeTracker/`

### 分发注意事项

1. **配置文件**：需要配置.env文件
2. **系统要求**：Windows 10/11
3. **运行时**：可能需要Visual C++ Redistributable
4. **首次启动**：单文件版本首次启动较慢

## 🚨 注意事项

1. **API限制**
   - 免费API有调用频率限制
   - 建议合理设置查询间隔
   - 大量数据查询可能需要付费API

2. **数据准确性**
   - 结果依赖区块链浏览器API
   - USD价格基于历史汇率
   - 建议交叉验证重要数据

3. **性能考虑**
   - 大量交易分析需要时间
   - 建议分批次处理
   - 可随时停止分析过程

## 🐛 故障排除

### 常见问题

1. **"配置检查失败"**
   - 检查.env文件是否存在
   - 确认API密钥格式正确

2. **"分析失败"**
   - 检查网络连接
   - 确认钱包地址格式
   - 查看详细错误日志

3. **GUI启动失败**
   - 确认Python版本3.8+
   - 检查tkinter是否可用
   - 安装完整依赖包

### 获取帮助

- 查看 [GUI_README.md](GUI_README.md) 获取详细GUI使用说明
- 检查日志文件获取错误信息
- 提交GitHub Issue获取技术支持

## 📝 更新日志

### v2.0.0 (GUI版本)
- ✅ 新增GUI图形界面
- ✅ 一键打包成可执行文件
- ✅ Windows批处理启动脚本
- ✅ 改进的配置管理系统
- ✅ 实时日志显示
- ✅ 交互式图表生成

### v1.0.0 (命令行版本)
- ✅ 多链Gas费用查询
- ✅ 统计分析功能
- ✅ 数据可视化
- ✅ 智能数据保存
- ✅ 配置管理系统

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**享受使用Gas Fee Tracker！** 🎉