import sys
import time
from datetime import datetime
import uiautomator2 as u2
import logging
import os
import subprocess

ip = '192.168.1.100'

def setup_logger():
    # 第一步，创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级开关
    current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 当前工作目录
    # 创建文件输出处理器
    log_dir = os.path.join(current_working_dir, "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, '{}.log'.format(time.strftime("%Y%m%d_%H%M%S", time.localtime())))
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 第三步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)

    # 第四步，将handler添加到logger里面
    logger.addHandler(file_handler)

    # 如果需要同时需要在终端上输出，定于一個streamHandler
    print_handler = logging.StreamHandler()  # 往屏幕上输出
    print_handler.setFormatter(formatter)  # 设置屏幕上显示的格式
    logger.addHandler(print_handler)

    return logger
def is_network_connected(d):
    # You might want to encapsulate the logic to check connection status
    try:
        return (d(resourceId="com.h3c.settings:id/m_wireless_connecting_item").exists() or
                d(text="我的网络").exists() or
                d(resourceId="com.h3c.settings:id/m_wireless_rv_wifi_list").exists() or
                d(resourceId="com.h3c.settings:id/m_wireless_rv_wifi_my_list").exists() or
                d(text="使用会议、投屏、文件分享时，建议开启Wi-Fi。").exists())
    except:
        logger.error("UI element not found.")
        return False
def screenshot(d):
    current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 当前工作目录
    image_path = os.path.join(current_working_dir,'screenshot')
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(image_path,f"{now}.jpg")
    d.screenshot(filename=screenshot_path)

logger = setup_logger()

# 连接到设备
subprocess.Popen(f'adb connect {ip}')
d = u2.connect(ip)

d.app_start("com.h3c.settings", "com.h3c.settings.main.ui.activity.SettingActivity")
time.sleep(5)
d(text="无线网络").click()
times = 0
while True:
    try:
        times += 1
        d(className="android.widget.Switch").click()
        time.sleep(10)  # Adjust this time to ensure elements have loaded.
        # screenshot(d)
        if not is_network_connected(d):
            logger.info(f"第{times}次压测出现wifi无法连接的问题")
            screenshot(d)
            break
        else:
            logger.info(f"第{times}次压测通过")
    except Exception as e:
        logger.info(e)
        # 连接到设备
        subprocess.Popen(f'adb disconnect {ip}')
        time.sleep(10)
        subprocess.Popen(f'adb connect {ip}')
        d = u2.connect(ip)

        d.app_start("com.h3c.settings", "com.h3c.settings.main.ui.activity.SettingActivity")
        time.sleep(5)
        d(text="无线网络").click()
