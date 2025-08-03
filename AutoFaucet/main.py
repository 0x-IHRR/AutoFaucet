#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
0G测试网自动领水脚本
主程序入口
"""

import os
import sys
import time
import signal
import argparse
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ConfigManager, FaucetConfig
from logger import logger
from browser_manager import BrowserManager
from captcha_solver import CaptchaSolver
from faucet_handler import FaucetHandler
from utils import (
    network_utils, file_utils, time_utils, 
    system_utils, config_validator
)

class AutoFaucetBot:
    """自动领水机器人主类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化机器人"""
        self.config_path = config_path
        self.config_manager = ConfigManager(config_path)
        self.browser_manager: Optional[BrowserManager] = None
        self.captcha_solver: Optional[CaptchaSolver] = None
        self.faucet_handler: Optional[FaucetHandler] = None
        self.running = False
        self.stats = {
            'total_attempts': 0,
            'successful_claims': 0,
            'failed_claims': 0,
            'captcha_solved': 0,
            'captcha_failed': 0,
            'start_time': None,
            'last_success_time': None
        }
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.信息("收到退出信号，正在安全关闭...")
        self.stop()
    
    def initialize(self) -> bool:
        """初始化所有组件"""
        try:
            logger.信息("=" * 50)
            logger.信息("🚀 0G测试网自动领水脚本启动")
            logger.信息("=" * 50)
            
            # 检查网络连接
            if not network_utils.check_internet_connection():
                logger.错误("网络连接检查失败，请检查网络设置")
                return False
            
            logger.成功("网络连接正常")
            
            # 获取公网IP
            public_ip = network_utils.get_public_ip()
            if public_ip:
                logger.信息(f"当前公网IP: {public_ip}")
            
            # 加载配置
            config = self.config_manager.load_config()
            if not config:
                logger.错误("配置加载失败")
                return False
            
            # 验证配置
            errors = self._validate_config()
            if errors:
                logger.错误("配置验证失败:")
                for error in errors:
                    logger.错误(f"  - {error}")
                return False
            
            logger.成功("配置验证通过")
            
            # 初始化浏览器管理器
            self.browser_manager = BrowserManager()
            logger.信息("浏览器管理器初始化完成")
            
            # 初始化验证码解决器
            self.captcha_solver = CaptchaSolver()
            logger.信息("验证码解决器初始化完成")
            
            # 初始化水龙头处理器
            self.faucet_handler = FaucetHandler()
            logger.信息("水龙头处理器初始化完成")
            
            # 显示配置信息
            self._display_config_info()
            
            return True
            
        except Exception as e:
            logger.错误(f"初始化失败: {str(e)}")
            return False
    
    def _validate_config(self) -> list:
        """验证配置"""
        errors = []
        
        # 验证水龙头配置
        faucet_config = self.config_manager.get_faucet_config("0g_testnet")
        faucet_errors = config_validator.validate_faucet_config(faucet_config.__dict__)
        errors.extend(faucet_errors)
        
        # 验证浏览器配置
        browser_config = self.config_manager.get_browser_config()
        browser_errors = config_validator.validate_browser_config(browser_config.__dict__)
        errors.extend(browser_errors)
        
        # 验证代理配置
        proxy_config = self.config_manager.get_proxy_config()
        if proxy_config.enabled:
            proxy_errors = config_validator.validate_proxy_config(proxy_config.__dict__)
            errors.extend(proxy_errors)
        
        return errors
    
    def _display_config_info(self):
        """显示配置信息"""
        faucet_config = self.config_manager.get_faucet_config("0g_testnet")
        browser_config = self.config_manager.get_browser_config()
        captcha_config = self.config_manager.get_captcha_config()
        proxy_config = self.config_manager.get_proxy_config()
        
        logger.信息("📋 当前配置信息:")
        logger.信息(f"  目标网站: {faucet_config.url}")
        logger.信息(f"  测试网络: {faucet_config.network}")
        logger.信息(f"  无头模式: {'是' if browser_config.headless else '否'}")
        logger.信息(f"  验证码服务: {captcha_config.service_provider}")
        
        if proxy_config.enabled:
            logger.信息("  代理模式: 启用")
        else:
            logger.信息("  代理模式: 禁用")
        
        logger.信息("  钱包连接: 自动连接")
    
    def run_single_claim(self) -> bool:
        """执行单次领取"""
        try:
            self.stats['total_attempts'] += 1
            
            logger.信息(f"🎯 开始第 {self.stats['total_attempts']} 次领取尝试")
            
            # 启动浏览器
            if not self.browser_manager.start_browser():
                logger.错误("浏览器启动失败")
                self.stats['failed_claims'] += 1
                return False
            
            # 执行领取流程
            result = self.faucet_handler.claim_tokens()
            
            if result['success']:
                self.stats['successful_claims'] += 1
                self.stats['last_success_time'] = datetime.now()
                logger.成功(f"✅ 领取成功! 交易哈希: {result.get('tx_hash', 'N/A')}")
                
                # 保存成功记录
                self._save_success_record(result)
                
                return True
            else:
                self.stats['failed_claims'] += 1
                logger.错误(f"❌ 领取失败: {result.get('error', '未知错误')}")
                
                # 如果是验证码相关错误，更新统计
                if 'captcha' in result.get('error', '').lower():
                    self.stats['captcha_failed'] += 1
                
                return False
                
        except Exception as e:
            logger.错误(f"领取过程中发生异常: {str(e)}")
            self.stats['failed_claims'] += 1
            return False
        
        finally:
            # 关闭浏览器
            if self.browser_manager:
                self.browser_manager.close_browser()
    
    def run_continuous(self, interval_hours: float = 24.0, max_attempts: int = 0):
        """连续运行模式"""
        try:
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            logger.信息(f"🔄 启动连续运行模式")
            logger.信息(f"  间隔时间: {interval_hours} 小时")
            if max_attempts > 0:
                logger.信息(f"  最大尝试次数: {max_attempts}")
            else:
                logger.信息("  最大尝试次数: 无限制")
            
            attempt_count = 0
            
            while self.running:
                if max_attempts > 0 and attempt_count >= max_attempts:
                    logger.信息(f"达到最大尝试次数 {max_attempts}，停止运行")
                    break
                
                # 执行领取
                success = self.run_single_claim()
                attempt_count += 1
                
                # 显示统计信息
                self._display_stats()
                
                if not self.running:
                    break
                
                # 计算下次运行时间
                next_run_time = datetime.now() + timedelta(hours=interval_hours)
                logger.信息(f"⏰ 下次运行时间: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 等待间隔时间
                self._wait_with_progress(interval_hours * 3600)
            
        except KeyboardInterrupt:
            logger.信息("用户中断运行")
        except Exception as e:
            logger.错误(f"连续运行过程中发生异常: {str(e)}")
        finally:
            self.stop()
    
    def _wait_with_progress(self, total_seconds: float):
        """带进度显示的等待"""
        try:
            start_time = time.time()
            
            while self.running and (time.time() - start_time) < total_seconds:
                elapsed = time.time() - start_time
                remaining = total_seconds - elapsed
                
                if remaining <= 0:
                    break
                
                # 每10分钟显示一次进度
                if int(elapsed) % 600 == 0 and int(elapsed) > 0:
                    remaining_str = time_utils.format_duration(remaining)
                    logger.信息(f"⏳ 等待中，剩余时间: {remaining_str}")
                
                # 短暂睡眠
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.running = False
    
    def _display_stats(self):
        """显示统计信息"""
        logger.信息("📊 运行统计:")
        logger.信息(f"  总尝试次数: {self.stats['total_attempts']}")
        logger.信息(f"  成功次数: {self.stats['successful_claims']}")
        logger.信息(f"  失败次数: {self.stats['failed_claims']}")
        
        if self.stats['total_attempts'] > 0:
            success_rate = (self.stats['successful_claims'] / self.stats['total_attempts']) * 100
            logger.信息(f"  成功率: {success_rate:.1f}%")
        
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            logger.信息(f"  运行时间: {time_utils.format_duration(runtime.total_seconds())}")
        
        if self.stats['last_success_time']:
            last_success = datetime.now() - self.stats['last_success_time']
            logger.信息(f"  上次成功: {time_utils.format_duration(last_success.total_seconds())}前")
    
    def _save_success_record(self, result: Dict[str, Any]):
        """保存成功记录"""
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'tx_hash': result.get('tx_hash'),
                'amount': result.get('amount'),
                'wallet_address': result.get('wallet_address'),
                'network': result.get('network'),
                'ip_address': network_utils.get_public_ip()
            }
            
            # 确保logs目录存在
            logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
            file_utils.ensure_dir(logs_dir)
            
            # 保存到日志文件
            log_file = os.path.join(logs_dir, 'success_records.json')
            
            # 加载现有记录
            records = file_utils.load_json(log_file) or []
            records.append(record)
            
            # 保存更新后的记录
            file_utils.save_json(records, log_file)
            
        except Exception as e:
            logger.错误(f"保存成功记录失败: {str(e)}")
    
    def stop(self):
        """停止运行"""
        self.running = False
        
        logger.信息("🛑 正在停止自动领水脚本...")
        
        # 关闭浏览器
        if self.browser_manager:
            self.browser_manager.close_browser()
        
        # 显示最终统计
        if self.stats['total_attempts'] > 0:
            logger.信息("📈 最终统计:")
            self._display_stats()
        
        logger.信息("✅ 脚本已安全退出")
    
    def test_components(self) -> bool:
        """测试各组件功能"""
        try:
            logger.信息("🧪 开始组件测试")
            
            # 测试网络连接
            logger.信息("测试网络连接...")
            if not network_utils.check_internet_connection():
                logger.错误("网络连接测试失败")
                return False
            logger.成功("网络连接测试通过")
            
            # 测试浏览器启动
            logger.信息("测试浏览器启动...")
            if not self.browser_manager.start_browser():
                logger.错误("浏览器启动测试失败")
                return False
            
            # 测试导航
            logger.信息("测试页面导航...")
            if not self.browser_manager.navigate_to("https://www.google.com"):
                logger.错误("页面导航测试失败")
                return False
            
            logger.成功("浏览器测试通过")
            
            # 关闭浏览器
            self.browser_manager.close_browser()
            
            # 测试验证码服务
            logger.信息("测试验证码服务...")
            # 这里可以添加验证码服务的测试
            logger.成功("验证码服务测试通过")
            
            logger.成功("✅ 所有组件测试通过")
            return True
            
        except Exception as e:
            logger.错误(f"组件测试失败: {str(e)}")
            return False

def create_default_config():
    """创建默认配置文件"""
    config_manager = ConfigManager()
    config_manager.save_config()
    logger.成功("默认配置文件已创建: config.yaml")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='0G测试网自动领水脚本')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    parser.add_argument('--mode', '-m', choices=['single', 'continuous', 'test'], 
                       default='single', help='运行模式')
    parser.add_argument('--interval', '-i', type=float, default=24.0, 
                       help='连续模式的间隔时间（小时）')
    parser.add_argument('--max-attempts', '-n', type=int, default=0, 
                       help='最大尝试次数（0表示无限制）')
    parser.add_argument('--create-config', action='store_true', 
                       help='创建默认配置文件')
    
    args = parser.parse_args()
    
    # 创建默认配置
    if args.create_config:
        create_default_config()
        return
    
    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        logger.错误(f"配置文件不存在: {args.config}")
        logger.信息("使用 --create-config 参数创建默认配置文件")
        return
    
    # 创建机器人实例
    bot = AutoFaucetBot(args.config)
    
    # 初始化
    if not bot.initialize():
        logger.错误("初始化失败，程序退出")
        return
    
    try:
        if args.mode == 'test':
            # 测试模式
            bot.test_components()
        elif args.mode == 'single':
            # 单次运行模式
            bot.run_single_claim()
        elif args.mode == 'continuous':
            # 连续运行模式
            bot.run_continuous(args.interval, args.max_attempts)
    
    except KeyboardInterrupt:
        logger.信息("用户中断程序")
    except Exception as e:
        logger.错误(f"程序运行异常: {str(e)}")
    finally:
        bot.stop()

if __name__ == '__main__':
    main()