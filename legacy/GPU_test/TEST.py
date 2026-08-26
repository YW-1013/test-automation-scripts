from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pyautogui
import os
import configparser
import sys

# 获取当前工作目录
current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
config_path = os.path.join(current_working_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

# 从配置文件中读取路径和设置
paths = config['Paths']
settings = config['Settings']
chrome_driver = paths.get('chrome_driver')
chrome_user_data = paths.get('chrome_user_data')
run_time = settings.getint('run_time')  # 获取运行时间（秒）

# 设置Chrome选项
options = Options()
options.add_argument(f"user-data-dir={chrome_user_data}")

# 初始化WebDriver服务
service = Service(chrome_driver)
driver = webdriver.Chrome(service=service, options=options)

# 全屏操作
def toggle_fullscreen():
    pyautogui.hotkey('win', 'up')

# 记录开始运行的时间
start_time = time.time()

while True:
    try:
        # 检查运行时间是否超过指定的时间
        elapsed_time = time.time() - start_time
        if elapsed_time > run_time:
            print("运行时间已达到指定时间，退出程序。")
            break

        driver.get("https://your-tenant.feishu.cn/share/base/dashboard/shrcn6sk4q4IoXTqRFfz529PxZf")
        toggle_fullscreen()
        time.sleep(500)  # 等待页面加载

        # 使用 XPath 定位并点击文本
        target_text = driver.find_element(By.XPATH, "//*[text()='本周各版本bug数据']")
        target_text.click()

        # 在使用 body 之前，确保获取页面的 <body> 元素
        body = driver.find_element(By.TAG_NAME, "body")

        # 循环按 pgup 和 pgdn 键
        body.send_keys(Keys.PAGE_DOWN)
        while True:
            # 检查运行时间是否超过指定的时间
            elapsed_time = time.time() - start_time
            if elapsed_time > run_time:
                print("运行时间已达到指定时间，退出程序。")
                break

            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_UP)
            body.send_keys(Keys.PAGE_UP)
            body.send_keys(Keys.PAGE_UP)
            body.send_keys(Keys.PAGE_UP)
            body.send_keys(Keys.PAGE_UP)
            body.send_keys(Keys.PAGE_UP)

    except Exception as e:
        print(e)
        driver.quit()
        break

driver.quit()
