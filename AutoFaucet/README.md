# 0G测试网自动领水脚本

一个基于浏览器自动化的0G测试网代币领取脚本，支持验证码识别、IP伪装和反检测功能。

## 功能特性

- 🚀 **全自动领取**: 自动访问水龙头页面，处理Twitter跳转，连接钱包，完成领取
- 🔍 **验证码识别**: 支持图片验证码、reCAPTCHA v2等多种验证码类型
- 🛡️ **反检测机制**: 基于undetected-chromedriver，模拟真实用户行为
- 🌐 **代理支持**: 支持HTTP/HTTPS/SOCKS代理，防止IP封锁
- 📊 **详细日志**: 中文日志输出，记录每个操作步骤
- ⚙️ **模块化设计**: 配置管理、浏览器管理、验证码处理等模块分离
- 🔄 **多种运行模式**: 单次运行、连续运行、组件测试

## 快速开始

### 1. 安装依赖

```bash
cd /Users/ihrr/Code/python/test/autofaucet
pip install -r requirements.txt
```

### 2. 创建配置文件

```bash
python main.py --create-config
```

这将创建一个默认的 `config.json` 配置文件。

### 3. 编辑配置

打开 `config.json` 文件，根据需要修改配置：

```json
{
  "faucet": {
    "url": "https://hub.0g.ai/faucet",
    "network_name": "0G Testnet",
    "wallet_address": "",
    "claim_amount": "0.1",
    "cooldown_hours": 24
  },
  "browser": {
    "browser_type": "chrome",
    "headless": false,
    "timeout": 30,
    "user_agent": "",
    "window_size": [1280, 720]
  },
  "captcha": {
    "service_type": "local_ocr",
    "api_key": "",
    "timeout": 60
  },
  "proxy": {
    "enabled": false,
    "proxy_list": [],
    "rotation_interval": 5
  }
}
```

### 4. 运行脚本

#### 单次运行
```bash
python main.py --mode single
```

#### 连续运行（每24小时一次）
```bash
python main.py --mode continuous --interval 24
```

#### 测试组件
```bash
python main.py --mode test
```

## 配置说明

### 水龙头配置 (faucet)

- `url`: 水龙头网站URL
- `network_name`: 测试网络名称
- `wallet_address`: 钱包地址（留空则自动连接钱包）
- `claim_amount`: 领取数量
- `cooldown_hours`: 冷却时间（小时）

### 浏览器配置 (browser)

- `browser_type`: 浏览器类型（chrome/firefox/edge）
- `headless`: 是否无头模式
- `timeout`: 页面加载超时时间
- `user_agent`: 自定义User-Agent
- `window_size`: 浏览器窗口大小

### 验证码配置 (captcha)

- `service_type`: 验证码服务类型
  - `local_ocr`: 本地OCR识别（免费）
  - `ocr_space`: OCR.space在线服务（免费）
  - `2captcha`: 2captcha付费服务
- `api_key`: API密钥（付费服务需要）
- `timeout`: 验证码识别超时时间

### 代理配置 (proxy)

- `enabled`: 是否启用代理
- `proxy_list`: 代理列表，格式：`["ip:port", "http://ip:port"]`
- `rotation_interval`: 代理轮换间隔（分钟）

## 命令行参数

```bash
python main.py [选项]

选项:
  --config, -c          配置文件路径 (默认: config.json)
  --mode, -m           运行模式 (single/continuous/test)
  --interval, -i       连续模式间隔时间（小时，默认: 24.0）
  --max-attempts, -n   最大尝试次数（0表示无限制）
  --create-config      创建默认配置文件
  --help, -h           显示帮助信息
```

## 项目结构

```
autofaucet/
├── main.py              # 主程序入口
├── config.py            # 配置管理模块
├── logger.py            # 日志模块
├── browser_manager.py   # 浏览器管理模块
├── captcha_solver.py    # 验证码处理模块
├── faucet_handler.py    # 水龙头处理模块
├── utils.py             # 工具模块
├── requirements.txt     # 依赖列表
├── config.json          # 配置文件
├── logs/                # 日志目录
│   ├── app.log         # 应用日志
│   └── success_records.json  # 成功记录
└── screenshots/         # 截图目录
```

## 使用示例

### 1. 基础使用

```bash
# 创建配置文件
python main.py --create-config

# 测试组件
python main.py --mode test

# 单次领取
python main.py --mode single
```

### 2. 连续运行

```bash
# 每12小时运行一次
python main.py --mode continuous --interval 12

# 最多尝试10次
python main.py --mode continuous --max-attempts 10
```

### 3. 使用代理

编辑 `config.json`：

```json
{
  "proxy": {
    "enabled": true,
    "proxy_list": [
      "127.0.0.1:8080",
      "http://proxy1.example.com:3128",
      "socks5://proxy2.example.com:1080"
    ],
    "rotation_interval": 5
  }
}
```

### 4. 使用付费验证码服务

编辑 `config.json`：

```json
{
  "captcha": {
    "service_type": "2captcha",
    "api_key": "your_2captcha_api_key",
    "timeout": 120
  }
}
```

## 注意事项

### 安全建议

1. **代理使用**: 建议使用高质量的住宅代理，避免数据中心IP
2. **频率控制**: 不要设置过于频繁的运行间隔，建议至少12小时
3. **钱包安全**: 使用测试钱包，不要使用包含真实资产的钱包
4. **配置保护**: 不要将包含API密钥的配置文件上传到公共仓库

### 故障排除

1. **浏览器启动失败**
   - 检查Chrome浏览器是否正确安装
   - 尝试更新ChromeDriver
   - 检查系统权限

2. **验证码识别失败**
   - 检查网络连接
   - 验证API密钥是否正确
   - 尝试更换验证码服务

3. **网络连接问题**
   - 检查代理配置
   - 验证代理服务器状态
   - 尝试更换代理

4. **页面元素找不到**
   - 网站可能已更新，需要更新选择器
   - 检查页面加载是否完成
   - 增加等待时间

### 法律声明

本脚本仅用于学习和测试目的。使用者需要：

1. 遵守目标网站的服务条款
2. 不进行恶意攻击或滥用
3. 承担使用风险和责任
4. 遵守当地法律法规

## 更新日志

### v1.0.0
- 初始版本发布
- 支持0G测试网自动领取
- 集成验证码识别功能
- 实现反检测机制
- 添加代理支持

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License