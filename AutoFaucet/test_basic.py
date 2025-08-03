#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础功能测试脚本
用于验证各个模块是否正常工作
"""

import os
import sys
import time
from typing import Dict, Any

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import logger
from config import ConfigManager
from utils import network_utils, file_utils, validation_utils
from browser_manager import BrowserManager
from captcha_solver import CaptchaSolver

class BasicTester:
    """基础功能测试器"""
    
    def __init__(self):
        self.test_results = []
        self.config_manager = ConfigManager()
    
    def run_test(self, test_name: str, test_func) -> bool:
        """运行单个测试"""
        try:
            logger.信息(f"🧪 开始测试: {test_name}")
            start_time = time.time()
            
            result = test_func()
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result:
                logger.成功(f"✅ {test_name} - 通过 ({duration:.2f}秒)")
                self.test_results.append({
                    'name': test_name,
                    'status': 'PASS',
                    'duration': duration,
                    'error': None
                })
                return True
            else:
                logger.错误(f"❌ {test_name} - 失败 ({duration:.2f}秒)")
                self.test_results.append({
                    'name': test_name,
                    'status': 'FAIL',
                    'duration': duration,
                    'error': 'Test returned False'
                })
                return False
                
        except Exception as e:
            logger.错误(f"❌ {test_name} - 异常: {str(e)}")
            self.test_results.append({
                'name': test_name,
                'status': 'ERROR',
                'duration': 0,
                'error': str(e)
            })
            return False
    
    def test_imports(self) -> bool:
        """测试模块导入"""
        try:
            # 测试所有主要模块的导入
            import config
            from logger import logger as log_instance
            import browser_manager
            import captcha_solver
            import faucet_handler
            import utils
            
            log_instance.信息("所有模块导入成功")
            return True
            
        except ImportError as e:
            logger.错误(f"模块导入失败: {str(e)}")
            return False
    
    def test_network_utils(self) -> bool:
        """测试网络工具"""
        try:
            # 测试网络连接
            if not network_utils.check_internet_connection():
                logger.错误("网络连接检查失败")
                return False
            
            # 测试获取公网IP
            public_ip = network_utils.get_public_ip()
            if not public_ip:
                logger.警告("无法获取公网IP")
            else:
                logger.信息(f"当前公网IP: {public_ip}")
            
            # 测试URL验证
            test_urls = [
                ("https://www.google.com", True),
                ("invalid-url", False),
                ("http://example.com", True),
                ("not-a-url", False)
            ]
            
            for url, expected in test_urls:
                result = validation_utils.validate_url(url)
                if result != expected:
                    logger.错误(f"URL验证失败: {url} 期望 {expected}, 得到 {result}")
                    return False
            
            logger.信息("网络工具测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"网络工具测试失败: {str(e)}")
            return False
    
    def test_file_utils(self) -> bool:
        """测试文件工具"""
        try:
            test_dir = os.path.join(os.path.dirname(__file__), 'test_temp')
            test_file = os.path.join(test_dir, 'test.json')
            
            # 测试目录创建
            if not file_utils.ensure_dir(test_dir):
                logger.错误("目录创建失败")
                return False
            
            # 测试JSON文件保存和加载
            test_data = {
                'test': True,
                'number': 123,
                'array': [1, 2, 3],
                'chinese': '测试中文'
            }
            
            if not file_utils.save_json(test_data, test_file):
                logger.错误("JSON文件保存失败")
                return False
            
            loaded_data = file_utils.load_json(test_file)
            if loaded_data != test_data:
                logger.错误("JSON文件加载数据不匹配")
                return False
            
            # 清理测试文件
            file_utils.delete_file(test_file)
            os.rmdir(test_dir)
            
            logger.信息("文件工具测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"文件工具测试失败: {str(e)}")
            return False
    
    def test_config_manager(self) -> bool:
        """测试配置管理器"""
        try:
            # 测试默认配置生成
            default_config = self.config_manager.get_default_config()
            if not default_config:
                logger.错误("默认配置生成失败")
                return False
            
            # 验证配置结构
            required_sections = ['faucet', 'browser', 'captcha', 'proxy']
            for section in required_sections:
                if not hasattr(default_config, section):
                    logger.错误(f"配置缺少必需部分: {section}")
                    return False
            
            # 测试配置保存和加载
            if not self.config_manager.save_config():
                logger.错误("配置保存失败")
                return False
            
            loaded_config = self.config_manager.load_config()
            if not loaded_config:
                logger.错误("配置加载失败")
                return False
            
            logger.信息("配置管理器测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"配置管理器测试失败: {str(e)}")
            return False
    
    def test_browser_manager_init(self) -> bool:
        """测试浏览器管理器初始化"""
        try:
            # 创建浏览器管理器实例
            browser_manager = BrowserManager()
            
            if not browser_manager:
                logger.错误("浏览器管理器创建失败")
                return False
            
            logger.信息("浏览器管理器初始化测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"浏览器管理器初始化测试失败: {str(e)}")
            return False
    
    def test_captcha_solver_init(self) -> bool:
        """测试验证码解决器初始化"""
        try:
            # 创建验证码解决器实例
            captcha_solver = CaptchaSolver()
            
            if not captcha_solver:
                logger.错误("验证码解决器创建失败")
                return False
            
            logger.信息("验证码解决器初始化测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"验证码解决器初始化测试失败: {str(e)}")
            return False
    
    def test_validation_utils(self) -> bool:
        """测试验证工具"""
        try:
            # 测试以太坊地址验证
            test_addresses = [
                ("0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b", False),  # 长度不对
                ("0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b9", True),   # 正确格式
                ("742d35Cc6634C0532925a3b8D4C9db96C4b4d8b9", False),    # 缺少0x
                ("0xGGGd35Cc6634C0532925a3b8D4C9db96C4b4d8b9", False),   # 非十六进制
            ]
            
            for address, expected in test_addresses:
                result = validation_utils.is_valid_ethereum_address(address)
                if result != expected:
                    logger.错误(f"以太坊地址验证失败: {address} 期望 {expected}, 得到 {result}")
                    return False
            
            # 测试代理格式验证
            test_proxies = [
                ("127.0.0.1:8080", True),
                ("http://127.0.0.1:8080", True),
                ("socks5://127.0.0.1:1080", True),
                ("invalid-proxy", False),
                ("127.0.0.1", False),  # 缺少端口
            ]
            
            for proxy, expected in test_proxies:
                result = validation_utils.validate_proxy_format(proxy)
                if result != expected:
                    logger.错误(f"代理格式验证失败: {proxy} 期望 {expected}, 得到 {result}")
                    return False
            
            logger.信息("验证工具测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"验证工具测试失败: {str(e)}")
            return False
    
    def test_logger(self) -> bool:
        """测试日志功能"""
        try:
            # 测试各种日志级别
            logger.调试("这是调试信息")
            logger.信息("这是普通信息")
            logger.警告("这是警告信息")
            logger.错误("这是错误信息")
            logger.成功("这是成功信息")
            
            # 测试操作日志
            logger.开始操作("测试操作")
            time.sleep(0.1)
            logger.完成操作("测试操作")
            
            logger.步骤("执行测试步骤")
            logger.等待("等待测试完成")
            logger.点击("测试按钮")
            logger.输入("测试输入框", "测试内容")
            
            logger.信息("日志功能测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"日志功能测试失败: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.信息("=" * 50)
        logger.信息("🚀 开始基础功能测试")
        logger.信息("=" * 50)
        
        # 定义测试列表
        tests = [
            ("模块导入", self.test_imports),
            ("日志功能", self.test_logger),
            ("网络工具", self.test_network_utils),
            ("文件工具", self.test_file_utils),
            ("验证工具", self.test_validation_utils),
            ("配置管理器", self.test_config_manager),
            ("浏览器管理器初始化", self.test_browser_manager_init),
            ("验证码解决器初始化", self.test_captcha_solver_init),
        ]
        
        # 运行所有测试
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
            else:
                failed += 1
        
        # 显示测试结果
        logger.信息("=" * 50)
        logger.信息("📊 测试结果汇总")
        logger.信息("=" * 50)
        
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.信息(f"总测试数: {total}")
        logger.信息(f"通过: {passed}")
        logger.信息(f"失败: {failed}")
        logger.信息(f"成功率: {success_rate:.1f}%")
        
        if failed == 0:
            logger.成功("🎉 所有测试通过!")
        else:
            logger.错误(f"❌ {failed} 个测试失败")
            
            # 显示失败的测试详情
            logger.信息("\n失败测试详情:")
            for result in self.test_results:
                if result['status'] != 'PASS':
                    logger.错误(f"  - {result['name']}: {result['error']}")
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'results': self.test_results
        }

def main():
    """主函数"""
    tester = BasicTester()
    results = tester.run_all_tests()
    
    # 返回适当的退出码
    if results['failed'] == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()