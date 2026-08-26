from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import configparser

# 配置部分
current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # 当前工作目录
config_path = os.path.join(current_working_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
urls = config['Urls']
settings = config['Settings']
PLAY_VIDEO_DURATION = settings.getint('PLAY_VIDEO_DURATION')
BROWSE_DOUYIN_DURATION = settings.getint('BROWSE_DOUYIN_DURATION')
VIDEO_URL = urls.get('VIDEO_URL')
DOUYIN_URL = urls.get('DOUYIN_URL')
driver_path = os.path.join(os.path.join(current_working_dir,'chromedriver'),'chromedriver.exe')

# 初始化 WebDriver
chrome_options = Options()
chrome_options.add_argument("--mute-audio")  # 这个参数用于启动后默认静音

# 指定 chrome driver 路径
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 打开腾讯视频并播放指定时长
    driver.get(VIDEO_URL)

    # 将网页全屏
    driver.maximize_window()

    # 等待页面加载完成
    # time.sleep(5)

    # 将视频全屏播放（找到全屏按钮并点击）
    try:
        # 查找全屏按钮并点击（这里的选择器可能需要根据具体页面调整）
        fullscreen_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class*="fullscreen"]'))
        )
        fullscreen_button.click()
        print("成功全屏播放视频")
    except Exception as e:
        print("未找到全屏按钮或全屏失败:", e)

    time.sleep(PLAY_VIDEO_DURATION)

    # 打开抖音网页
    driver.get(DOUYIN_URL)
    time.sleep(5)  # 等待页面加载

    # 关闭登录弹窗
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'douyin-login__close'))
        )
        close_button.click()
        print("成功关闭登录弹窗")
        time.sleep(2)
    except Exception as e:
        print("未找到关闭按钮或关闭失败:", e)

    # 模拟按键操作，持续指定时间
    start_time = time.time()
    while time.time() - start_time < BROWSE_DOUYIN_DURATION:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)
        time.sleep(10)


finally:
    # 关闭浏览器
    driver.quit()