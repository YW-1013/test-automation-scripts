"""
一、多场景负载模拟
1、腾讯双人会议2小时----ok
2、使用高速SSD进行文件压缩和解压操作，模拟混合办公负载，持续30分钟----ok
3、PPT播放，持续30分钟----ok
4、视频格式转换/视频编辑----ok
5、本地4K视频播放，持续30分钟----ok
6、网络压测----ok
二、记录笔记本性能数据
1、CPU占用
2、GPU占用
3、内存占用
4、电池电量
5、功耗
6、温度
7、CPU频率
"""
import subprocess
import pyautogui
import configparser
import shutil
import zipfile
import win32gui
import ctypes
import os
import time
from moviepy.editor import VideoFileClip
import sys
import cv2
import pygame
import requests
import json
import psutil
import GPUtil
import wmi
import datetime


# 窗口状态常量
SW_SHOWMAXIMIZED = 3
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2

current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # 当前工作目录
config_path = os.path.join(current_working_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
paths = config['Paths']
urls = config['Urls']
settings = config['Settings']
tenxunmeeting_path = paths.get('tenxunmeeting_path')
meeting_code = settings.get('meeting_code')
meeting_time = settings.getint('meeting_time')
ppt_play_time = settings.getint('ppt_play_time')
play_duration = settings.getint('play_duration')
test_times = settings.getint('test_times')
test_url = urls.get('test_url')

image_dir = os.path.join(current_working_dir, 'images')
join_meeting_path = os.path.join(image_dir,"join_meeting.jpg")
join_meeting_botton = os.path.join(image_dir,"join_meeting_botton.jpg")
folder_path = os.path.join(current_working_dir,'test_folder')
ota_zip_path = os.path.join(current_working_dir,'H3C_1.0.7.6.zip')
video_dir = os.path.join(current_working_dir, 'videos')
log_path = os.path.join(current_working_dir, 'system_status_log.txt')
ppt_path = os.path.join(current_working_dir, 'test.pptx')


def click_button(image_path, confidence=0.6):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location is not None:
            pyautogui.click(location)
            time.sleep(1)  # 等待界面刷新
        else:
            print(f"未找到按钮: {image_path}")
    except Exception as e:
        print(f"点击按钮时发生错误: {e}")

#腾讯会议2H,参数为会议号、会议时长
def start_meeting():
    subprocess.Popen(tenxunmeeting_path)
    time.sleep(5)
    click_button(join_meeting_path)
    time.sleep(1)
    pyautogui.typewrite(meeting_code, interval=0.1)
    time.sleep(5)
    click_button(join_meeting_botton)
    time.sleep(meeting_time)
    pyautogui.hotkey('alt', 'f4')
    time.sleep(5)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.hotkey('alt', 'f4')
    time.sleep(2)


def compress_folder(folder_path):
    base_folder_name = os.path.basename(folder_path)
    parent_folder = os.path.dirname(folder_path)
    zip_file_name = f"{base_folder_name}_done.zip"
    zip_file_path = os.path.join(parent_folder, zip_file_name)

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    return zip_file_path


def decompress_folder(zip_file_path):
    base_file_name = os.path.basename(zip_file_path)
    base_name_without_extension = os.path.splitext(base_file_name)[0].replace('_done', '')
    extract_folder_name = f"{base_name_without_extension}_done"
    parent_folder = os.path.dirname(zip_file_path)
    extract_folder_path = os.path.join(parent_folder, extract_folder_name)

    with zipfile.ZipFile(zip_file_path, 'r') as zipf:
        zipf.extractall(extract_folder_path)

    return extract_folder_path


def cleanup_files(*file_paths):
    for file_path in file_paths:
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


#压缩解压文件，压缩解压一次共2分钟50S左右
def zip_and_unzip():
    # Step 1: Compress the folder and rename it
    zipped_file_path = compress_folder(folder_path)
    print(f'文件压缩至: {zipped_file_path}')

    # Step 2: Decompress the folder and rename it
    decompressed_folder_path = decompress_folder(zipped_file_path)
    print(f'文件解压至: {decompressed_folder_path}')

    # Step 3: Clean up the files
    cleanup_files(zipped_file_path, decompressed_folder_path)
    print(f'删除文件: {zipped_file_path} and {decompressed_folder_path}')


def is_maximized():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        # 定义 WINDOWPLACEMENT 结构体
        class WINDOWPLACEMENT(ctypes.Structure):
            _fields_ = [("length", ctypes.c_uint),
                        ("flags", ctypes.c_uint),
                        ("showCmd", ctypes.c_uint),
                        ("ptMinPosition", ctypes.wintypes.POINT),
                        ("ptMaxPosition", ctypes.wintypes.POINT),
                        ("rcNormalPosition", ctypes.wintypes.RECT)]

        # 创建一个 WINDOWPLACEMENT 对象并初始化其长度
        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)

        # 获取窗口显示状态
        ctypes.windll.user32.GetWindowPlacement(hwnd, ctypes.byref(placement))

        # 检查 showCmd 是否为最大化状态
        if placement.showCmd == SW_SHOWMAXIMIZED:
            return True
    return False

