# -*- coding: utf-8 -*-
"""
水龙头处理模块
专门处理0G测试网水龙头的领取流程
"""

import time
import random
from typing import Optional, Dict, List, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import config_manager
from logger import logger
from browser_manager import BrowserManager
from captcha_solver import CaptchaSolver

class FaucetHandler:
    """0G测试网水龙头处理器"""
    
    def __init__(self):
        self.config = config_manager.get_faucet_config("0g_testnet")
        self.browser = None
        self.captcha_solver = CaptchaSolver()
        self.current_step = "初始化"
        
        # 0G水龙头特定配置
        self.faucet_url = "https://hub.0g.ai/faucet"
        self.network_name = "0G Testnet"
        
        # 常用选择器
        self.selectors = {
            'twitter_link': 'a[href*="twitter.com"], a[href*="x.com"]',
            'connect_wallet': 'button[class*="connect"], button[class*="wallet"], [id*="connect"]',
            'wallet_address_input': 'input[placeholder*="address"], input[name*="address"], input[id*="address"]',
            'captcha_image': 'img[src*="captcha"], img[src*="verify"], img[src*="code"]',
            'captcha_input': 'input[name*="captcha"], input[id*="captcha"], input[placeholder*="captcha"]',
            'submit_button': 'button[type="submit"], button[class*="submit"], input[type="submit"]',
            'claim_button': 'button[class*="claim"], button[class*="faucet"], [id*="claim"]',
            'success_message': '[class*="success"], [class*="complete"], [id*="success"]',
            'error_message': '[class*="error"], [class*="fail"], [id*="error"]'
        }
        
        logger.信息("0G水龙头处理器初始化完成")
    
    def start_claim_process(self, wallet_address: str = None, use_proxy: bool = True) -> bool:
        """开始领取流程"""
        try:
            logger.开始操作("0G测试网代币领取")
            
            # 初始化浏览器
            self.browser = BrowserManager()
            
            # 选择代理
            proxy = None
            if use_proxy:
                proxy = self._get_random_proxy()
            
            # 启动浏览器
            if not self.browser.start_browser(headless=False, proxy=proxy):
                logger.错误("浏览器启动失败")
                return False
            
            # 执行领取流程
            success = self._execute_claim_flow(wallet_address)
            
            if success:
                logger.完成操作("代币领取", "成功")
            else:
                logger.完成操作("代币领取", "失败")
            
            return success
            
        except Exception as e:
            logger.异常(f"领取流程异常: {str(e)}")
            return False
        finally:
            self._cleanup()
    
    def _execute_claim_flow(self, wallet_address: str) -> bool:
        """执行完整的领取流程"""
        try:
            # 步骤1: 访问水龙头页面
            if not self._navigate_to_faucet():
                return False
            
            # 步骤2: 处理Twitter跳转
            if not self._handle_twitter_redirect():
                return False
            
            # 步骤3: 连接钱包或输入地址
            if not self._handle_wallet_connection(wallet_address):
                return False
            
            # 步骤4: 处理验证码
            if not self._handle_captcha():
                return False
            
            # 步骤5: 提交领取请求
            if not self._submit_claim_request():
                return False
            
            # 步骤6: 验证结果
            return self._verify_claim_result()
            
        except Exception as e:
            logger.异常(f"执行领取流程失败: {str(e)}")
            return False
    
    def _navigate_to_faucet(self) -> bool:
        """导航到水龙头页面"""
        try:
            self.current_step = "访问水龙头页面"
            logger.步骤(self.current_step)
            
            # 访问页面
            if not self.browser.navigate_to(self.faucet_url):
                return False
            
            # 等待页面加载
            self.browser.random_wait(3, 6)
            
            # 检查页面是否正确加载
            current_url = self.browser.get_current_url()
            if "0g.ai" not in current_url.lower():
                logger.错误(f"页面加载异常，当前URL: {current_url}")
                return False
            
            # 模拟人类行为
            self.browser.simulate_human_behavior()
            
            logger.完成操作("页面访问", "成功")
            return True
            
        except Exception as e:
            logger.错误(f"访问水龙头页面失败: {str(e)}")
            return False
    
    def _handle_twitter_redirect(self) -> bool:
        """处理Twitter跳转链接"""
        try:
            self.current_step = "处理Twitter跳转"
            logger.步骤(self.current_step)
            
            # 查找Twitter链接
            twitter_link = self.browser.find_element_safe(
                By.CSS_SELECTOR, self.selectors['twitter_link'], timeout=10
            )
            
            if not twitter_link:
                logger.警告("未找到Twitter链接，尝试其他方式")
                # 尝试查找包含twitter或x.com的链接
                all_links = self.browser.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    href = link.get_attribute("href") or ""
                    if "twitter.com" in href or "x.com" in href:
                        twitter_link = link
                        break
            
            if twitter_link:
                # 记录当前窗口
                original_window = self.browser.driver.current_window_handle
                
                # 点击Twitter链接
                logger.点击("Twitter链接")
                self.browser._human_like_click(twitter_link)
                
                # 等待新窗口打开
                self.browser.random_wait(3, 5)
                
                # 检查是否有新窗口
                all_windows = self.browser.driver.window_handles
                if len(all_windows) > 1:
                    # 切换到新窗口
                    for window in all_windows:
                        if window != original_window:
                            self.browser.switch_to_window(window)
                            break
                    
                    # 在Twitter页面停留一段时间
                    logger.等待("Twitter页面停留", 5)
                    self.browser.random_wait(3, 8)
                    
                    # 关闭Twitter窗口并返回原窗口
                    self.browser.driver.close()
                    self.browser.switch_to_window(original_window)
                    
                    logger.完成操作("Twitter跳转", "成功")
                else:
                    # 如果没有新窗口，可能是在当前窗口打开
                    logger.信息("Twitter链接在当前窗口打开")
                    self.browser.random_wait(3, 5)
                    
                    # 返回水龙头页面
                    self.browser.navigate_to(self.faucet_url)
                    
                return True
            else:
                logger.警告("未找到Twitter链接，继续后续流程")
                return True
                
        except Exception as e:
            logger.错误(f"处理Twitter跳转失败: {str(e)}")
            # Twitter跳转失败不应该阻止整个流程
            return True
    
    def _handle_wallet_connection(self, wallet_address: str) -> bool:
        """处理钱包连接"""
        try:
            self.current_step = "连接钱包"
            logger.步骤(self.current_step)
            
            # 等待页面稳定
            self.browser.random_wait(2, 4)
            
            # 方法1: 尝试连接钱包按钮
            connect_button = self.browser.find_element_safe(
                By.CSS_SELECTOR, self.selectors['connect_wallet'], timeout=10
            )
            
            if connect_button:
                logger.钱包("发现连接钱包按钮")
                self.browser._human_like_click(connect_button)
                
                # 等待钱包弹窗
                self.browser.random_wait(3, 6)
                
                # 这里可以添加具体的钱包连接逻辑
                # 例如MetaMask的处理
                if self._handle_metamask_connection():
                    logger.钱包("钱包连接成功")
                    return True
            
            # 方法2: 尝试直接输入钱包地址
            address_input = self.browser.find_element_safe(
                By.CSS_SELECTOR, self.selectors['wallet_address_input'], timeout=5
            )
            
            if address_input and wallet_address:
                logger.钱包("发现地址输入框")
                if self.browser.input_text_safe(
                    By.CSS_SELECTOR, self.selectors['wallet_address_input'], wallet_address
                ):
                    logger.钱包("地址输入成功", wallet_address)
                    return True
            
            # 如果都没有找到，尝试查找其他可能的元素
            logger.警告("未找到标准钱包连接方式，尝试其他方法")
            return self._try_alternative_wallet_methods(wallet_address)
            
        except Exception as e:
            logger.错误(f"钱包连接失败: {str(e)}")
            return False
    
    def _handle_metamask_connection(self) -> bool:
        """处理MetaMask连接"""
        try:
            # 检查是否有新窗口（MetaMask弹窗）
            original_window = self.browser.driver.current_window_handle
            all_windows = self.browser.driver.window_handles
            
            if len(all_windows) > 1:
                # 切换到MetaMask窗口
                for window in all_windows:
                    if window != original_window:
                        self.browser.switch_to_window(window)
                        
                        # 检查是否是MetaMask窗口
                        if "metamask" in self.browser.get_current_url().lower():
                            logger.钱包("检测到MetaMask窗口")
                            
                            # 查找连接按钮
                            connect_selectors = [
                                'button[data-testid="page-container-footer-next"]',
                                'button:contains("Connect")',
                                'button:contains("连接")',
                                '[class*="connect"]'
                            ]
                            
                            for selector in connect_selectors:
                                if self.browser.click_element_safe(By.CSS_SELECTOR, selector, timeout=3):
                                    logger.钱包("点击MetaMask连接按钮")
                                    self.browser.random_wait(2, 4)
                                    break
                            
                            # 返回原窗口
                            self.browser.switch_to_window(original_window)
                            return True
                        
                        # 如果不是MetaMask窗口，关闭它
                        self.browser.driver.close()
                        self.browser.switch_to_window(original_window)
            
            return False
            
        except Exception as e:
            logger.错误(f"MetaMask连接处理失败: {str(e)}")
            return False
    
    def _try_alternative_wallet_methods(self, wallet_address: str) -> bool:
        """尝试其他钱包连接方法"""
        try:
            # 查找所有可能的按钮和输入框
            buttons = self.browser.driver.find_elements(By.TAG_NAME, "button")
            inputs = self.browser.driver.find_elements(By.TAG_NAME, "input")
            
            # 查找包含钱包相关关键词的按钮
            wallet_keywords = ["wallet", "connect", "metamask", "钱包", "连接"]
            
            for button in buttons:
                text = (button.text or "").lower()
                if any(keyword in text for keyword in wallet_keywords):
                    logger.钱包(f"尝试点击按钮: {button.text}")
                    self.browser._human_like_click(button)
                    self.browser.random_wait(2, 4)
                    return True
            
            # 查找可能的地址输入框
            for input_elem in inputs:
                placeholder = (input_elem.get_attribute("placeholder") or "").lower()
                name = (input_elem.get_attribute("name") or "").lower()
                
                if any(keyword in placeholder + name for keyword in ["address", "wallet", "地址"]):
                    if wallet_address:
                        logger.钱包(f"尝试输入地址到: {placeholder or name}")
                        input_elem.clear()
                        input_elem.send_keys(wallet_address)
                        self.browser.random_wait(1, 2)
                        return True
            
            return False
            
        except Exception as e:
            logger.错误(f"其他钱包方法失败: {str(e)}")
            return False
    
    def _handle_captcha(self) -> bool:
        """处理验证码"""
        try:
            self.current_step = "处理验证码"
            logger.步骤(self.current_step)
            
            # 等待验证码出现
            if not self.captcha_solver.wait_for_captcha(self.browser.driver, timeout=15):
                logger.信息("未检测到验证码，继续流程")
                return True
            
            # 检测验证码类型
            captcha_type = self.captcha_solver.detect_captcha_type(self.browser.driver)
            logger.验证码("检测到验证码类型", captcha_type)
            
            if captcha_type == "image":
                return self._solve_image_captcha()
            elif captcha_type == "recaptcha_v2":
                return self._solve_recaptcha_v2()
            elif captcha_type == "hcaptcha":
                return self._solve_hcaptcha()
            else:
                logger.警告(f"未知验证码类型: {captcha_type}")
                return False
                
        except Exception as e:
            logger.错误(f"验证码处理失败: {str(e)}")
            return False
    
    def _solve_image_captcha(self) -> bool:
        """解决图片验证码"""
        try:
            logger.验证码("开始解决图片验证码")
            
            # 查找验证码图片
            captcha_img = self.browser.find_element_safe(
                By.CSS_SELECTOR, self.selectors['captcha_image'], timeout=10
            )
            
            if not captcha_img:
                logger.错误("未找到验证码图片")
                return False
            
            # 识别验证码
            result = self.captcha_solver.solve_image_captcha(
                image_element=captcha_img,
                driver=self.browser.driver
            )
            
            if not result:
                logger.错误("验证码识别失败")
                return False
            
            # 输入验证码
            captcha_input = self.browser.find_element_safe(
                By.CSS_SELECTOR, self.selectors['captcha_input'], timeout=5
            )
            
            if captcha_input:
                self.browser.input_text_safe(
                    By.CSS_SELECTOR, self.selectors['captcha_input'], result
                )
                logger.验证码("验证码输入完成", result)
                return True
            else:
                logger.错误("未找到验证码输入框")
                return False
                
        except Exception as e:
            logger.错误(f"图片验证码解决失败: {str(e)}")
            return False
    
    def _solve_recaptcha_v2(self) -> bool:
        """解决reCAPTCHA v2"""
        try:
            logger.验证码("开始解决reCAPTCHA v2")
            
            # 获取site key
            recaptcha_element = self.browser.driver.find_element(
                By.CLASS_NAME, "g-recaptcha"
            )
            site_key = recaptcha_element.get_attribute("data-sitekey")
            
            if not site_key:
                logger.错误("未找到reCAPTCHA site key")
                return False
            
            # 使用第三方服务解决
            result = self.captcha_solver.solve_recaptcha_v2(
                site_key, self.browser.get_current_url()
            )
            
            if result:
                # 注入解决结果
                self.browser.execute_script(
                    f'document.getElementById("g-recaptcha-response").innerHTML="{result}";'
                )
                logger.验证码("reCAPTCHA v2解决成功")
                return True
            
            return False
            
        except Exception as e:
            logger.错误(f"reCAPTCHA v2解决失败: {str(e)}")
            return False
    
    def _solve_hcaptcha(self) -> bool:
        """解决hCaptcha"""
        logger.验证码("hCaptcha暂不支持")
        return False
    
    def _submit_claim_request(self) -> bool:
        """提交领取请求"""
        try:
            self.current_step = "提交领取请求"
            logger.步骤(self.current_step)
            
            # 查找提交按钮
            submit_selectors = [
                self.selectors['submit_button'],
                self.selectors['claim_button'],
                'button:contains("Claim")',
                'button:contains("Submit")',
                'button:contains("领取")',
                'button:contains("提交")'
            ]
            
            for selector in submit_selectors:
                submit_button = self.browser.find_element_safe(
                    By.CSS_SELECTOR, selector, timeout=5
                )
                
                if submit_button:
                    logger.点击(f"提交按钮: {selector}")
                    self.browser._human_like_click(submit_button)
                    
                    # 等待提交处理
                    self.browser.random_wait(3, 8)
                    
                    logger.完成操作("请求提交", "成功")
                    return True
            
            logger.错误("未找到提交按钮")
            return False
            
        except Exception as e:
            logger.错误(f"提交请求失败: {str(e)}")
            return False
    
    def _verify_claim_result(self) -> bool:
        """验证领取结果"""
        try:
            self.current_step = "验证领取结果"
            logger.步骤(self.current_step)
            
            # 等待结果页面加载
            self.browser.random_wait(5, 10)
            
            # 检查成功消息
            success_element = self.browser.find_element_safe(
                By.CSS_SELECTOR, self.selectors['success_message'], timeout=15
            )
            
            if success_element:
                success_text = success_element.text
                logger.完成操作("代币领取验证", f"成功 - {success_text}")
                return True
            
            # 检查错误消息
            error_element = self.browser.find_element_safe(
                By.CSS_SELECTOR, self.selectors['error_message'], timeout=5
            )
            
            if error_element:
                error_text = error_element.text
                logger.错误(f"领取失败: {error_text}")
                return False
            
            # 检查页面URL变化
            current_url = self.browser.get_current_url()
            if "success" in current_url.lower() or "complete" in current_url.lower():
                logger.完成操作("代币领取验证", "成功（URL变化）")
                return True
            
            # 检查页面内容
            page_text = self.browser.driver.page_source.lower()
            success_keywords = ["success", "successful", "complete", "claimed", "sent", "成功", "完成", "已发送"]
            
            if any(keyword in page_text for keyword in success_keywords):
                logger.完成操作("代币领取验证", "成功（内容检测）")
                return True
            
            logger.警告("无法确定领取结果")
            return False
            
        except Exception as e:
            logger.错误(f"验证结果失败: {str(e)}")
            return False
    
    def _get_random_proxy(self) -> Optional[str]:
        """获取随机代理"""
        try:
            proxies = self.config.get('proxy_list', [])
            if proxies:
                proxy = random.choice(proxies)
                logger.代理("选择代理", proxy)
                return proxy
            return None
        except Exception as e:
            logger.错误(f"获取代理失败: {str(e)}")
            return None
    
    def _cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                self.browser.close_browser()
            
            # 清理验证码临时文件
            self.captcha_solver.cleanup_temp_files()
            
            logger.信息("资源清理完成")
            
        except Exception as e:
            logger.错误(f"资源清理失败: {str(e)}")
    
    def get_claim_status(self) -> Dict[str, Any]:
        """获取领取状态"""
        return {
            'current_step': self.current_step,
            'faucet_url': self.faucet_url,
            'network': self.network_name,
            'timestamp': time.time()
        }

# 导出
__all__ = ['FaucetHandler']