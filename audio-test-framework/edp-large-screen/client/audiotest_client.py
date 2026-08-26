# -*- coding: utf-8 -*-

"""
2024-10-31:新增检查项，检测是否出现两分钟后重启的现象
"""

import socket
import time
import pyaudio
import wave
import os
import logging
from logging import handlers
import numpy as np
import scipy.fft
import sys
import configparser
import subprocess
import pywifi
from pywifi import const
import pyautogui
from pywinauto.application import Application
import win32com.client
from PIL import Image
import wmi
from pygrabber.dshow_graph import FilterGraph
import shutil
import glob


current_working_dir = os.getcwd()
test_wav_path = os.path.join(current_working_dir, 'test.wav')
test_wav_Save_path = os.path.join(current_working_dir, 'recorded_audio.wav')
hdmi_8k_mega_image = os.path.join(current_working_dir, '8k_mega_image')
hdmi_8k_mega_image_1 = os.path.join(hdmi_8k_mega_image, '1.jpg')
hdmi_edp_mega_image = os.path.join(current_working_dir, 'edp_mega_image')
hdmi_edp_mega_image_1 = os.path.join(hdmi_edp_mega_image, '1.jpg')
test_image = os.path.join(current_working_dir, 'test_image')
test_image_1 = os.path.join(test_image, '1.jpg')
setting_path = r'C:\Program Files (x86)\H3C.Magic\MagicSetting\H3C.Entry.exe'
hdmi_in_path = r'C:\Program Files (x86)\H3C.Magic\MagicHdmiRecord\H3C.Entry.exe'
mega_x1 = 2277  # 切换系统按钮横坐标
mega_y1 = 3357  # 切换系统按钮纵坐标
mega_x2 = 4023  # 确定按钮横坐标
mega_y2 = 2245  # 确定按钮纵坐标
mega_hdmi_in_left_on_x = 1490  # hdmi-in截图左上角横坐标
mega_hdmi_in_left_on_y = 570  # hdmi-in截图左上角纵坐标
mega_hdmi_in_right_width = 4706  # hdmi-in截图宽度
mega_hdmi_in_right_height = 2934  # hdmi-in截图高度
edp_mega_x1 = 1172  # 切换系统按钮横坐标
edp_mega_y1 = 1695  # 切换系统按钮纵坐标
edp_mega_x2 = 2020  # 确定按钮横坐标
edp_mega_y2 = 1140  # 确定按钮纵坐标
audio_file = test_wav_path
recorded_file = test_wav_Save_path

config = configparser.ConfigParser()
config.read('audio_test.ini',encoding='utf-8-sig')
rms_single = int(config.get('audio_message', 'rms'))
record_time = int(config.get('audio_message', 'record_time'))
host_ip = config.get('audio_message', 'host_ip')
wifi_name = config.get('audio_message', 'connect_wifi_name')
wifi_password = config.get('audio_message', 'wifi_password')
test_project = config.get('audio_message', 'test_project')
boot_delay = int(config.get('audio_message', 'boot_delay'))
config_usb_names = config.get('audio_message', 'u_disk_name').split(',')
config_camera_names = config.get('audio_message', 'camera_name').split(',')
sim_check = int(config.get('audio_message', 'sim_check'))
success = config.get('audio_message', 'success')


def get_logger(log_filename, level=logging.INFO, when='D', back_count=0):
    """
    :brief  日志记录
    :param log_filename: 日志名称
    :param level: 日志等级
    :param when: 间隔时间:
        S:秒
        M:分
        H:小时
        D:天
        W:每星期（interval==0时代表星期一）
        midnight: 每天凌晨
    :param back_count: 备份文件的个数，若超过该值，就会自动删除
    :return: logger
    """
    # 创建一个日志器。提供了应用程序接口
    logger = logging.getLogger(log_filename)
    # 设置日志输出的最低等级,低于当前等级则会被忽略
    logger.setLevel(level)
    # 创建日志输出路径
    log_path = os.path.join(LOG_ROOT, "logs")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file_path = os.path.join(log_path, log_filename)
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # 创建处理器：ch为控制台处理器，fh为文件处理器
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # 输出到文件
    fh = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when=when,
        backupCount=back_count,
        encoding='utf-8')
    fh.setLevel(level)
    # 设置日志输出格式
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # 将处理器，添加至日志器中
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def play_audio(file_path):
    chunk = 4096
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    stream.stop_stream()
    stream.close()
    p.terminate()


