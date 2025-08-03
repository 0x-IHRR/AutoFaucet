# -*- coding: utf-8 -*-
"""
验证码识别模块
支持多种验证码类型的识别，优先使用免费方案
"""

import os
import time
import base64
import requests
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from typing import Optional, Dict, Any, Tuple
import pytesseract
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import config_manager
from logger import logger

class CaptchaSolver:
    """验证码识别器"""
    
    def __init__(self):
        self.config = config_manager.get_captcha_config()
        self.temp_dir = "temp_captcha"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 初始化OCR引擎
        self._init_ocr()
        
        logger.信息("验证码识别器初始化完成")
    
    def _init_ocr(self):
        """初始化OCR引擎"""
        try:
            # 检查tesseract是否可用
            pytesseract.get_tesseract_version()
            self.ocr_available = True
            logger.信息("Tesseract OCR引擎可用")
        except Exception as e:
            self.ocr_available = False
            logger.警告(f"Tesseract OCR不可用: {str(e)}")
            logger.警告("请安装tesseract: brew install tesseract (macOS)")
    
    def solve_image_captcha(self, image_element=None, image_url: str = None, 
                          image_path: str = None, driver=None) -> Optional[str]:
        """识别图片验证码"""
        try:
            logger.验证码("开始识别图片验证码")
            
            # 获取验证码图片
            image_data = self._get_captcha_image(image_element, image_url, image_path, driver)
            if not image_data:
                return None
            
            # 保存原始图片
            timestamp = int(time.time())
            original_path = os.path.join(self.temp_dir, f"captcha_original_{timestamp}.png")
            
            if isinstance(image_data, bytes):
                with open(original_path, 'wb') as f:
                    f.write(image_data)
            else:
                image_data.save(original_path)
            
            # 预处理图片
            processed_path = self._preprocess_image(original_path)
            
            # 尝试多种识别方法
            result = None
            
            # 方法1: 本地OCR识别
            if self.ocr_available:
                result = self._ocr_recognize(processed_path)
                if result:
                    logger.验证码("OCR识别成功", result)
                    return result
            
            # 方法2: 免费在线OCR服务
            result = self._free_online_ocr(processed_path)
            if result:
                logger.验证码("在线OCR识别成功", result)
                return result
            
            # 方法3: 第三方付费服务（如果配置了）
            if self.config.get('use_paid_service', False):
                result = self._paid_service_recognize(processed_path)
                if result:
                    logger.验证码("付费服务识别成功", result)
                    return result
            
            logger.验证码("所有识别方法均失败")
            return None
            
        except Exception as e:
            logger.错误(f"验证码识别失败: {str(e)}")
            return None
    
    def _get_captcha_image(self, image_element, image_url, image_path, driver) -> Optional[Any]:
        """获取验证码图片"""
        try:
            if image_path and os.path.exists(image_path):
                # 从文件路径加载
                return Image.open(image_path)
            
            elif image_url:
                # 从URL下载
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    return BytesIO(response.content)
            
            elif image_element and driver:
                # 从页面元素截图
                return self._screenshot_element(driver, image_element)
            
            logger.错误("无法获取验证码图片")
            return None
            
        except Exception as e:
            logger.错误(f"获取验证码图片失败: {str(e)}")
            return None
    
    def _screenshot_element(self, driver, element) -> Optional[Image.Image]:
        """截取元素图片"""
        try:
            # 获取元素位置和大小
            location = element.location
            size = element.size
            
            # 截取整个页面
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))
            
            # 裁剪验证码区域
            left = location['x']
            top = location['y']
            right = left + size['width']
            bottom = top + size['height']
            
            captcha_image = image.crop((left, top, right, bottom))
            
            logger.验证码("元素截图成功", f"{size['width']}x{size['height']}")
            return captcha_image
            
        except Exception as e:
            logger.错误(f"元素截图失败: {str(e)}")
            return None
    
    def _preprocess_image(self, image_path: str) -> str:
        """预处理验证码图片"""
        try:
            logger.验证码("开始图片预处理")
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                # 尝试用PIL读取
                pil_image = Image.open(image_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 降噪
            denoised = cv2.medianBlur(gray, 3)
            
            # 二值化
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 形态学操作去除噪点
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 放大图片提高识别率
            height, width = cleaned.shape
            enlarged = cv2.resize(cleaned, (width * 3, height * 3), interpolation=cv2.INTER_CUBIC)
            
            # 保存处理后的图片
            timestamp = int(time.time())
            processed_path = os.path.join(self.temp_dir, f"captcha_processed_{timestamp}.png")
            cv2.imwrite(processed_path, enlarged)
            
            logger.验证码("图片预处理完成")
            return processed_path
            
        except Exception as e:
            logger.错误(f"图片预处理失败: {str(e)}")
            return image_path  # 返回原始路径
    
    def _ocr_recognize(self, image_path: str) -> Optional[str]:
        """使用Tesseract OCR识别"""
        try:
            if not self.ocr_available:
                return None
            
            # 配置OCR参数
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            
            # 识别文本
            text = pytesseract.image_to_string(
                Image.open(image_path),
                config=custom_config
            ).strip()
            
            # 清理结果
            result = self._clean_ocr_result(text)
            
            if result and len(result) >= 3:  # 验证码通常至少3位
                logger.验证码("OCR识别结果", result)
                return result
            
            return None
            
        except Exception as e:
            logger.错误(f"OCR识别失败: {str(e)}")
            return None
    
    def _clean_ocr_result(self, text: str) -> str:
        """清理OCR识别结果"""
        # 移除空白字符
        text = text.replace(' ', '').replace('\n', '').replace('\t', '')
        
        # 常见字符替换
        replacements = {
            'O': '0', 'o': '0', 'I': '1', 'l': '1', 'S': '5', 's': '5',
            'Z': '2', 'z': '2', 'B': '8', 'G': '6', 'g': '9'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # 只保留字母数字
        result = ''.join(c for c in text if c.isalnum())
        
        return result
    
    def _free_online_ocr(self, image_path: str) -> Optional[str]:
        """使用免费在线OCR服务"""
        try:
            logger.验证码("尝试免费在线OCR")
            
            # 方法1: OCR.space API (免费额度)
            result = self._ocr_space_api(image_path)
            if result:
                return result
            
            # 方法2: 其他免费API
            # 可以添加更多免费服务
            
            return None
            
        except Exception as e:
            logger.错误(f"免费在线OCR失败: {str(e)}")
            return None
    
    def _ocr_space_api(self, image_path: str) -> Optional[str]:
        """使用OCR.space免费API"""
        try:
            # OCR.space免费API密钥（需要注册获取）
            api_key = self.config.get('ocr_space_api_key', 'helloworld')  # 默认测试密钥
            
            url = 'https://api.ocr.space/parse/image'
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'apikey': api_key,
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'OCREngine': 2
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('IsErroredOnProcessing', False):
                        logger.警告(f"OCR.space处理错误: {result.get('ErrorMessage')}")
                        return None
                    
                    parsed_results = result.get('ParsedResults', [])
                    if parsed_results:
                        text = parsed_results[0].get('ParsedText', '').strip()
                        cleaned = self._clean_ocr_result(text)
                        if cleaned:
                            return cleaned
            
            return None
            
        except Exception as e:
            logger.错误(f"OCR.space API失败: {str(e)}")
            return None
    
    def _paid_service_recognize(self, image_path: str) -> Optional[str]:
        """使用付费识别服务"""
        try:
            service = self.config.get('paid_service', '2captcha')
            
            if service == '2captcha':
                return self._solve_with_2captcha(image_path)
            elif service == 'anticaptcha':
                return self._solve_with_anticaptcha(image_path)
            
            return None
            
        except Exception as e:
            logger.错误(f"付费服务识别失败: {str(e)}")
            return None
    
    def _solve_with_2captcha(self, image_path: str) -> Optional[str]:
        """使用2captcha服务"""
        try:
            api_key = self.config.get('2captcha_api_key')
            if not api_key:
                logger.警告("未配置2captcha API密钥")
                return None
            
            # 上传图片
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'key': api_key,
                    'method': 'post'
                }
                
                response = requests.post(
                    'http://2captcha.com/in.php',
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.text.startswith('OK|'):
                    captcha_id = response.text.split('|')[1]
                    
                    # 等待识别结果
                    for _ in range(30):  # 最多等待5分钟
                        time.sleep(10)
                        
                        result_response = requests.get(
                            f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}',
                            timeout=30
                        )
                        
                        if result_response.text.startswith('OK|'):
                            result = result_response.text.split('|')[1]
                            logger.验证码("2captcha识别成功", result)
                            return result
                        elif result_response.text != 'CAPCHA_NOT_READY':
                            logger.错误(f"2captcha错误: {result_response.text}")
                            break
            
            return None
            
        except Exception as e:
            logger.错误(f"2captcha服务失败: {str(e)}")
            return None
    
    def _solve_with_anticaptcha(self, image_path: str) -> Optional[str]:
        """使用AntiCaptcha服务"""
        # 类似2captcha的实现
        logger.信息("AntiCaptcha服务暂未实现")
        return None
    
    def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """解决reCAPTCHA v2"""
        try:
            logger.验证码("开始解决reCAPTCHA v2")
            
            if self.config.get('use_paid_service', False):
                return self._solve_recaptcha_v2_paid(site_key, page_url)
            
            logger.警告("reCAPTCHA v2需要付费服务")
            return None
            
        except Exception as e:
            logger.错误(f"reCAPTCHA v2解决失败: {str(e)}")
            return None
    
    def _solve_recaptcha_v2_paid(self, site_key: str, page_url: str) -> Optional[str]:
        """使用付费服务解决reCAPTCHA v2"""
        # 实现付费服务的reCAPTCHA v2解决方案
        logger.信息("付费reCAPTCHA v2服务暂未实现")
        return None
    
    def detect_captcha_type(self, driver) -> str:
        """检测验证码类型"""
        try:
            logger.验证码("检测验证码类型")
            
            # 检测reCAPTCHA
            if driver.find_elements(By.CLASS_NAME, "g-recaptcha"):
                return "recaptcha_v2"
            
            # 检测hCaptcha
            if driver.find_elements(By.CLASS_NAME, "h-captcha"):
                return "hcaptcha"
            
            # 检测图片验证码
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            for img in img_elements:
                src = img.get_attribute("src") or ""
                if any(keyword in src.lower() for keyword in ["captcha", "verify", "code"]):
                    return "image"
            
            # 检测canvas验证码
            if driver.find_elements(By.TAG_NAME, "canvas"):
                return "canvas"
            
            return "unknown"
            
        except Exception as e:
            logger.错误(f"检测验证码类型失败: {str(e)}")
            return "unknown"
    
    def wait_for_captcha(self, driver, timeout: int = 30) -> bool:
        """等待验证码出现"""
        try:
            logger.验证码("等待验证码出现")
            
            # 常见验证码选择器
            captcha_selectors = [
                "img[src*='captcha']",
                "img[src*='verify']",
                "img[src*='code']",
                ".g-recaptcha",
                ".h-captcha",
                "canvas",
                "[id*='captcha']",
                "[class*='captcha']"
            ]
            
            for selector in captcha_selectors:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.验证码("发现验证码", selector)
                    return True
                except:
                    continue
            
            logger.验证码("未发现验证码")
            return False
            
        except Exception as e:
            logger.错误(f"等待验证码失败: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            import glob
            temp_files = glob.glob(os.path.join(self.temp_dir, "captcha_*"))
            for file in temp_files:
                try:
                    os.remove(file)
                except:
                    pass
            logger.信息(f"清理临时文件: {len(temp_files)}个")
        except Exception as e:
            logger.警告(f"清理临时文件失败: {str(e)}")

# 导出
__all__ = ['CaptchaSolver']