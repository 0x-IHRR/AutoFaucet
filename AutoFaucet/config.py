# -*- coding: utf-8 -*-
"""
配置管理模块
负责管理所有配置信息，包括网站配置、用户设置、代理配置等
"""

import yaml
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class Config:
    """主配置类"""
    faucet: 'FaucetConfig'
    browser: 'BrowserConfig'
    captcha: 'CaptchaConfig'
    proxy: 'ProxyConfig'

@dataclass
class FaucetConfig:
    """Faucet网站配置"""
    name: str = "0G Testnet Faucet"
    url: str = "https://faucet.0g.ai/"
    network: str = "0G Testnet"
    wallet_address: str = ""
    wallet_private_key: str = ""
    wallet_connection_method: str = "metamask"  # metamask, direct_input
    max_retry_attempts: int = 3
    retry_delay: int = 5
    request_interval: int = 3600  # 请求间隔（秒）
    timeout: int = 30
    user_agent: str = ""
    requires_wallet: bool = True
    requires_twitter: bool = False
    captcha_type: str = "image"  # image, recaptcha, hcaptcha, slider
    cooldown_hours: int = 24
    selectors: Dict[str, str] = None
    
    def __post_init__(self):
        if self.selectors is None:
            self.selectors = {}

@dataclass
class BrowserConfig:
    """浏览器配置"""
    headless: bool = False
    window_size: tuple = (1920, 1080)
    user_agent: str = ""
    disable_images: bool = True
    disable_javascript: bool = False
    page_load_timeout: int = 30
    implicit_wait: int = 10
    
@dataclass
class ProxyConfig:
    """代理配置"""
    enabled: bool = False
    proxy_type: str = "http"  # http, socks5
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    
@dataclass
class CaptchaConfig:
    """验证码配置"""
    use_paid_service: bool = False
    api_key: str = ""
    service_provider: str = "2captcha"  # 2captcha, anticaptcha
    max_retry: int = 3
    timeout: int = 120

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.config_dir, config_file)
        
        # 默认配置
        self.default_config = {
            "browser": {
                "headless": False,
                "window_size": [1920, 1080],
                "user_agent": "",
                "disable_images": True,
                "disable_javascript": False,
                "page_load_timeout": 30,
                "implicit_wait": 10
            },
            "proxy": {
                "enabled": False,
                "proxy_type": "http",
                "host": "",
                "port": 0,
                "username": "",
                "password": ""
            },
            "captcha": {
                "use_paid_service": False,
                "api_key": "",
                "service_provider": "2captcha",
                "max_retry": 3,
                "timeout": 120
            },
            "faucets": {
                "0g_testnet": {
                    "name": "0G Testnet Faucet",
                    "url": "https://hub.0g.ai/faucet",
                    "network": "0G Testnet",
                    "requires_wallet": True,
                    "requires_twitter": True,
                    "captcha_type": "image",
                    "cooldown_hours": 24,
                    "selectors": {
                        "twitter_button": "a[href*='twitter'], a[href*='x.com']",
                        "connect_wallet_button": "button[class*='connect'], button[class*='wallet']",
                        "wallet_address_input": "input[placeholder*='address'], input[type='text']",
                        "captcha_image": "img[src*='captcha'], canvas",
                        "captcha_input": "input[placeholder*='captcha'], input[placeholder*='验证码']",
                        "submit_button": "button[type='submit'], button[class*='submit']",
                        "claim_button": "button[class*='claim'], button[class*='领取']"
                    }
                }
            },
            "anti_detection": {
                "random_delay_min": 2,
                "random_delay_max": 5,
                "mouse_movement": True,
                "scroll_simulation": True,
                "typing_delay": True,
                "user_agent_rotation": True
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_enabled": True,
                "console_enabled": True,
                "max_file_size": "10MB",
                "backup_count": 5
            }
        }
        
        self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    # 合并默认配置和加载的配置
                    self.config = self._merge_config(self.default_config, loaded_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
                self.config = self.default_config.copy()
        else:
            print("配置文件不存在，创建默认配置文件")
            self.config = self.default_config.copy()
            self.save_config()
        
        return self.config
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """合并配置"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_browser_config(self) -> BrowserConfig:
        """获取浏览器配置"""
        browser_config = self.config.get("browser", {})
        return BrowserConfig(
            headless=browser_config.get("headless", False),
            window_size=tuple(browser_config.get("window_size", [1920, 1080])),
            user_agent=browser_config.get("user_agent", ""),
            disable_images=browser_config.get("disable_images", True),
            disable_javascript=browser_config.get("disable_javascript", False),
            page_load_timeout=browser_config.get("page_load_timeout", 30),
            implicit_wait=browser_config.get("implicit_wait", 10)
        )
    
    def get_proxy_config(self) -> ProxyConfig:
        """获取代理配置"""
        proxy_config = self.config.get("proxy", {})
        return ProxyConfig(
            enabled=proxy_config.get("enabled", False),
            proxy_type=proxy_config.get("proxy_type", "http"),
            host=proxy_config.get("host", ""),
            port=proxy_config.get("port", 0),
            username=proxy_config.get("username", ""),
            password=proxy_config.get("password", "")
        )
    
    def get_captcha_config(self) -> CaptchaConfig:
        """获取验证码配置"""
        captcha_config = self.config.get("captcha", {})
        return CaptchaConfig(
            use_paid_service=captcha_config.get("use_paid_service", False),
            api_key=captcha_config.get("api_key", ""),
            service_provider=captcha_config.get("service_provider", "2captcha"),
            max_retry=captcha_config.get("max_retry", 3),
            timeout=captcha_config.get("timeout", 120)
        )
    
    def get_faucet_config(self, faucet_name: str) -> Optional[FaucetConfig]:
        """获取指定faucet配置"""
        faucets = self.config.get("faucets", {})
        if faucet_name not in faucets:
            return None
        
        faucet_data = faucets[faucet_name]
        return FaucetConfig(
            name=faucet_data.get("name", ""),
            url=faucet_data.get("url", ""),
            network=faucet_data.get("network", ""),
            requires_wallet=faucet_data.get("requires_wallet", True),
            requires_twitter=faucet_data.get("requires_twitter", False),
            captcha_type=faucet_data.get("captcha_type", "image"),
            cooldown_hours=faucet_data.get("cooldown_hours", 24),
            selectors=faucet_data.get("selectors", {})
        )
    
    def get_all_faucets(self) -> List[str]:
        """获取所有faucet名称"""
        return list(self.config.get("faucets", {}).keys())
    
    def get_anti_detection_config(self) -> Dict:
        """获取反检测配置"""
        return self.config.get("anti_detection", {})
    
    def get_logging_config(self) -> Dict:
        """获取日志配置"""
        return self.config.get("logging", {})
    
    def update_config(self, section: str, key: str, value) -> bool:
        """更新配置"""
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value
            return self.save_config()
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False
    
    def add_faucet(self, faucet_name: str, faucet_config: FaucetConfig) -> bool:
        """添加新的faucet配置"""
        try:
            if "faucets" not in self.config:
                self.config["faucets"] = {}
            self.config["faucets"][faucet_name] = asdict(faucet_config)
            return self.save_config()
        except Exception as e:
            print(f"添加faucet配置失败: {e}")
            return False
    
    def get_default_config(self) -> 'Config':
        """获取默认配置"""
        return Config(
            faucet=FaucetConfig(),
            browser=BrowserConfig(),
            captcha=CaptchaConfig(),
            proxy=ProxyConfig()
        )

# 全局配置管理器实例
config_manager = ConfigManager()