def record_audio(duration, file_path):
    chunk = 4096
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


def analyze_audio(signal, threshold=1000):
    # 快速傅里叶变换
    spectrum = np.abs(scipy.fft.fft(signal))

    # 计算频谱能量
    energy = np.sum(spectrum)

    # 如果能量超过阈值，则认为存在声音
    return energy > threshold


# 获取已连接的wifi名称
def get_connected_wifi_name():
    result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "SSID" in line:
            wifi_name = line.split(":")[1].strip()
            return wifi_name
    return None

def connect_to_wifi(ssid, password=None):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]  # 获取第一个无线网卡
    profile = pywifi.Profile()  # 创建WiFi连接文件
    profile.ssid = ssid  # WiFi名称
    profile.auth = const.AUTH_ALG_OPEN  # 需要密码
    if password:
        profile.akm.append(const.AKM_TYPE_WPA2PSK)  # 加密类型
    else:
        profile.akm.append(const.AKM_TYPE_NONE)  # 无加密
    profile.cipher = const.CIPHER_TYPE_CCMP  # 加密单元
    profile.key = password  # WiFi密码

    iface.remove_all_network_profiles()  # 删除其他所有配置文件
    tmp_profile = iface.add_network_profile(profile)  # 加载配置文件

    iface.connect(tmp_profile)  # 连接WiFi
    time.sleep(5)  # 等待5秒以完成连接


def connect_to_wifi(network_name):
    command = f'netsh wlan connect name={network_name}'
    subprocess.run(command, shell=True)


def proc_exist(process_name):
    is_exist = False
    wmi = win32com.client.GetObject('winmgmts:')
    processCodeCov = wmi.ExecQuery('select * from Win32_Process where name=\"%s\"' % process_name)
    if len(processCodeCov) > 0:
        is_exist = True
    return is_exist


def win_to_android(test_type):
    if test_type == "8k_mega":
        x1 = mega_x1
        y1 = mega_y1
        x2 = mega_x2
        y2 = mega_y2
    if test_type == "edp_mega":
        x1 = edp_mega_x1
        y1 = edp_mega_y1
        x2 = edp_mega_x2
        y2 = edp_mega_y2

    app = Application(backend="win32")
    # try:
    app.start(setting_path)  # 打开设置
    time.sleep(10)
    logger.info("点击第一个点")
    pyautogui.click(x=x1, y=y1, clicks=1, interval=1, button='left', duration=0.0,
                    tween=pyautogui.linear)  # 点击切换系统按钮
    time.sleep(5)
    logger.info("点击第二个点")
    pyautogui.click(x=x2, y=y2, clicks=1, interval=1, button='left', duration=0.0,
                    tween=pyautogui.linear)  # 点击确定按钮


def compare_images(img1, img2):
    # 打开图片并转化为numpy数组
    i1 = np.array(Image.open(img1))
    i2 = np.array(Image.open(img2))

    # 计算两张图片的差异
    difference = np.sum((i1 - i2) ** 2)

    # 计算相似度
    similarity = 100 - (difference / float(i1.size))

    return similarity


def check_hdmi_in(test_type):

    app = Application(backend="win32")
    # if proc_exist('MagicHdmiRecord.exe') is False:
    #     logger.info("HDMI-IN应用未自动打开")
    #     return False
    # else:
    app.start(hdmi_in_path)  # 打开hdmi-in应用
    time.sleep(10)
    if test_type == "8k_mega":
        # 截图
        im = pyautogui.screenshot(region=(mega_hdmi_in_left_on_x, mega_hdmi_in_left_on_y, mega_hdmi_in_right_width, mega_hdmi_in_right_height))
        # 保存图片
        im.save(test_image_1)
        time.sleep(5)
        similarity = compare_images(test_image_1, hdmi_8k_mega_image_1)
    if test_type == "edp_mega":
        # 截图
        im = pyautogui.screenshot()
        # 保存图片
        im.save(test_image_1)
        time.sleep(5)
        similarity = compare_images(test_image_1, hdmi_edp_mega_image_1)
        logger.info(f"相似度为{similarity}%")
    if similarity > sim_check:
        return True
    if similarity <= sim_check:
        return False

def close_hdmi_in():
    if proc_exist('MagicHdmiRecord.exe'):
        os.system('TASKKILL /F /IM MagicHdmiRecord.exe')

