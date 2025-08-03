# -*- coding: utf-8 -*-
"""
工具模块
提供通用的辅助功能
"""

import os
import time
import json
import random
import hashlib
import requests
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
from urllib.parse import urlparse
import subprocess
from logger import logger

class NetworkUtils:
    """网络工具类"""
    
    @staticmethod
    def check_internet_connection(timeout: int = 5) -> bool:
        """检查网络连接"""
        try:
            # 尝试连接Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout)
            return True
        except OSError:
            try:
                # 备用：尝试连接百度
                socket.create_connection(("114.114.114.114", 53), timeout)
                return True
            except OSError:
                return False
    
    @staticmethod
    def get_public_ip() -> Optional[str]:
        """获取公网IP"""
        try:
            # 尝试多个IP查询服务
            services = [
                "https://api.ipify.org",
                "https://ipinfo.io/ip",
                "https://api.ip.sb/ip",
                "https://ifconfig.me/ip"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        if NetworkUtils.is_valid_ip(ip):
                            return ip
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.错误(f"获取公网IP失败: {str(e)}")
            return None
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """验证IP地址格式"""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    @staticmethod
    def test_proxy(proxy: str, timeout: int = 10) -> bool:
        """测试代理可用性"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=timeout
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    @staticmethod
    def get_domain_info(url: str) -> Dict[str, str]:
        """获取域名信息"""
        try:
            parsed = urlparse(url)
            return {
                'scheme': parsed.scheme,
                'domain': parsed.netloc,
                'path': parsed.path,
                'full_url': url
            }
        except Exception as e:
            logger.错误(f"解析URL失败: {str(e)}")
            return {}

class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def ensure_dir(directory: str) -> bool:
        """确保目录存在"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            logger.错误(f"创建目录失败 {directory}: {str(e)}")
            return False
    
    @staticmethod
    def save_json(data: Any, filepath: str, indent: int = 2) -> bool:
        """保存JSON文件"""
        try:
            # 确保目录存在
            directory = os.path.dirname(filepath)
            if directory:
                FileUtils.ensure_dir(directory)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.错误(f"保存JSON文件失败 {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_json(filepath: str) -> Optional[Any]:
        """加载JSON文件"""
        try:
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.错误(f"加载JSON文件失败 {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def save_text(text: str, filepath: str) -> bool:
        """保存文本文件"""
        try:
            directory = os.path.dirname(filepath)
            if directory:
                FileUtils.ensure_dir(directory)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return True
            
        except Exception as e:
            logger.错误(f"保存文本文件失败 {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_text(filepath: str) -> Optional[str]:
        """加载文本文件"""
        try:
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.错误(f"加载文本文件失败 {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(filepath)
        except Exception:
            return 0
    
    @staticmethod
    def delete_file(filepath: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except Exception as e:
            logger.错误(f"删除文件失败 {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def cleanup_old_files(directory: str, max_age_hours: int = 24, pattern: str = "*") -> int:
        """清理旧文件"""
        try:
            import glob
            
            if not os.path.exists(directory):
                return 0
            
            pattern_path = os.path.join(directory, pattern)
            files = glob.glob(pattern_path)
            
            cutoff_time = time.time() - (max_age_hours * 3600)
            deleted_count = 0
            
            for file in files:
                try:
                    if os.path.getmtime(file) < cutoff_time:
                        os.remove(file)
                        deleted_count += 1
                except:
                    continue
            
            return deleted_count
            
        except Exception as e:
            logger.错误(f"清理旧文件失败: {str(e)}")
            return 0

class TimeUtils:
    """时间工具类"""
    
    @staticmethod
    def get_timestamp() -> int:
        """获取当前时间戳"""
        return int(time.time())
    
    @staticmethod
    def get_datetime_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取格式化时间字符串"""
        return datetime.now().strftime(fmt)
    
    @staticmethod
    def sleep_random(min_seconds: float, max_seconds: float):
        """随机睡眠"""
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)
    
    @staticmethod
    def is_within_time_range(start_hour: int, end_hour: int) -> bool:
        """检查当前时间是否在指定范围内"""
        current_hour = datetime.now().hour
        
        if start_hour <= end_hour:
            return start_hour <= current_hour <= end_hour
        else:
            # 跨天的情况
            return current_hour >= start_hour or current_hour <= end_hour
    
    @staticmethod
    def get_next_run_time(interval_hours: int) -> datetime:
        """获取下次运行时间"""
        return datetime.now() + timedelta(hours=interval_hours)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化持续时间"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"

class CryptoUtils:
    """加密工具类"""
    
    @staticmethod
    def generate_hash(text: str, algorithm: str = "md5") -> str:
        """生成哈希值"""
        try:
            if algorithm == "md5":
                return hashlib.md5(text.encode()).hexdigest()
            elif algorithm == "sha256":
                return hashlib.sha256(text.encode()).hexdigest()
            else:
                return hashlib.md5(text.encode()).hexdigest()
        except Exception as e:
            logger.错误(f"生成哈希失败: {str(e)}")
            return ""
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """生成随机字符串"""
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def is_valid_ethereum_address(address: str) -> bool:
        """验证以太坊地址格式"""
        try:
            # 基本格式检查
            if not address.startswith('0x'):
                return False
            
            if len(address) != 42:
                return False
            
            # 检查是否为有效的十六进制
            int(address[2:], 16)
            return True
            
        except ValueError:
            return False

class SystemUtils:
    """系统工具类"""
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """获取系统信息"""
        try:
            import platform
            
            return {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            logger.错误(f"获取系统信息失败: {str(e)}")
            return {}
    
    @staticmethod
    def run_command(command: str, timeout: int = 30) -> Dict[str, Any]:
        """运行系统命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """获取内存使用情况"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            return {
                'total': memory.total / (1024**3),  # GB
                'available': memory.available / (1024**3),  # GB
                'used': memory.used / (1024**3),  # GB
                'percentage': memory.percent
            }
        except ImportError:
            logger.警告("psutil未安装，无法获取内存信息")
            return {}
        except Exception as e:
            logger.错误(f"获取内存信息失败: {str(e)}")
            return {}

class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_proxy_format(proxy: str) -> bool:
        """验证代理格式"""
        try:
            # 支持格式: ip:port 或 protocol://ip:port
            if '://' in proxy:
                parts = proxy.split('://', 1)
                if len(parts) != 2:
                    return False
                protocol, address = parts
                if protocol not in ['http', 'https', 'socks4', 'socks5']:
                    return False
            else:
                address = proxy
            
            # 验证 ip:port 格式
            if ':' not in address:
                return False
            
            ip, port = address.rsplit(':', 1)
            
            # 验证IP
            if not NetworkUtils.is_valid_ip(ip):
                return False
            
            # 验证端口
            port_num = int(port)
            return 1 <= port_num <= 65535
            
        except Exception:
            return False
    
    @staticmethod
    def is_valid_ethereum_address(address: str) -> bool:
        """验证以太坊地址格式"""
        try:
            # 以太坊地址必须以0x开头，长度为42个字符
            if not address.startswith('0x'):
                return False
            
            if len(address) != 42:
                return False
            
            # 检查是否为有效的十六进制字符
            hex_part = address[2:]
            int(hex_part, 16)
            
            return True
            
        except Exception:
            return False

class RetryUtils:
    """重试工具类"""
    
    @staticmethod
    def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0, 
                          max_delay: float = 60.0, backoff_factor: float = 2.0):
        """带退避的重试装饰器"""
        def wrapper(*args, **kwargs):
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.错误(f"重试{max_retries}次后仍然失败: {str(e)}")
                        raise
                    
                    logger.警告(f"第{attempt + 1}次尝试失败，{delay:.1f}秒后重试: {str(e)}")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
        return wrapper

class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_faucet_config(config: Dict[str, Any]) -> List[str]:
        """验证水龙头配置"""
        errors = []
        
        # 必需字段
        required_fields = ['url', 'network']
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f"缺少必需字段: {field}")
        
        # URL格式验证
        if 'url' in config and config['url']:
            if not ValidationUtils.validate_url(config['url']):
                errors.append("URL格式无效")
        
        return errors
    
    @staticmethod
    def validate_browser_config(config: Dict[str, Any]) -> List[str]:
        """验证浏览器配置"""
        errors = []
        
        # 超时时间验证
        if 'timeout' in config:
            timeout = config['timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                errors.append("超时时间必须为正数")
        
        return errors
    
    @staticmethod
    def validate_proxy_config(config: Dict[str, Any]) -> List[str]:
        """验证代理配置"""
        errors = []
        
        if 'proxy_list' in config and config['proxy_list']:
            for i, proxy in enumerate(config['proxy_list']):
                if not ValidationUtils.validate_proxy_format(proxy):
                    errors.append(f"代理格式无效 (索引 {i}): {proxy}")
        
        return errors

# 导出常用工具实例
network_utils = NetworkUtils()
file_utils = FileUtils()
time_utils = TimeUtils()
crypto_utils = CryptoUtils()
system_utils = SystemUtils()
validation_utils = ValidationUtils()
retry_utils = RetryUtils()
config_validator = ConfigValidator()

# 导出
__all__ = [
    'NetworkUtils', 'FileUtils', 'TimeUtils', 'CryptoUtils', 'SystemUtils',
    'ValidationUtils', 'RetryUtils', 'ConfigValidator',
    'network_utils', 'file_utils', 'time_utils', 'crypto_utils', 
    'system_utils', 'validation_utils', 'retry_utils', 'config_validator'
]