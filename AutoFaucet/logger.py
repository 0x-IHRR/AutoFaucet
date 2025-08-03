# -*- coding: utf-8 -*-
"""
日志管理模块
提供统一的日志记录功能，支持中文日志输出
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
import coloredlogs
from config import config_manager

class ChineseLogger:
    """中文日志记录器"""
    
    def __init__(self, name: str = "AutoFaucet", log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 获取日志配置
        log_config = config_manager.get_logging_config()
        
        # 设置日志格式
        self.formatter = logging.Formatter(
            fmt=log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 控制台处理器
        if log_config.get("console_enabled", True):
            self._setup_console_handler(log_config.get("level", "INFO"))
        
        # 文件处理器
        if log_config.get("file_enabled", True):
            if log_file is None:
                log_file = f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log"
            self._setup_file_handler(log_file, log_config)
    
    def _setup_console_handler(self, level: str):
        """设置控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # 使用coloredlogs为控制台添加颜色
        coloredlogs.install(
            level=level.upper(),
            logger=self.logger,
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            field_styles={
                'asctime': {'color': 'green'},
                'hostname': {'color': 'magenta'},
                'levelname': {'color': 'white', 'bold': True},
                'name': {'color': 'blue'},
                'programname': {'color': 'cyan'}
            },
            level_styles={
                'debug': {'color': 'white'},
                'info': {'color': 'cyan'},
                'warning': {'color': 'yellow'},
                'error': {'color': 'red'},
                'critical': {'color': 'red', 'bold': True}
            }
        )
    
    def _setup_file_handler(self, log_file: str, log_config: dict):
        """设置文件处理器"""
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 使用RotatingFileHandler支持日志轮转
        max_bytes = self._parse_size(log_config.get("max_file_size", "10MB"))
        backup_count = log_config.get("backup_count", 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        
        self.logger.addHandler(file_handler)
    
    def _parse_size(self, size_str: str) -> int:
        """解析文件大小字符串"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """异常日志（包含堆栈信息）"""
        self.logger.exception(message, *args, **kwargs)
    
    # 中文日志方法
    def 调试(self, message: str, *args, **kwargs):
        """调试日志（中文）"""
        self.debug(f"🔍 {message}", *args, **kwargs)
    
    def 信息(self, message: str, *args, **kwargs):
        """信息日志（中文）"""
        self.info(f"ℹ️ {message}", *args, **kwargs)
    
    def 警告(self, message: str, *args, **kwargs):
        """警告日志（中文）"""
        self.warning(f"⚠️ {message}", *args, **kwargs)
    
    def 错误(self, message: str, *args, **kwargs):
        """错误日志（中文）"""
        self.error(f"❌ {message}", *args, **kwargs)
    
    def 严重错误(self, message: str, *args, **kwargs):
        """严重错误日志（中文）"""
        self.critical(f"🚨 {message}", *args, **kwargs)
    
    def 异常(self, message: str, *args, **kwargs):
        """异常日志（中文）"""
        self.exception(f"💥 {message}", *args, **kwargs)
    
    def 成功(self, message: str, *args, **kwargs):
        """成功日志（中文）"""
        self.info(f"✅ {message}", *args, **kwargs)
    
    # 操作日志方法
    def 开始操作(self, operation: str, target: str = ""):
        """记录操作开始"""
        msg = f"🚀 开始{operation}"
        if target:
            msg += f" - 目标: {target}"
        self.info(msg)
    
    def 完成操作(self, operation: str, result: str = "成功"):
        """记录操作完成"""
        if result == "成功":
            self.info(f"✅ {operation}完成 - {result}")
        else:
            self.error(f"❌ {operation}失败 - {result}")
    
    def 步骤(self, step: str, details: str = ""):
        """记录操作步骤"""
        msg = f"📝 步骤: {step}"
        if details:
            msg += f" - {details}"
        self.info(msg)
    
    def 等待(self, reason: str, duration: float = 0):
        """记录等待操作"""
        msg = f"⏳ 等待: {reason}"
        if duration > 0:
            msg += f" ({duration}秒)"
        self.info(msg)
    
    def 点击(self, element: str):
        """记录点击操作"""
        self.info(f"👆 点击: {element}")
    
    def 输入(self, element: str, content: str = "***"):
        """记录输入操作"""
        self.info(f"⌨️ 输入: {element} -> {content}")
    
    def 导航(self, url: str):
        """记录页面导航"""
        self.info(f"🌐 导航到: {url}")
    
    def 检测(self, item: str, result: str):
        """记录检测结果"""
        if "成功" in result or "找到" in result:
            self.info(f"🔍 检测{item}: {result}")
        else:
            self.warning(f"🔍 检测{item}: {result}")
    
    def 验证码(self, action: str, result: str = ""):
        """记录验证码相关操作"""
        msg = f"🔐 验证码{action}"
        if result:
            msg += f": {result}"
        self.info(msg)
    
    def 钱包(self, action: str, address: str = ""):
        """记录钱包相关操作"""
        msg = f"💰 钱包{action}"
        if address:
            # 隐藏地址中间部分
            masked_address = f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address
            msg += f": {masked_address}"
        self.info(msg)
    
    def 网络请求(self, method: str, url: str, status: int = 0):
        """记录网络请求"""
        msg = f"🌐 {method} {url}"
        if status > 0:
            if 200 <= status < 300:
                msg += f" ✅ {status}"
            else:
                msg += f" ❌ {status}"
        self.info(msg)
    
    def 代理(self, action: str, proxy: str = ""):
        """记录代理相关操作"""
        msg = f"🔄 代理{action}"
        if proxy:
            msg += f": {proxy}"
        self.info(msg)
    
    def 反检测(self, action: str, details: str = ""):
        """记录反检测操作"""
        msg = f"🛡️ 反检测: {action}"
        if details:
            msg += f" - {details}"
        self.debug(msg)

# 创建全局日志实例
logger = ChineseLogger()

# 为了兼容性，也提供英文接口
class Logger:
    """英文日志接口"""
    
    @staticmethod
    def debug(message: str, *args, **kwargs):
        logger.debug(message, *args, **kwargs)
    
    @staticmethod
    def info(message: str, *args, **kwargs):
        logger.info(message, *args, **kwargs)
    
    @staticmethod
    def warning(message: str, *args, **kwargs):
        logger.warning(message, *args, **kwargs)
    
    @staticmethod
    def error(message: str, *args, **kwargs):
        logger.error(message, *args, **kwargs)
    
    @staticmethod
    def critical(message: str, *args, **kwargs):
        logger.critical(message, *args, **kwargs)
    
    @staticmethod
    def exception(message: str, *args, **kwargs):
        logger.exception(message, *args, **kwargs)

# 导出常用实例
__all__ = ['logger', 'Logger', 'ChineseLogger']