# 获取当前设备上的USB存储设备，磁盘类的U盘无法识别
def get_current_usb_names():
    c = wmi.WMI()
    usb_names = []
    for disk in c.Win32_LogicalDisk(DriveType=2):
        usb_names.append(disk.VolumeName)
    logger.info('U盘列表如下')
    logger.info(usb_names)
    return usb_names

def compare_usb_names(config_usb_names, current_usb_names):
    missing_usb_names = [usb for usb in config_usb_names if usb not in current_usb_names]
    if missing_usb_names:
        logger.info(f'缺少U盘: {missing_usb_names}')
        return False
    else:
        logger.info('所有U盘都检测到了')
        return True

#获取当前设备上的相机列表
def get_camera_list():
    camera_list = []
    graph = FilterGraph()
    camera_name_lists = graph.get_input_devices()
    for camera_name in camera_name_lists:
        camera_list.append(camera_name)
    logger.info('相机列表如下')
    logger.info(camera_list)
    return camera_list

def compare_camera_names(config_camera_names, current_camera_names):
    missing_camera_names = [usb for usb in config_camera_names if usb not in current_camera_names]
    if missing_camera_names:
        logger.info(f'缺少相机: {missing_camera_names}')
        return False
    else:
        logger.info('所有相机都检测到了')
        return True

def get_volumes():
    # 创建一个COM对象
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    # 连接到本地计算机的WMI服务
    objSWbemServices = objWMIService.ConnectServer(".", "root\\cimv2")

    # 获取所有磁盘卷的信息
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Volume")

    for objItem in colItems:
        logger.info(objItem.Label)
        logger.info(objItem.DriveLetter)
        if objItem.Label == "PUBLICDISK" and objItem.DriveLetter is None:
            return True
    else:
        return False

def clean_old_mei_directories(exclude_dir=None):
    temp_dir = os.environ.get("TEMP")
    mei_dirs = glob.glob(os.path.join(temp_dir, '_MEI*'))

    current_time = time.time()

    for dir_path in mei_dirs:
        # 获取目录的修改时间
        dir_time = os.path.getmtime(dir_path)

        # 检查目录是否是最近创建的（例如，过去10分钟内）
        # 这个时间可以根据实际需要调整
        if current_time - dir_time > 600:  # 600秒，即10分钟
            try:
                if dir_path != exclude_dir:
                    shutil.rmtree(dir_path)
                    logger.info(f"删除目录: {dir_path}")
            except Exception as e:
                logger.info(f"删除 {dir_path} 目录报错: {e}")


