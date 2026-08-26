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
power_name = "0367"
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

def kill_process_by_name(process_name, logger):
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            proc.kill()
            logger.info(f"进程 {process_name} 已被终止")
            return
    logger.info(f"没有找到进程 {process_name}")

def reopen_power(power_process_name, power_path, logger):
    logger.info("杀掉模拟器进程")
    kill_process_by_name(power_process_name, logger)
    time.sleep(10)
    logger.info("重新打开模拟器")
    app1 = subprocess.Popen(power_path)
    logger.info(app1)
    time.sleep(40)

def comnon_to_power(power_ip, power_sn, power_name):
    recheck = 0
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接，devices信息为{devices}")

    device = u2.connect(power_ip)

    while not device.xpath(f"//android.widget.ImageView[contains(@resource-id, 'com.oray.sunlogin:id/iv_power_strip_s{power_sn}')]").wait(30):
        if device(text="向日葵远程控制").exists(timeout=20):
            device(text="向日葵远程控制").click()
        if device(text="开机设备").exists(timeout=20):
            device(text="开机设备").click()
        if device(text=power_name).exists(timeout=20):
            device(text=power_name).click()
        if device(text="显示列表").exists(timeout=5):
            device(text="显示列表").click()
        if device(text="确定").exists(timeout=5):
            device(text="确定").click()
        if device(resourceId="com.oray.sunlogin:id/tv_offline_power_strip_tip").exists(timeout=5):
            device(resourceId="com.oray.sunlogin:id/fl_back").click()
            time.sleep(2)
            device(text=power_name).click()
        recheck += 1
        if recheck > 5:
            raise RuntimeError(f"命令执行失败: 尝试打开模拟器进入到电源按钮界面失败")

def switch_power(tests, device_ip, power_ip, power_sn, power_path, power_process_name, power_name):
    device = u2.connect(power_ip)
    if device(text="显示列表").exists(timeout=20):
        device(text="显示列表").click()
    if device(text="确定").exists(timeout=20):
        device(text="确定").click()

    if (tests + 1) % 20 == 0:
        logger.info("杀掉模拟器进程")
        kill_process_by_name(power_process_name, logger)
        logger.info("重新打开模拟器")
        app1 = subprocess.Popen(power_path)
        logger.info(app1)
        time.sleep(40)
        check_and_reconnect(device_ip, power_ip, power_sn, power_path, power_process_name, power_name, logger)

    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接, devices信息为{devices}")
    device = u2.connect(power_ip)

    logger.info("关闭电源")
    if device(resourceId="com.oray.sunlogin:id/fl_back").exists(timeout=10):
        device(resourceId="com.oray.sunlogin:id/fl_back").click()
    if device(text=power_name).exists(timeout=10):
        device(text=power_name).click()
    while device.xpath(f"//android.view.View[contains(@resource-id, 'com.oray.sunlogin:id/cd_view_s{power_sn}')]").exists:
        logger.info("检测到当前电源为开启状态，关闭电源")
        device.xpath(f"//android.widget.ImageView[contains(@resource-id, 'com.oray.sunlogin:id/iv_power_strip_s{power_sn}')]").click()
        if device(text="确认").exists(timeout=5):
            device(text="确认").click()
        if device(resourceId="com.oray.sunlogin:id/fl_back").exists(timeout=10):
            device(resourceId="com.oray.sunlogin:id/fl_back").click()
        if device(text=power_name).exists(timeout=10):
            device(text=power_name).click()

    time.sleep(10)

    logger.info("开启电源")
    if device(resourceId="com.oray.sunlogin:id/fl_back").exists(timeout=10):
        device(resourceId="com.oray.sunlogin:id/fl_back").click()
    if device(text=power_name).exists(timeout=10):
        device(text=power_name).click()
    while not device.xpath(f"//android.view.View[contains(@resource-id, 'com.oray.sunlogin:id/cd_view_s{power_sn}')]").wait(3):
        logger.info("检测到当前电源为关闭状态，开启电源")
        device.xpath(f"//android.widget.ImageView[contains(@resource-id, 'com.oray.sunlogin:id/iv_power_strip_s{power_sn}')]").click()
        if device(text="确认").exists(timeout=5):
            device(text="确认").click()
        if device(resourceId="com.oray.sunlogin:id/fl_back").exists(timeout=10):
            device(resourceId="com.oray.sunlogin:id/fl_back").click()
        if device(text=power_name).exists(timeout=10):
            device(text=power_name).click()

def check_and_reconnect(device_ip, power_ip, power_sn, power_path, power_process_name, power_name, logger):
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}

    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        reopen_power(power_process_name, power_path, logger)
    comnon_to_power(power_ip, power_sn, power_name)
    if f"{device_ip}:5555" not in device_status.keys() or device_status[f"{device_ip}:5555"].strip() != 'device':
        raise RuntimeError("设备未成功连接大屏ip")

def check_and_reconnect_except(device_ip, power_ip, power_sn, power_path, power_process_name, power_name, logger):
    run_command(f'adb connect {device_ip}')
    devices = get_adb_devices()
    logger.info(f"连接异常时的adb devices状态{devices}")
    reopen_power(power_process_name, power_path, logger)
    run_command(f"adb disconnect {device_ip}")
    run_command(f"adb connect {device_ip}")
    devices = get_adb_devices()
    logger.info(f"重新连接后的adb devices状态{devices}")

device = u2.connect(power_ip)
test_times = 0
while True:
    try:
        device.xpath(
            f"//android.widget.ImageView[contains(@resource-id, 'com.oray.sunlogin:id/iv_power_strip_s{power_sn}')]").click()
        if device(text="确认").exists(timeout=5):
            device(text="确认").click()
        time.sleep(10)
        device.xpath(
            f"//android.widget.ImageView[contains(@resource-id, 'com.oray.sunlogin:id/iv_power_strip_s{power_sn}')]").click()
        if device(text="确认").exists(timeout=5):
            device(text="确认").click()
        time.sleep(10)
        test_times += 1
        print(f"运行了{test_times}次")
    except:
        continue
