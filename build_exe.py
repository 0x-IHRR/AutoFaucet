#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gas Fee Tracker GUI打包脚本

使用PyInstaller将GUI应用打包成Windows可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['QueryGasFee/run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('QueryGasFee/*.py', 'QueryGasFee'),
        ('QueryGasFee/.env.example', 'QueryGasFee'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'asyncio',
        'aiohttp',
        'requests',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'plotly',
        'python-dotenv',
        'orjson',
        'httpx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GasFeeTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有图标文件，可以在这里指定
)
'''
    
    with open('GasFeeTracker.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 规格文件已创建")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    print("这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 使用规格文件构建
        subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean",
            "GasFeeTracker.spec"
        ], check=True)
        
        print("✅ 可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_portable_package():
    """创建便携版本包"""
    print("创建便携版本包...")
    
    # 创建发布目录
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_path = Path("dist/GasFeeTracker.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "GasFeeTracker.exe")
    
    # 复制必要文件
    files_to_copy = [
        "README.md",
        "QueryGasFee/.env.example",
    ]
    
    for file_path in files_to_copy:
        src = Path(file_path)
        if src.exists():
            if src.name == ".env.example":
                shutil.copy2(src, release_dir / ".env.example")
            else:
                shutil.copy2(src, release_dir / src.name)
    
    # 创建使用说明
    usage_text = '''
# Gas Fee Tracker 使用说明

## 快速开始

1. 首次使用前，请将 `.env.example` 重命名为 `.env`
2. 在 `.env` 文件中配置您的API密钥
3. 双击 `GasFeeTracker.exe` 启动应用

## API密钥配置

支持的API服务商：
- Etherscan (ethereum)
- BscScan (bsc)
- PolygonScan (polygon)
- Arbiscan (arbitrum)
- Optimistic Etherscan (optimism)
- Snowtrace (avalanche)

## 功能特性

- 🔍 多链Gas费用查询分析
- 📊 可视化图表生成
- 💾 数据导出保存
- 🎯 智能统计分析
- 🖥️ 简洁直观的GUI界面

## 技术支持

如有问题，请访问项目GitHub页面获取帮助。
'''
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(usage_text)
    
    print(f"✅ 便携版本包已创建: {release_dir.absolute()}")

def cleanup():
    """清理临时文件"""
    print("清理临时文件...")
    
    cleanup_paths = [
        "build",
        "__pycache__",
        "QueryGasFee/__pycache__",
        "GasFeeTracker.spec"
    ]
    
    for path in cleanup_paths:
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()
    
    print("✅ 清理完成")

def main():
    """主函数"""
    print("🚀 Gas Fee Tracker GUI 打包工具")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("QueryGasFee/run_gui.py").exists():
        print("❌ 请在项目根目录运行此脚本")
        return
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("PyInstaller未安装")
        if input("是否自动安装PyInstaller? (y/n): ").lower() == 'y':
            if not install_pyinstaller():
                return
        else:
            print("请手动安装PyInstaller: pip install pyinstaller")
            return
    
    print("\n选择打包方式:")
    print("1. 单文件可执行程序 (推荐)")
    print("2. 文件夹形式 (包含所有依赖)")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        # 单文件模式
        create_spec_file()
        if build_executable():
            create_portable_package()
            print("\n🎉 打包完成！")
            print(f"可执行文件位置: {Path('release/GasFeeTracker.exe').absolute()}")
            print("\n注意事项:")
            print("- 首次运行可能较慢，这是正常现象")
            print("- 请确保目标机器安装了Visual C++ Redistributable")
            print("- 配置.env文件后即可使用")
    elif choice == "2":
        print("文件夹模式打包...")
        try:
            subprocess.run([
                sys.executable, "-m", "PyInstaller",
                "--onedir",
                "--windowed",
                "--name=GasFeeTracker",
                "--add-data=QueryGasFee/*.py;QueryGasFee",
                "--add-data=QueryGasFee/.env.example;QueryGasFee",
                "QueryGasFee/run_gui.py"
            ], check=True)
            print("✅ 文件夹模式打包完成")
            print(f"程序位置: {Path('dist/GasFeeTracker').absolute()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 打包失败: {e}")
    else:
        print("无效选择")
        return
    
    # 询问是否清理
    if input("\n是否清理临时文件? (y/n): ").lower() == 'y':
        cleanup()
    
    print("\n打包完成！")

if __name__ == "__main__":
    main()