def main(duration, record_path, play_path, single_thold, host_ip):
    host = host_ip  # 将此处替换为 A（服务器）的 IP 地址
    port = 12345

    logger.info(f"当前连接wifi为{get_connected_wifi_name()},需要连接的wifi为{wifi_name}")
    while get_connected_wifi_name() != wifi_name:
        # 连接到特定的WiFi网络
        if wifi_password == "None":
            connect_to_wifi(wifi_name)
        else:
            connect_to_wifi(wifi_name, wifi_password)
        logger.info(f'尝试连接wifi:{wifi_name}...')
        time.sleep(20)
    logger.info(f"已连接上wifi:{wifi_name}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 连接到服务器
    logger.info('尝试连接到服务器...')
    s.connect((host, port))
    logger.info('已连接到服务器')
    if success == "true":
        # 将success键的值改为false
        config.set('audio_message', 'success', 'false')
        with open('audio_test.ini', 'w', encoding='utf-8-sig') as configfile:
            config.write(configfile)
        logger.info("success 键的值为 true，程序继续运行。")
    else:
        logger.info("success 键的值不是 true，程序将停止运行。")
        sys.exit(0)
    while True:
        # 接收服务器的指令
        data = s.recv(1024)
        if data.decode() == '1':
            logger.info('已收到服务端连接码1')
            s.sendall(b'11')
            continue
        if data.decode() == '2':
            logger.info('已收到服务端连接码2,开始检测hdmiin画面')
            if check_hdmi_in(test_project) is True:
                logger.info('hdmiin画面检测通过，发送码20')
                s.sendall(b'20')
                continue
            if check_hdmi_in(test_project) is False:
                logger.info('hdmiin画面检测不通过，发送码21')
                s.sendall(b'21')
                continue

        if data.decode() == '3':
            logger.info("已收到码3，开始检查扬声器")
            s.sendall(b'32')
            time.sleep(2)
            logger.info("已发送码32，开始播放音频")
            play_audio(play_path)
            time.sleep(2)
            continue

        if data.decode() == '4':
            logger.info("收到码4，开始检查麦克风")
            s.sendall(b'42')
            logger.info("开始录音，录制指定时间")
            record_audio(duration, record_path)
            logger.info("分析录音数据，检查录音数据是否正常")
            wf = wave.open(record_path, 'rb')
            signal = wf.readframes(-1)
            signal = np.frombuffer(signal, dtype=np.int16)
            spectrum = np.abs(scipy.fft.fft(signal))
            # 计算频谱能量
            rms = np.sum(spectrum)
            logger.info(rms)
            if rms < single_thold:
                s.sendall(b'40')  # 30表示音频数据不达标，麦克风无声
                logger.info("麦克风无声，已发送码40")
                continue
            if rms > single_thold:
                s.sendall(b'41')  # 21表示音频数据达标，麦克风有声音
                logger.info("麦克风正常，已发送码41")
                continue

        if data.decode() == '5':
            logger.info("收到码5，开始切换系统")
            s.sendall(b'52')
            logger.info("开始切系统")
            time.sleep(100)
            logger.info("修改配置")
            config.set('audio_message', 'success', 'true')
            with open('audio_test.ini', 'w', encoding='utf-8-sig') as configfile:
                config.write(configfile)
                time.sleep(20)
            win_to_android(test_project)
            continue

        if data.decode() == '6':
            logger.info("收到码6，hdmi音频检测通过，开始关闭hdmiin应用")
            close_hdmi_in()
            continue

        if data.decode() == '7':
            logger.info("收到码7，开始检测U盘")
            if compare_usb_names(config_usb_names, get_current_usb_names()) is True:
                s.sendall(b'70')
                logger.info("U盘检测通过，已发送码70")
                continue
            if compare_usb_names(config_usb_names, get_current_usb_names()) is False:
                s.sendall(b'71')
                logger.info("U盘检测不通过，已发送码71")
                continue
        if data.decode() == '8':
            logger.info("收到码8，开始检测相机")
            if compare_camera_names(config_camera_names, get_camera_list()) is True:
                s.sendall(b'80')
                logger.info("相机检测通过，已发送码80")
                continue
            if compare_camera_names(config_camera_names, get_camera_list()) is False:
                s.sendall(b'81')
                logger.info("相机检测不通过，已发送码81")
                continue
        if data.decode() == '9':
            logger.info("收到码9，开始重启系统")
            s.sendall(b'92')
            logger.info("开始重启系统")
            time.sleep(60)
            logger.info("修改配置")
            config.set('audio_message', 'success', 'true')
            with open('audio_test.ini', 'w', encoding='utf-8-sig') as configfile:
                config.write(configfile)
                time.sleep(60)
            os.system('shutdown /r /t 1')
            continue

        if data.decode() == '100':
            logger.info("收到码100，开始检测公共分区")
            if get_volumes() is True:
                s.sendall(b'102')
                logger.info("公共分区检测通过，已发送码a1")
                continue
            if get_volumes() is False:
                s.sendall(b'101')
                logger.info("公共分区检测不通过，已发送码a0")
                continue
        if data.decode() == '110':
            logger.info("收到码110，开始关机")
            s.sendall(b'112')
            logger.info("开始关机")
            time.sleep(60)
            logger.info("修改配置")
            config.set('audio_message', 'success', 'true')
            with open('audio_test.ini', 'w', encoding='utf-8-sig') as configfile:
                config.write(configfile)
                time.sleep(60)
            os.system('shutdown /s /t 1')
            continue

        if data.decode() == '120':
            logger.info("收到码120，开始修改配置")
            time.sleep(100)
            config.set('audio_message', 'success', 'true')
            with open('audio_test.ini', 'w', encoding='utf-8-sig') as configfile:
                config.write(configfile)
                time.sleep(20)
            continue


if __name__ == '__main__':
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    LOG_ROOT = dirname
    logger = get_logger(f'audio_test.log')
    time.sleep(boot_delay)

    current_mei_dir = os.path.dirname(sys.executable)
    clean_old_mei_directories(exclude_dir=current_mei_dir)

    while True:
        try:
            main(record_time, recorded_file, audio_file, rms_single, host_ip)
        except Exception as run_error:
            logger.info(run_error)
