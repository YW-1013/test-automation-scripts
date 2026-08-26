import subprocess
import psutil
import time
import uiautomator2 as u2
import logging
import cv2
import os

device_ip = "192.168.1.100"
power_ip = "emulator-5554"
power_sn = 4
power_path = "D:\\leidian\\LDPlayer9\\dnplayer.exe"
power_process_name = "dnplayer.exe"
power_name = "yw8769"
screenshot_path = "screenshot.png"

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def match_image(template_path, screenshot_path, threshold=0.8):
    """
    在截图中寻找与模板图像相似的区域
    :param template_path: 模板图像路径
    :param screenshot_path: 截图路径
    :param threshold: 相似度阈值
    :return: True/False 根据匹配结果判断
    """
    # 检查路径
    if not os.path.exists(screenshot_path):
        logger.error(f"Screenshot file {screenshot_path} does not exist.")
        return False
    if not os.path.exists(template_path):
        logger.error(f"Template file {template_path} does not exist.")
        return False

    # 读取截图和模板图像
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path, 0)  # 模板图像读取为灰度图像

    if screenshot is None:
        logger.error(f"Failed to read screenshot {screenshot_path}")
        return False
    if template is None:
        logger.error(f"Failed to read template {template_path}")
        return False

    # 转换截图为灰度图像
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # 使用模板匹配
    result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)

    # 获取匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return max_val >= threshold

def take_screenshot(device, filename):
    logger.info("Taking screenshot...")
    device.screenshot(filename)
    if os.path.exists(filename):
        logger.info(f"Screenshot saved to {filename}")
    else:
        logger.error(f"Failed to save screenshot to {filename}")

def run_command(command):
    process = subprocess.Popen(command, bufsize=10000, stdout=subprocess.PIPE, close_fds=True)
    out = process.communicate()[0]
    if process.stdin: process.stdin.close()
    if process.stdout: process.stdout.close()
    if process.stderr: process.stderr.close()
    try:
        process.kill()
    except OSError:
        pass
    return out.decode()

def get_adb_devices():
    output = run_command('adb devices')
    devices = output.strip().split('\n')[1:]
    return devices

def check_and_reconnect():
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if f"{device_ip}:5555" not in device_status.keys() or device_status[f"{device_ip}:5555"].strip() != 'device':
        raise RuntimeError("设备未成功连接大屏ip")

def check_and_reconnect_except():
    run_command(f'adb connect {device_ip}')
    devices = get_adb_devices()
    logger.info(f"连接异常时的adb devices状态{devices}")
    run_command(f"adb disconnect {device_ip}")
    run_command(f"adb connect {device_ip}")
    devices = get_adb_devices()
    logger.info(f"重新连接后的adb devices状态{devices}")

def reboot_android(d):
    if d(resourceId="com.h3c.launcher:id/iv_power_key").exists(timeout=5):
        d(resourceId="com.h3c.launcher:id/iv_power_key").click()

    # 等待并点击重启图标
    if d(resourceId="com.h3c.launcher:id/iv_reboot").exists(timeout=5):
        d(resourceId="com.h3c.launcher:id/iv_reboot").click()

    # 等待并点击"重启"文字
    if d(text="重启").exists(timeout=5):
        d(text="重启").click()

test_times = 1
while True:
    try:
        check_and_reconnect()
    except Exception as connect_e:
        print(f"设备连接失败, 意外报错, 继续下一轮, 失败信息为 {connect_e}")
        check_and_reconnect_except()
        continue

    run_command(f"adb -s {device_ip} shell am start com.h3c.vm.windows/.ui.activity.LaunchVmActivity")
    time.sleep(60)

    # 获取设备截图
    device2 = u2.connect(device_ip)
    take_screenshot(device2, screenshot_path)

    if match_image("template1.png", screenshot_path, threshold=0.8):
        print(f"第{test_times}轮测试正常")
    else:
        print(f"第{test_times}轮测试不通过，测试停止")
        break

    reboot_android(device2)
    test_times += 1
    time.sleep(120)