#全屏操作
def toggle_fullscreen():
    if not is_maximized():
        pyautogui.hotkey('win', 'up')  # 只有在当前不处于全屏时，才尝试进行全屏操作

#打开PPT进行自动放映----主运行
def open_and_play_ppt_with_wps():
    if not os.path.exists(ppt_path):
        raise FileNotFoundError(f"PPT 文件路径不存在: {ppt_path}")

    # 使用默认程序打开PPT文件（假设WPS Office是默认的PPT处理程序）
    subprocess.Popen(['start', ppt_path], shell=True)

    # 等待PPT文件完全打开
    time.sleep(5)
    toggle_fullscreen()
    time.sleep(5)


    # 模拟按键 'F5' 开始幻灯片放映
    pyautogui.hotkey('f5')

    # 等待放映一段时间（假设30秒）
    time.sleep(ppt_play_time)

    # 关闭WPS应用（假设WPS已经被激活）
    pyautogui.hotkey('alt', 'f4')
    time.sleep(5)
    pyautogui.hotkey('alt', 'f4')
    time.sleep(5)

#将指定视频进行格式转换，转换完成后删除转换后的视频；一轮转换本机测试7分钟左右
def convert_specific_video_to_mkv():
    # 检查输入文件是否存在
    input_filepath = os.path.join(video_dir, "change_fomat.mp4")
    if not os.path.exists(input_filepath):
        print(f"Input file does not exist: {input_filepath}")
        return

    # 确定输出文件路径
    output_filepath = os.path.join(video_dir, "change_fomat.mkv")
    print(output_filepath)

    # 使用moviepy进行格式转换
    try:
        clip = VideoFileClip(input_filepath)
        clip.write_videofile(output_filepath, codec='libx264')
        print(f"Converted {video_dir} to mkv")
    except Exception as e:
        print(f"Failed to convert {video_dir}: {e}")

    time.sleep(20)

    os.remove(output_filepath)


def play_video_in_loop():
    video_name = "change_fomat.mp4"
    """使用 OpenCV 和 Pygame 播放指定目录下的视频文件并循环播放，支持全屏、按Esc键退出和播放指定时长后自动退出"""
    video_path = os.path.join(video_dir, video_name)
    if not os.path.exists(video_path):
        print(f"Video file '{video_name}' not found in directory '{video_dir}'")
        return

    # 提取音频
    video = VideoFileClip(video_path)
    audio_path = video_path.replace(".mp4", ".mp3")
    video.audio.write_audiofile(audio_path)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 检查视频是否成功打开
    if not cap.isOpened():
        print(f"Failed to open video file: {video_name}")
        return

    # 初始化 Pygame
    pygame.init()
    pygame.mixer.init()
    pygame.display.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Video Playback")

    # 加载音频
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    start_time = time.time()  # 获取开始时间

    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重新定位到第0帧
        pygame.mixer.music.rewind()  # 音频也重新播放

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.transpose(frame)
            surface = pygame.surfarray.make_surface(frame)
            screen.blit(surface, (0, 0))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.mixer.music.stop()
                    pygame.quit()
                    return

                # 按 'Esc' 键退出播放
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    cap.release()
                    pygame.mixer.music.stop()
                    pygame.quit()
                    return

            # 检查是否超出指定播放时长
            if play_duration > 0 and (time.time() - start_time) >= play_duration:
                cap.release()
                pygame.mixer.music.stop()
                pygame.quit()
                return
    cap.release()
    pygame.mixer.music.stop()
    pygame.quit()


