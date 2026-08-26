import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys  # 导入 Keys 类
import logging
from logging import handlers
import os
import sys
import datetime


def get_logger(log_filename, level=logging.INFO, when='D', back_count=0):
    logger = logging.getLogger(log_filename)
    logger.setLevel(level)
    log_path = os.path.join(LOG_ROOT, "logs")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file_path = os.path.join(log_path, log_filename)
    formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fh = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when=when,
        backupCount=back_count,
        encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )


dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
LOG_ROOT = dirname
logger = get_logger('test.log')

num = 0
while True:
    num += 1

    logger.info(f"第{num}次测试开始")
    chrome_driver_path = 'D:\\chromedriver_win64\\chromedriver.exe'

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    url = "http://your-server.example.com/#/wisdom/device/detail?wisdomId=YOUR_DEVICE_ID"
    driver.get(url)

    wait_for_page_load(driver)

    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div/form/div[2]/button'))
        )
        username_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入用户名']")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入密码']")
        username_input.send_keys("YOUR_ACCOUNT")
        password_input.send_keys("YOUR_PASSWORD")
        login_button.click()

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="router-view"]/div/div/div/div[1]/div[2]/div/input'))
        )
        search_button.click()
        search_button.send_keys('1-0R')
        search_button.send_keys(Keys.ENTER)
        # driver.maximize_window()
        time.sleep(5)
        device_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="router-view"]/div/div/div/div[2]/div[1]/div/div[3]/table/tbody/tr/td[2]/div/span'))
        )
        device_button.click()
        time.sleep(30)


        # 获取所有打开的窗口句柄
        all_handles = driver.window_handles

        # 切换到新窗口
        driver.switch_to.window(all_handles[1])

        wait_for_page_load(driver)
        time.sleep(5)
        flash_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "router-view"] / div / div[1] / i'))
        )
        flash_button.click()
        time.sleep(30)


        remote_control_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="router-view"]/div/div[2]/div[2]/button[3]'))
        )
        remote_control_button.click()

        # 等待30秒，判断是否出现正在控制的字样
        time.sleep(30)
        try:
            element = driver.find_element(By.XPATH, '//*[@id="router-view"]/div/div[8]/div/div/div[1]/span')
            logger.info("指定的XPath存在")
        except NoSuchElementException:
            logger.info("指定的XPath不存在")
            driver.save_screenshot(os.path.join(dirname, f"screenshot_{datetime.datetime.now().strftime('%m%d%H%M%S')}.png"))

    except TimeoutException as e:
        logger.error(f"等待元素超时: {str(e)}")
        driver.save_screenshot(os.path.join(dirname, 'timeout_screenshot.png'))
        continue

    finally:
        image_folder = os.path.join(dirname, 'image')
        if not os.path.exists(image_folder):
            os.mkdir(image_folder)
        driver.quit()
        time.sleep(30)
        logger.info("\n")