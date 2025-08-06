# Gas Fee Tracker GUI 使用指南

## 🚀 快速开始

### 方式一：直接运行Python脚本

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置API密钥**
   - 复制 `QueryGasFee/.env.example` 为 `QueryGasFee/.env`
   - 编辑 `.env` 文件，填入您的API密钥

3. **启动GUI应用**
   ```bash
   python QueryGasFee/run_gui.py
   ```

### 方式二：打包成可执行文件

1. **运行打包脚本**
   ```bash
   python build_exe.py
   ```

2. **选择打包方式**
   - 单文件可执行程序（推荐）：生成一个独立的.exe文件
   - 文件夹形式：包含所有依赖的文件夹

3. **使用可执行文件**
   - 配置.env文件（同上）
   - 双击运行生成的.exe文件

## 🔧 API密钥配置

支持以下区块链浏览器API：

| 区块链 | API服务商 | 获取地址 |
|--------|-----------|----------|
| Ethereum | Etherscan | https://etherscan.io/apis |
| BSC | BscScan | https://bscscan.com/apis |
| Polygon | PolygonScan | https://polygonscan.com/apis |
| Arbitrum | Arbiscan | https://arbiscan.io/apis |
| Optimism | Optimistic Etherscan | https://optimistic.etherscan.io/apis |
| Avalanche | Snowtrace | https://snowtrace.io/apis |

### .env文件示例
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

## 🖥️ GUI界面功能

### 主要功能区域

1. **配置状态**
   - 显示API密钥配置状态
   - 重新检查配置按钮

2. **查询参数**
   - 钱包地址输入
   - 区块链选择（支持多选）
   - 时间范围选择（预设或自定义）

3. **控制按钮**
   - 🔍 开始分析：启动Gas费用分析
   - ⏹ 停止分析：中止当前分析
   - 📊 生成图表：创建可视化图表
   - 💾 保存结果：导出分析数据
   - 📁 打开结果目录：查看保存的文件

4. **结果显示**
   - **📊 概览**：统计摘要和分析报告
   - **📋 详细数据**：交易明细表格
   - **📝 日志**：操作日志和状态信息

### 操作流程

1. **检查配置**：确保API密钥已正确配置
2. **输入地址**：填入要分析的钱包地址
3. **选择链**：勾选需要分析的区块链
4. **设置时间**：选择分析的时间范围
5. **开始分析**：点击"开始分析"按钮
6. **查看结果**：在不同标签页查看分析结果
7. **生成图表**：可选择生成可视化图表
8. **保存数据**：导出分析结果到本地

## 📊 输出文件

### 数据保存目录：`Data_Save/`
- `gas_fee_analysis_YYYYMMDD_HHMMSS.json`：完整分析数据
- `gas_fee_summary_YYYYMMDD_HHMMSS.txt`：分析摘要报告
- `transactions_YYYYMMDD_HHMMSS.csv`：交易明细表格

### 图表保存目录：`charts/`
- `gas_fee_trends.png`：Gas费用趋势图
- `chain_comparison.png`：链间对比图
- `gas_price_distribution.png`：Gas价格分布图
- `daily_statistics.png`：每日统计图

## 🔧 技术要求

### 系统要求
- Windows 10/11
- Python 3.8+ （如果运行源码）
- 网络连接（用于API调用）

### Python依赖
- tkinter（GUI框架）
- aiohttp（异步HTTP客户端）
- requests（HTTP请求）
- pandas（数据处理）
- matplotlib/seaborn（图表生成）
- python-dotenv（环境变量）

## 🚨 注意事项

1. **API限制**
   - 免费API通常有调用频率限制
   - 建议分批次分析大量交易
   - 某些API需要付费才能获取历史数据

2. **性能考虑**
   - 分析大量交易可能需要较长时间
   - 建议合理设置时间范围
   - 可以随时停止分析过程

3. **数据准确性**
   - 结果依赖于区块链浏览器API的数据质量
   - USD价格基于历史汇率，可能存在误差
   - 建议交叉验证重要数据

## 🐛 故障排除

### 常见问题

1. **"配置检查失败"**
   - 检查.env文件是否存在
   - 确认API密钥格式正确
   - 验证API密钥是否有效

2. **"分析失败"**
   - 检查网络连接
   - 确认钱包地址格式正确
   - 查看日志获取详细错误信息

3. **"图表生成失败"**
   - 确保已完成数据分析
   - 检查matplotlib依赖是否正确安装
   - 查看是否有足够的磁盘空间

4. **可执行文件启动慢**
   - 首次启动需要解压，属于正常现象
   - 后续启动会更快
   - 确保杀毒软件未误报

### 获取帮助

- 查看日志标签页的详细错误信息
- 检查控制台输出
- 访问项目GitHub页面提交Issue

## 📝 更新日志

### v1.0.0
- ✅ 基础GUI界面
- ✅ 多链Gas费用分析
- ✅ 可视化图表生成
- ✅ 数据导出功能
- ✅ 可执行文件打包
- ✅ 配置管理系统

---

**享受使用Gas Fee Tracker GUI！** 🎉