def download_file_and_delete_afterwards():
    """
    下载文件到指定目录，下载完成后删除文件。

    Parameters:
    url (str): 文件下载地址
    download_dir (str): 文件下载保存的目录
    """
    # 确保下载目录存在
    if not os.path.exists(current_working_dir):
        os.makedirs(current_working_dir)

    # 确定文件名
    filename = test_url.split("/")[-1]
    file_path = os.path.join(current_working_dir, filename)

    try:
        # 发送 HTTP 请求以获取文件
        response = requests.get(test_url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 打开文件以写入下载数据
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 过滤出空块
                    f.write(chunk)

        print(f"文件下载完成，保存路径: {file_path}")

    except requests.RequestException as e:
        print(f"下载过程中发生错误: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除下载失败的文件: {file_path}")
        return

    try:
        # 下载完成后删除文件
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"文件已删除: {file_path}")
        else:
            print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"删除文件时发生错误: {e}")

def get_token():
    url = "http://your-server.example.com/ota-api/auth/login"

    payload = json.dumps({
       "username": "admin",
       "password": "YOUR_PASSWORD"
    })
    headers = {
       'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
       'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response_data = response.json()
    access_token = response_data.get('data', {}).get('access_token')
    return access_token


def upload_files(token):
    url = "http://your-server.example.com/ota/file/full-package/upload-package"

    payload={}
    files=[
       ('file',(ota_zip_path,open(ota_zip_path,'rb'),'application/zip'))
    ]
    headers = {
       'Authorization': token,
       'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.text

#进行网络压测
def network_stress():
    download_file_and_delete_afterwards()
    time.sleep(5)
    upload_files(get_token())

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_gpu_usage():
    gpus = GPUtil.getGPUs()
    if gpus:
        return gpus[0].load * 100  # 获取第一个GPU的占用率
    return 0

def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent

def get_battery_info():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent
    return "No Battery Found"

def get_system_power_draw():
    try:
        # 获取整体功耗 (暂未实现，需要特定硬件支持)
        return "N/A"
    except:
        return "N/A"

def get_motherboard_temp():
    try:
        c = wmi.WMI(namespace="root/wmi")
        temperature_info = c.MSAcpi_ThermalZoneTemperature()
        for temp in temperature_info:
            return temp.CurrentTemperature / 10.0 - 273.15  # 转换为摄氏度
    except wmi.x_wmi as e:
        print(f"Error getting motherboard temperature: {e.com_error}")
        return "N/A"

def get_cpu_frequency():
    freq = psutil.cpu_freq()
    if freq:
        return freq.current
    return "N/A"

def record_system_info(message, log_file=log_path):

    with open(log_file, "a") as file:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cpu_usage = get_cpu_usage()
        gpu_usage = get_gpu_usage()
        memory_usage = get_memory_usage()
        battery_percent = get_battery_info()
        power_draw = get_system_power_draw()
        motherboard_temp = get_motherboard_temp()
        cpu_freq = get_cpu_frequency()

        log_entry = f"CPU：{cpu_usage}, GPU：{gpu_usage}, 内存：{memory_usage}, 电量：{battery_percent}, 功耗：{power_draw}, 温度：{motherboard_temp}, CPU频率：{cpu_freq}\n"
        print(log_entry.strip())  # 打印到控制台（方便调试）
        file.write(f"{current_time} {message}\n{log_entry}\n")
        file.flush()  # 确保内容写入文件

if __name__ == '__main__':
    for i in range(test_times):
        record_system_info(f"腾讯视频会议压测", log_file=log_path)
        #腾讯视频会议30分钟
        start_meeting()

        record_system_info(f"文件压缩解压压测", log_file=log_path)
        #文件压缩解压一次2分50秒
        for i in range(10):
            zip_and_unzip()
            time.sleep(5)

        record_system_info(f"PPT自动放映压测", log_file=log_path)
        #PPT自动放映30分钟
        open_and_play_ppt_with_wps()

        record_system_info(f"视频格式转换压测", log_file=log_path)
        #视频格式转换1次，一次7分钟，时长与电脑性能相关
        for change_video_times in range(3):
            convert_specific_video_to_mkv()
            time.sleep(5)

        record_system_info(f"本地4K视频播放压测", log_file=log_path)
        #本地播放4K视频30分钟
        play_video_in_loop()

        record_system_info(f"网络上传下载压测", log_file=log_path)
        #进行网络压测
        for network_stress_times in range(3):
            network_stress()
            time.sleep(5)