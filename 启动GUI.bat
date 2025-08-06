@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ==========================================
echo    Gas Fee Tracker GUI 启动器
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检测正常

REM 检查依赖是否安装
echo 检查依赖包...
python -c "import tkinter, aiohttp, requests" >nul 2>&1
if errorlevel 1 (
    echo ❌ 缺少必要依赖包
    echo 正在自动安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo ✅ 依赖包检查完成

REM 检查配置文件
if not exist "QueryGasFee\.env" (
    echo.
    echo ⚠️  警告: 未找到配置文件 .env
    if exist "QueryGasFee\.env.example" (
        echo 正在复制示例配置文件...
        copy "QueryGasFee\.env.example" "QueryGasFee\.env" >nul
        echo ✅ 已创建 .env 文件
        echo.
        echo 📝 请编辑 QueryGasFee\.env 文件，配置您的API密钥
        echo 配置完成后重新运行此脚本
        echo.
        pause
        exit /b 0
    ) else (
        echo ❌ 未找到 .env.example 文件
        echo 请确保在正确的项目目录中运行
        pause
        exit /b 1
    )
)

echo ✅ 配置文件检查完成
echo.
echo 🚀 启动 Gas Fee Tracker GUI...
echo.

REM 启动GUI应用
python QueryGasFee\run_gui.py

echo.
echo 程序已退出
pause