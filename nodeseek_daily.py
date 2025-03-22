# -- coding: utf-8 --
"""
Copyright (c) 2024 [Hosea]
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import traceback
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

ns_random = os.environ.get("NS_RANDOM","false")
cookie = os.environ.get("NS_COOKIE") or os.environ.get("COOKIE")
# 通过环境变量控制是否使用无头模式，默认为 True（无头模式）
headless = os.environ.get("HEADLESS", "true").lower() == "true"

randomInputStr = ["bd","绑定","帮顶"]

def click_sign_icon(driver):
    """
    尝试点击签到图标和试试手气按钮的通用方法
    """
    try:
        print("开始查找签到图标...")
        
        # 检查是否被Cloudflare拦截
        time.sleep(10)  # 增加等待时间
        
        # 打印当前页面URL和标题，用于调试
        print(f"当前页面URL: {driver.current_url}")
        print(f"当前页面标题: {driver.title}")
        
        # 检查是否在Cloudflare验证页面
        if "Just a moment" in driver.title or "Cloudflare" in driver.title:
            print("检测到Cloudflare验证页面，等待更长时间...")
            # 等待更长时间以通过Cloudflare验证
            time.sleep(20)
            # 刷新页面
            driver.refresh()
            time.sleep(10)
        
        # 尝试多次查找签到图标
        max_retries = 3
        for retry in range(max_retries):
            try:
                print(f"尝试查找签到图标 (尝试 {retry+1}/{max_retries})...")
                # 使用更精确的选择器定位签到图标，增加等待时间
                sign_icon = WebDriverWait(driver, 45).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@title='签到']"))
                )
                print("找到签到图标，准备点击...")
                
                # 确保元素可见和可点击
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sign_icon)
                time.sleep(1)
                
                # 打印元素信息
                print(f"签到图标元素: {sign_icon.get_attribute('outerHTML')}")
                
                # 尝试点击
                try:
                    sign_icon.click()
                    print("签到图标点击成功")
                except Exception as click_error:
                    print(f"点击失败，尝试使用 JavaScript 点击: {str(click_error)}")
                    driver.execute_script("arguments[0].click();", sign_icon)
                
                print("等待页面跳转...")
                time.sleep(8)  # 增加等待时间
                
                # 打印当前URL
                print(f"当前页面URL: {driver.current_url}")
                
                # 点击"试试手气"按钮
                try:
                    click_button = None
                    
                    if ns_random:
                        click_button = WebDriverWait(driver, 10).until(  # 增加等待时间
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '试试手气')]"))
                        )
                    else:
                        click_button = WebDriverWait(driver, 10).until(  # 增加等待时间
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '鸡腿 x 5')]"))
                        )
                    
                    # 确保按钮可见
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", click_button)
                    time.sleep(1)
                    
                    # 尝试点击
                    try:
                        click_button.click()
                        print("完成试试手气点击")
                    except Exception as direct_click_error:
                        print(f"直接点击失败，尝试使用JavaScript点击: {str(direct_click_error)}")
                        driver.execute_script("arguments[0].click();", click_button)
                        print("使用JavaScript点击试试手气按钮")
                except Exception as lucky_error:
                    print(f"试试手气按钮点击失败或者签到过了: {str(lucky_error)}")
                
                return True
                
            except Exception as retry_error:
                print(f"查找签到图标失败 (尝试 {retry+1}/{max_retries}): {str(retry_error)}")
                if retry < max_retries - 1:
                    print("等待后重试...")
                    time.sleep(10)
                    driver.refresh()
                    time.sleep(10)
                else:
                    print("达到最大重试次数，无法找到签到图标")
                    return False
        
    except Exception as e:
        print(f"签到过程中出错:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"当前页面URL: {driver.current_url}")
        print(f"当前页面源码片段: {driver.page_source[:500]}...")
        print("详细错误信息:")
        traceback.print_exc()
        return False

def setup_driver_and_cookies():
    """
    初始化浏览器并设置cookie的通用方法
    返回: 设置好cookie的driver实例
    """
    try:
        cookie = os.environ.get("NS_COOKIE") or os.environ.get("COOKIE")
        headless = os.environ.get("HEADLESS", "true").lower() == "true"
        
        if not cookie:
            print("未找到cookie配置")
            return None
            
        print("开始初始化浏览器...")
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 添加更多参数来绕过 Cloudflare 检测，无论是否为无头模式
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--window-size=1920,1080')
        # 设置更新的 User-Agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
        
        if headless:
            print("启用无头模式...")
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        
        print("正在启动Chrome...")
        driver = uc.Chrome(options=options)
        
        # 执行 JavaScript 来修改 webdriver 标记，无论是否为无头模式
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']})")
        driver.set_window_size(1920, 1080)
        
        print("Chrome启动成功")
        
        print("正在设置cookie...")
        driver.get('https://www.nodeseek.com')
        
        # 增加等待时间，确保页面完全加载
        print("等待页面加载...")
        time.sleep(10)
        
        for cookie_item in cookie.split(';'):
            try:
                name, value = cookie_item.strip().split('=', 1)
                driver.add_cookie({
                    'name': name, 
                    'value': value, 
                    'domain': '.nodeseek.com',
                    'path': '/'
                })
            except Exception as e:
                print(f"设置cookie出错: {str(e)}")
                continue
        
        print("刷新页面...")
        driver.refresh()
        time.sleep(5)  # 增加等待时间
        
        return driver
        
    except Exception as e:
        print(f"设置浏览器和Cookie时出错: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc())
        return None

# 评论功能已移除
def nodeseek_add_chicken_leg(driver):
    """仅执行加鸡腿功能"""
    try:
        print("正在访问交易区...")
        target_url = 'https://www.nodeseek.com/categories/trade'
        driver.get(target_url)
        print("等待页面加载...")
        
        # 检查是否被Cloudflare拦截
        time.sleep(10)  # 增加等待时间
        
        # 打印当前页面URL和标题，用于调试
        print(f"当前页面URL: {driver.current_url}")
        print(f"当前页面标题: {driver.title}")
        
        # 检查是否在Cloudflare验证页面
        if "Just a moment" in driver.title or "Cloudflare" in driver.title:
            print("检测到Cloudflare验证页面，等待更长时间...")
            # 等待更长时间以通过Cloudflare验证
            time.sleep(20)
            # 刷新页面
            driver.refresh()
            time.sleep(10)
        
        # 尝试多次获取帖子列表
        max_retries = 3
        for retry in range(max_retries):
            try:
                print(f"尝试获取帖子列表 (尝试 {retry+1}/{max_retries})...")
                # 获取初始帖子列表，增加等待时间
                posts = WebDriverWait(driver, 45).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.post-list-item'))
                )
                print(f"成功获取到 {len(posts)} 个帖子")
                break
            except Exception as e:
                print(f"获取帖子列表失败 (尝试 {retry+1}/{max_retries}): {str(e)}")
                if retry < max_retries - 1:
                    print("等待后重试...")
                    time.sleep(10)
                    driver.refresh()
                    time.sleep(10)
                else:
                    print("达到最大重试次数，无法获取帖子列表")
                    return
        
        # 过滤掉置顶帖
        valid_posts = [post for post in posts if not post.find_elements(By.CSS_SELECTOR, '.pined')]
        if not valid_posts:
            print("没有找到有效的非置顶帖子")
            return
            
        selected_posts = random.sample(valid_posts, min(5, len(valid_posts)))
        
        # 存储已选择的帖子URL
        selected_urls = []
        for post in selected_posts:
            try:
                post_link = post.find_element(By.CSS_SELECTOR, '.post-title a')
                selected_urls.append(post_link.get_attribute('href'))
            except Exception as e:
                print(f"获取帖子链接失败: {str(e)}")
                continue
        
        # 使用URL列表进行操作
        for i, post_url in enumerate(selected_urls):
            try:
                print(f"正在处理第 {i+1} 个帖子")
                driver.get(post_url)
                
                # 处理加鸡腿
                click_chicken_leg(driver)
                time.sleep(random.uniform(2,5))
                
            except Exception as e:
                print(f"处理帖子时出错: {str(e)}")
                continue
                
        print("NodeSeek加鸡腿任务完成")
                
    except Exception as e:
        print(f"NodeSeek加鸡腿出错: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc())

def click_chicken_leg(driver):
    try:
        print("尝试点击加鸡腿按钮...")
        # 等待页面完全加载
        time.sleep(5)
        
        # 尝试滚动到页面中间，以便更好地加载元素
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
        time.sleep(2)
        
        # 使用更长的等待时间和更精确的选择器
        try:
            chicken_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="nsk-post"]//div[@title="加鸡腿"][1]'))
            )
        except Exception as e:
            print(f"未找到加鸡腿按钮，尝试使用备用选择器: {str(e)}")
            # 尝试使用备用选择器
            chicken_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.nsk-post .post-action-item[title="加鸡腿"]'))
            )
        
        # 打印找到的元素信息
        print(f"找到加鸡腿按钮: {chicken_btn.get_attribute('outerHTML')}")
        
        # 确保元素可见和可点击
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chicken_btn)
        time.sleep(1)
        
        # 尝试点击，如果直接点击失败则使用JavaScript点击
        try:
            chicken_btn.click()
            print("加鸡腿按钮点击成功")
        except Exception as click_error:
            print(f"直接点击失败，尝试使用JavaScript点击: {str(click_error)}")
            driver.execute_script("arguments[0].click();", chicken_btn)
            print("使用JavaScript点击加鸡腿按钮")
        
        # 等待确认对话框出现，增加等待时间
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.msc-confirm'))
            )
            print("确认对话框已出现")
        except Exception as dialog_error:
            print(f"等待确认对话框出现失败: {str(dialog_error)}")
            return False
        
        # 检查是否是7天前的帖子
        try:
            error_title = driver.find_element(By.XPATH, "//h3[contains(text(), '该评论创建于7天前')]")
            if error_title:
                print("该帖子超过7天，无法加鸡腿")
                ok_btn = driver.find_element(By.CSS_SELECTOR, '.msc-confirm .msc-ok')
                ok_btn.click()
                return False
        except Exception as not_found:
            # 没有找到错误提示，说明可以加鸡腿
            try:
                ok_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.msc-confirm .msc-ok'))
                )
                ok_btn.click()
                print("确认加鸡腿成功")
            except Exception as ok_error:
                print(f"点击确认按钮失败: {str(ok_error)}")
                # 尝试使用JavaScript点击
                try:
                    ok_btn = driver.find_element(By.CSS_SELECTOR, '.msc-confirm .msc-ok')
                    driver.execute_script("arguments[0].click();", ok_btn)
                    print("使用JavaScript点击确认按钮")
                except Exception as js_error:
                    print(f"JavaScript点击确认按钮失败: {str(js_error)}")
                    return False
            
        # 等待确认对话框消失，增加等待时间
        try:
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.msc-overlay'))
            )
            time.sleep(2)  # 额外等待以确保对话框完全消失
        except Exception as overlay_error:
            print(f"等待对话框消失失败: {str(overlay_error)}")
            # 继续执行，不要因为这个错误而中断
        
        return True
        
    except Exception as e:
        print(f"加鸡腿操作失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始执行NodeSeek签到加鸡腿脚本...")
    try:
        # 初始化浏览器
        driver = setup_driver_and_cookies()
        if not driver:
            print("浏览器初始化失败")
            exit(1)
        
        # 先执行签到操作
        print("\n=== 开始执行签到操作 ===")
        sign_success = click_sign_icon(driver)
        if sign_success:
            print("签到操作执行成功")
        else:
            print("签到操作执行失败，但将继续执行加鸡腿操作")
        
        # 然后执行加鸡腿操作
        print("\n=== 开始执行加鸡腿操作 ===")
        nodeseek_add_chicken_leg(driver)
        
        print("\n所有操作执行完成")
    except Exception as e:
        print(f"脚本执行过程中出现未处理的异常: {str(e)}")
        print("详细错误信息:")
        traceback.print_exc()
    finally:
        # 确保浏览器正常关闭
        try:
            if driver:
                print("正在关闭浏览器...")
                driver.quit()
                print("浏览器已关闭")
        except Exception as close_error:
            print(f"关闭浏览器时出错: {str(close_error)}")
        
        print("脚本执行完成")
        # 调试模式下可以取消注释以下代码，保持浏览器窗口打开
        # while True:
        #     time.sleep(1)

