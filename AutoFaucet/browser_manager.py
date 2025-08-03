# -*- coding: utf-8 -*-
"""
浏览器管理模块
提供反检测的浏览器自动化功能，重点关注IP伪装和反封锁
"""

import random
import time
import json
import os
from typing import Optional, Dict, List, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from config import config_manager
from logger import logger

class BrowserManager:
    """浏览器管理器 - 专注反检测和IP伪装"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.config = config_manager.get_browser_config()
        self.proxy_config = config_manager.get_proxy_config()
        self.ua = UserAgent()
        
        # 反检测配置
        self.stealth_config = {
            'user_agent_rotation': True,
            'viewport_randomization': True,
            'timing_randomization': True,
            'mouse_movement_simulation': True,
            'keyboard_simulation': True
        }
        
        logger.信息("浏览器管理器初始化完成")
    
    def start_browser(self, headless: bool = False, proxy: Optional[str] = None) -> bool:
        """启动浏览器"""
        try:
            logger.开始操作("启动浏览器")
            
            # 配置Chrome选项
            options = self._get_chrome_options(headless, proxy)
            
            # 首先尝试使用undetected-chromedriver
            try:
                self.driver = uc.Chrome(
                    options=options,
                    version_main=None,  # 自动检测Chrome版本
                    driver_executable_path=None,  # 自动下载驱动
                    browser_executable_path=None,  # 使用系统Chrome
                    suppress_welcome=True,
                    use_subprocess=False,  # 改为False避免崩溃
                    debug=False
                )
                logger.反检测("使用undetected-chromedriver启动成功")
            except Exception as uc_error:
                logger.警告(f"undetected-chromedriver启动失败: {str(uc_error)}")
                logger.反检测("回退到标准selenium webdriver")
                
                # 回退到标准selenium webdriver
                # 转换选项格式
                standard_options = ChromeOptions()
                for arg in options.arguments:
                    standard_options.add_argument(arg)
                
                # 复制实验性选项
                for key, value in options.experimental_options.items():
                    if key != 'excludeSwitches':  # 跳过不兼容的选项
                        standard_options.add_experimental_option(key, value)
                
                # 使用webdriver-manager自动管理chromedriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=standard_options)
                logger.反检测("标准selenium webdriver启动成功")
            
            # 设置等待器
            self.wait = WebDriverWait(self.driver, self.config.page_load_timeout)
            
            # 应用反检测措施
            self._apply_stealth_measures()
            
            # 设置窗口大小（随机化）
            self._set_random_viewport()
            
            logger.完成操作("启动浏览器", "成功")
            return True
            
        except Exception as e:
            logger.错误(f"启动浏览器失败: {str(e)}")
            return False
    
    def _get_chrome_options(self, headless: bool, proxy: Optional[str]) -> uc.ChromeOptions:
        """获取Chrome选项配置"""
        options = uc.ChromeOptions()
        
        # 基础反检测选项
        anti_detection_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images',  # 禁用图片加载以提高速度
            '--disable-javascript',  # 可选：禁用JS（某些情况下）
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-default-apps',
            '--disable-component-extensions-with-background-pages',
            '--no-default-browser-check',
            '--no-first-run',
            '--no-pings',
            '--password-store=basic',
            '--use-mock-keychain',
            '--disable-component-update',
            '--disable-domain-reliability',
            '--disable-features=UserAgentClientHint'
        ]
        
        for arg in anti_detection_args:
            options.add_argument(arg)
        
        # 设置用户代理
        user_agent = self._get_random_user_agent()
        options.add_argument(f'--user-agent={user_agent}')
        logger.反检测("设置随机User-Agent", user_agent[:50] + "...")
        
        # 代理设置
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            logger.代理("设置代理", proxy)
        
        # 无头模式
        if headless:
            options.add_argument('--headless')
            logger.反检测("启用无头模式")
        
        # 设置首选项
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2,  # 禁用通知
                'media_stream': 2,   # 禁用媒体流
                'geolocation': 2,    # 禁用地理位置
            },
            'profile.managed_default_content_settings': {
                'images': 2  # 禁用图片
            },
            'profile.default_content_settings': {
                'popups': 0  # 允许弹窗（钱包连接需要）
            }
        }
        options.add_experimental_option('prefs', prefs)
        
        # 排除自动化标识 (移除excludeSwitches以兼容新版Chrome)
        options.add_experimental_option('useAutomationExtension', False)
        # 添加其他反检测措施
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        return options
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        try:
            # 优先使用Chrome User-Agent
            ua = self.ua.chrome
            return ua
        except:
            # 备用User-Agent列表
            backup_uas = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            return random.choice(backup_uas)
    
    def _get_user_data_dir(self) -> str:
        """获取用户数据目录"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='chrome_profile_')
        logger.反检测("创建临时用户数据目录", temp_dir)
        return temp_dir
    
    def _apply_stealth_measures(self):
        """应用反检测措施"""
        try:
            # 移除webdriver属性
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # 修改Chrome对象
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})"
            )
            
            # 修改语言设置
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en', 'zh-CN', 'zh']})"
            )
            
            # 设置权限
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})"
            )
            
            logger.反检测("应用JavaScript反检测措施")
            
        except Exception as e:
            logger.警告(f"应用反检测措施时出错: {str(e)}")
    
    def _set_random_viewport(self):
        """设置随机视口大小"""
        try:
            # 常见的屏幕分辨率
            resolutions = [
                (1920, 1080), (1366, 768), (1440, 900),
                (1536, 864), (1280, 720), (1600, 900)
            ]
            
            width, height = random.choice(resolutions)
            self.driver.set_window_size(width, height)
            
            # 随机位置
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            self.driver.set_window_position(x, y)
            
            logger.反检测(f"设置随机视口", f"{width}x{height} at ({x},{y})")
            
        except Exception as e:
            logger.警告(f"设置随机视口失败: {str(e)}")
    
    def navigate_to(self, url: str, wait_time: float = None) -> bool:
        """导航到指定URL"""
        try:
            logger.导航(url)
            
            # 随机等待时间
            if wait_time is None:
                wait_time = random.uniform(2, 5)
            
            self.driver.get(url)
            
            # 等待页面加载
            self.random_wait(wait_time)
            
            # 检查页面是否正确加载
            if self.driver.current_url != url:
                logger.警告(f"页面重定向: {self.driver.current_url}")
            
            logger.完成操作("页面导航", "成功")
            return True
            
        except Exception as e:
            logger.错误(f"导航失败: {str(e)}")
            return False
    
    def find_element_safe(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """安全查找元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logger.检测(f"元素 {value}", "找到")
            return element
        except TimeoutException:
            logger.检测(f"元素 {value}", "未找到")
            return None
    
    def click_element_safe(self, by: By, value: str, timeout: int = 10) -> bool:
        """安全点击元素"""
        try:
            element = self.find_element_safe(by, value, timeout)
            if element:
                # 模拟人类点击行为
                self._human_like_click(element)
                logger.点击(value)
                return True
            return False
        except Exception as e:
            logger.错误(f"点击元素失败 {value}: {str(e)}")
            return False
    
    def _human_like_click(self, element):
        """模拟人类点击行为"""
        try:
            # 滚动到元素可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.random_wait(0.5, 1.5)
            
            # 移动鼠标到元素
            ActionChains(self.driver).move_to_element(element).perform()
            self.random_wait(0.2, 0.8)
            
            # 点击
            element.click()
            self.random_wait(0.5, 1.5)
            
        except Exception as e:
            logger.警告(f"人类化点击失败，使用普通点击: {str(e)}")
            element.click()
    
    def input_text_safe(self, by: By, value: str, text: str, timeout: int = 10) -> bool:
        """安全输入文本"""
        try:
            element = self.find_element_safe(by, value, timeout)
            if element:
                # 清空输入框
                element.clear()
                self.random_wait(0.5, 1.0)
                
                # 模拟人类输入
                self._human_like_input(element, text)
                logger.输入(value, "***" if "password" in value.lower() else text[:20])
                return True
            return False
        except Exception as e:
            logger.错误(f"输入文本失败 {value}: {str(e)}")
            return False
    
    def _human_like_input(self, element, text: str):
        """模拟人类输入行为"""
        try:
            # 逐字符输入
            for char in text:
                element.send_keys(char)
                # 随机输入间隔
                time.sleep(random.uniform(0.05, 0.2))
        except Exception as e:
            logger.警告(f"人类化输入失败，使用普通输入: {str(e)}")
            element.send_keys(text)
    
    def wait_for_element(self, by: By, value: str, timeout: int = 30) -> bool:
        """等待元素出现"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logger.检测(f"等待元素 {value}", "出现")
            return True
        except TimeoutException:
            logger.检测(f"等待元素 {value}", "超时")
            return False
    
    def random_wait(self, min_time: float = 1.0, max_time: float = 3.0):
        """随机等待"""
        wait_time = random.uniform(min_time, max_time)
        logger.等待("随机延迟", wait_time)
        time.sleep(wait_time)
    
    def simulate_human_behavior(self):
        """模拟人类行为"""
        try:
            # 随机滚动
            scroll_actions = [
                "window.scrollBy(0, 100);",
                "window.scrollBy(0, -50);",
                "window.scrollBy(0, 200);"
            ]
            
            action = random.choice(scroll_actions)
            self.driver.execute_script(action)
            
            # 随机鼠标移动
            body = self.driver.find_element(By.TAG_NAME, "body")
            ActionChains(self.driver).move_to_element_with_offset(
                body, random.randint(100, 500), random.randint(100, 400)
            ).perform()
            
            self.random_wait(1, 3)
            logger.反检测("模拟人类行为")
            
        except Exception as e:
            logger.警告(f"模拟人类行为失败: {str(e)}")
    
    def take_screenshot(self, filename: str = None) -> str:
        """截图"""
        try:
            if filename is None:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            # 确保截图目录存在
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            filepath = os.path.join(screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            
            logger.信息(f"截图保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.错误(f"截图失败: {str(e)}")
            return ""
    
    def get_page_source(self) -> str:
        """获取页面源码"""
        try:
            return self.driver.page_source
        except Exception as e:
            logger.错误(f"获取页面源码失败: {str(e)}")
            return ""
    
    def execute_script(self, script: str) -> Any:
        """执行JavaScript"""
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            logger.错误(f"执行脚本失败: {str(e)}")
            return None
    
    def switch_to_window(self, window_handle: str):
        """切换窗口"""
        try:
            self.driver.switch_to.window(window_handle)
            logger.步骤("切换窗口", window_handle[:10])
        except Exception as e:
            logger.错误(f"切换窗口失败: {str(e)}")
    
    def get_current_url(self) -> str:
        """获取当前URL"""
        try:
            return self.driver.current_url
        except Exception as e:
            logger.错误(f"获取当前URL失败: {str(e)}")
            return ""
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.driver:
                self.driver.quit()
                logger.完成操作("关闭浏览器", "成功")
        except Exception as e:
            logger.错误(f"关闭浏览器失败: {str(e)}")
        finally:
            self.driver = None
            self.wait = None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close_browser()

# 导出
__all__ = ['BrowserManager']