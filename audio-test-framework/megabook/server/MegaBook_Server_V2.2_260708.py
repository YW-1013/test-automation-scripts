# -*- coding: utf-8 -*-

"""
2026-7-8 修改点：
1、双系统切换新增"快速切换"方式：在"重启切换/休眠切换"基础上增加"快速切换"。Win->安卓方向不再让客户端逐像素点击控制中心，
   改为通知客户端(新增码6/ACK62)走 H3C SystemControl 的 WebSocket IPC 直接下发切换命令(见客户端 win_to_android_fast)。
   安卓->Win 方向因无对应IPC手段，仍沿用点击控制中心。快速切换后系统重启进安卓，服务端流程与重启切换一致。

2026-6-24 修改点：
1、修复客户端握手死循环：原 while response!="11" 循环内未重新 recv，遇到上一轮残留的半开/失效连接(recv返回空)时会无限刷"正在连接中"；改为循环内重新接收 + 空连接/超时即抛出由外层重新 accept，并对 conn 设置30秒超时
2、雷电模拟器启动兜底(reopen_power)：启动前清理多开器/VBox等全套残留进程(dnmultiplayer.exe/LdVBoxHeadless.exe)，校验 power_path 为有效文件，启动失败(WinError5)时给出明确排查提示(杀软白名单/残留进程/提权不匹配)，并用 cwd 指定工作目录
3、修复 kill_process_by_name 在中文系统把"没有找到进程"误判为 ERROR 的问题(关键词补"没有找到")
4、启动时检测管理员权限：非管理员运行时弹出UAC提权弹窗，以管理员身份重启自身(powercfg/杀进程/起模拟器/模拟键鼠等均需管理员权限)
5、修改版本名称：MegaBook_Server_V2.1_260624

2026-6-22 修改点：
1、双系统切换支持"光感检测"测试项：选择"双系统切换"方法时显示并可勾选"光感检测"（执行层仅在Win下检查，安卓下自动跳过）
2、双系统"休眠切换"卡死问题的服务端双保险：win轮长时间（约4次30秒超时）等不到Win客户端连接时，判定"安卓切Win"可能未成功，自动重新执行一次切换到Win并唤醒后继续监听，避免服务端误认为已在Win而无限死等

2026-6-12 修改点：
1、新增模块级 interruptible_sleep 函数，每 0.5 秒检查 is_running/is_paused 标志，替代原有阻塞式 time.sleep
2、将主测试循环及 control_devices 中所有 ≥10 秒的 time.sleep 替换为 interruptible_sleep，包括 on_off_interval、test_interval、1800s 等配置项等待
3、在 check_home_open、check_power_open、reopen_power、common_to_home_on、check_devices_status 等 helper 函数的 while 循环中加入 is_running 退出检查，防止停止/暂停信号卡在循环内无法响应
4、将 check_speaker、check_camera、check_udisk 中的长 time.sleep 替换为 interruptible_sleep
5、修复 toggle_pause：点"继续"时调用 update_button_text() 而非 update_button_pause_end()，确保恢复后暂停和停止按钮正常可用
6、修复 check_pause_and_stop 中 root.after(0, update_button_text()) 括号错误（原代码在工作线程直接执行 GUI 操作），改为正确的函数引用传递
2025-12-23修改点：
1、新增重启和开关机后检查桌面应用和小组件是否丢失
2025-8-6 修改点：
1、安卓下打开音视频文件适配VLC
2、把冗余路径删除，图像文件夹放在文件同目录image文件夹下
2025-7-28 修改点：
1、修改还是按智能生活的空闲按钮，增加容错项，判断安卓和win下只要是包含按键开机的，超过10次没有连接上客户端的话，那就再按一次，然后归零，继续尝试
2、增加报错信息详细解释，except中增加
2025-7-23 修改点：
1、把版本号等需要修改的地方都放在代码开头，防止后续遗漏
2、把start_test函数修改为back_home函数，规避关闭所有应用时launcher崩溃的问题
3、修改安卓下检测息屏后的时间，之前有个时间配置了10S，现在是用户自由配置了
4、新增关闭当前设备的自动更新
5、新增设置无操作睡眠和息屏的时间
6、修改按拇指机器人的方法，改为开关方式，避免按不到
7、修改版本号为MegaBook_Server_V1.6_250723
2025-7-22 修改点：
1、增加模拟器打开时间检测，并判断智能生活和向日葵是否存在
2、修改打开安卓下音视频播放器的方式，适配系统
3、修改安卓下切换windows的坐标点，适配系统
2025-7-10 修改点：
1、修改安卓下息屏时检测是否adb连接不上了
2、减少库
3、修改版本名称：MegaBook_Server_V1.5_250710
2025-7-8 修改点：
1、修改充电检测下导致开关机间隔不显示
2、增加检测设备连接状态后等待20S再去检测
3、修改版本号和设备名称统一模板为AudioTestMegaBook_V1.3_250708
2025-5-7 修改点：
1、单独新增megabook的脚本，与其他分离开
"""

from logging import handlers
import tkinter.messagebox as tkMessageBox
import subprocess
import ctypes
import logging
import sys
import cv2
import os
import time
import wave
import pyaudio
import numpy as np
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import font
import threading
import json
from multiprocessing import freeze_support
from locale import getpreferredencoding
import zipfile
import shutil
import socket
import pywifi
from pywifi import const
from uiautomator2 import connect
import requests
from pygrabber.dshow_graph import FilterGraph
import pythoncom
from tkinter import PhotoImage
import winreg
import traceback


def get_path():
    try:
        base_path = sys._MEIPASS  # pyinstaller打包后的路径
    except AttributeError:
        base_path = os.path.abspath(".")  # 当前工作目录的路径

    return base_path  # 返回实际路径


def _get_u2jar_meipass_path():
    """返回PyInstaller模式下u2.jar在_MEI临时目录中的路径，非PyInstaller模式返回None"""
    if not hasattr(sys, '_MEIPASS'):
        return None
    return os.path.join(sys._MEIPASS, 'uiautomator2', 'assets', 'u2.jar')


def restore_u2jar_if_needed():
    """若_MEI临时目录被OS清理导致u2.jar丢失，从程序目录备份自动恢复"""
    meipass_jar = _get_u2jar_meipass_path()
    if not meipass_jar or os.path.exists(meipass_jar):
        return
    if not os.path.exists(_U2JAR_STABLE_PATH):
        return
    os.makedirs(os.path.dirname(meipass_jar), exist_ok=True)
    shutil.copy2(_U2JAR_STABLE_PATH, meipass_jar)


# ANR「无响应」弹窗自动关闭 watcher（每个ip仅启动一个后台线程，避免频繁重连造成线程泄漏）
_anr_watcher_devices = {}  # ip -> Device


def _setup_anr_watchers(d, ip):
    """注册并启动 ANR「无响应」弹窗自动关闭 watcher。
    仅当界面同时出现"无响应/没有响应/未响应"文字与对应按钮时才点击，避免误点其他正常对话框；
    优先点"等待"(保留应用/launcher，不会把桌面关掉)，其次"确定"/"关闭应用"/"关闭"。"""
    if ip in _anr_watcher_devices:
        return
    anr = '//*[contains(@text,"无响应") or contains(@text,"没有响应") or contains(@text,"未响应")]'
    try:
        for btn in ('等待', '确定', '关闭应用', '关闭'):
            d.watcher.when(anr).when(f'//*[@text="{btn}"]').click()
        d.watcher.start(2.0)  # 每2秒轮询一次，发现ANR弹窗即自动点掉
        _anr_watcher_devices[ip] = d
    except Exception:
        pass


def _reset_anr_watchers(ip):
    """模拟器重启前调用：停止并清除旧 watcher，便于在新模拟器上重新建立。"""
    d = _anr_watcher_devices.pop(ip, None)
    if d is not None:
        try:
            d.watcher.stop()
            d.watcher.remove()
        except Exception:
            pass


def safe_u2_connect(ip):
    """封装uiautomator2 connect，connect前自动检查并恢复u2.jar，并确保ANR弹窗watcher已启动"""
    restore_u2jar_if_needed()
    d = connect(ip)
    _setup_anr_watchers(d, ip)
    return d


current_working_dir = get_path()
globals_file_path = os.path.dirname(os.path.realpath(sys.argv[0]))

# 携带 adb 环境：把随程序打包的 adb 目录加到进程 PATH 最前面，
# 这样脚本里所有 run_command("adb ...") 无需改动即可优先使用携带版 adb，
# 与目标机是否安装 adb 无关。打包(PyInstaller)后取 _MEIPASS/adb，直接跑 .py 时取脚本目录/adb。
_adb_dir = os.path.join(sys._MEIPASS, 'adb') if hasattr(sys, '_MEIPASS') \
    else os.path.join(globals_file_path, 'adb')
os.environ['PATH'] = _adb_dir + os.pathsep + os.environ.get('PATH', '')

# 备份u2.jar到程序目录，防止PyInstaller _MEI临时目录被系统维护任务清理后无法connect
_U2JAR_STABLE_PATH = os.path.join(globals_file_path, '_u2jar_backup', 'u2.jar')
if hasattr(sys, '_MEIPASS'):
    _u2jar_src = os.path.join(sys._MEIPASS, 'uiautomator2', 'assets', 'u2.jar')
    if os.path.exists(_u2jar_src) and not os.path.exists(_U2JAR_STABLE_PATH):
        os.makedirs(os.path.dirname(_U2JAR_STABLE_PATH), exist_ok=True)
        shutil.copy2(_u2jar_src, _U2JAR_STABLE_PATH)
requests.adapters.DEFAULT_RETRIES = 300
log_path = os.path.join(globals_file_path, 'logs')
current_time = datetime.now()
formatted_date = current_time.strftime("%m-%d")
monkey_log_path = os.path.join(log_path, f"monkey_{formatted_date}.log")
image_path = os.path.join(globals_file_path, 'image')
refresh_img_path = os.path.join(current_working_dir, 'refresh.png')
# 创建名为'image_path'的新文件夹，如果已经存在则忽略
if not os.path.exists(image_path):
    os.makedirs(image_path)

# 黑屏检测
template_similarity_image_path = os.path.join(image_path, "template_captured_frame.jpg")

# 安卓相机检测
video_test_template1 = os.path.join(image_path, "video_test_template1.jpg")
video_test_template2 = os.path.join(image_path, "video_test_template2.jpg")
video_test_image1 = os.path.join(image_path, "video_test_image1.jpg")
video_test_image2 = os.path.join(image_path, "video_test_image2.jpg")


test_wav_path = os.path.join(current_working_dir, 'test.wav')  # 测试音频的存放路径
win_speaker_path = os.path.join(globals_file_path, 'win_speaker_audio.wav')  # win测试扬声器的音频路径
test_wav_speaker_path = os.path.join(globals_file_path, 'recorded_speaker_audio.wav')  # 安卓测试本机录音文件的地址，即验证大屏的扬声器
test_wav_mic_path = os.path.join(globals_file_path, 'recorded_mic_audio.wav')  # 安卓测试大屏录音文件的地址，即验证大屏的麦克风
test_wav_mp4_path = os.path.join(globals_file_path, 'recorded_mic_audio.mp4')  # 安卓测试大屏录音文件视频的地址，用来分解为音频

# 设置版本号，统一写在一块，避免漏掉
root_title = 'MegaBook_Server_V2.2_260708'
process_name = "MegaBook_Server_V2.2_260708.exe"

is_running = True
# 定义全局变量test_count_var
global test_count_var
test_count_var = None

# 定义全局变量test_fail_count_var
global test_fail_count_var
test_fail_count_var = None

is_paused = False
global android_or_win
android_or_win = 'android'
global test_items_checkbuttons
test_items_checkbuttons = {}
global switch_mode_var
switch_mode_var = None
global switch_mode_label_widget
switch_mode_label_widget = None
global switch_mode_combobox_widget
switch_mode_combobox_widget = None


class TextHandler(logging.Handler):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # 自动滚动到底部
            self.text.yview(tk.END)

        # 在主线程中执行GUI操作
        self.text.after(0, append)


class DailyDateFileHandler(logging.FileHandler):
    """按日期自动切换日志文件，文件名格式：{prefix}_MM-DD.log，跨天后自动创建新文件"""

    def __init__(self, log_dir, prefix, encoding='utf-8'):
        self.log_dir = log_dir
        self.prefix = prefix
        self._current_date = datetime.now().strftime('%m-%d')
        filename = os.path.join(log_dir, f'{prefix}_{self._current_date}.log')
        super().__init__(filename, mode='a', encoding=encoding)

    def emit(self, record):
        current_date = datetime.now().strftime('%m-%d')
        if current_date != self._current_date:
            self._current_date = current_date
            if self.stream:
                self.stream.flush()
                self.stream.close()
                self.stream = None
            self.baseFilename = os.path.abspath(
                os.path.join(self.log_dir, f'{self.prefix}_{current_date}.log'))
            self.stream = self._open()
        super().emit(record)


def get_logger(log_prefix, level=logging.INFO, text_widget=None):
    logger = logging.getLogger(log_prefix)
    logger.setLevel(level)
    dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
    log_path = os.path.join(dirname, "logs")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fh = DailyDateFileHandler(log_path, log_prefix, encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    if text_widget:
        text_handler = TextHandler(text_widget)
        text_handler.setLevel(level)
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)

    return logger


def load_config(config_path, test_items):
    default_config = {
        'device_ip': '192.168.1.100',
        'power_ip': 'emulator-5554',
        'similarity': '0.8',
        'connect_wifi_name': '无',
        'wifi_password': "无",
        'rms_speaker': '100000000000',
        'rms_mic': '100000000000',
        'record_time': '10',
        'power_path': r'D:\leidian\LDPlayer9\dnplayer.exe',
        'test_interval': '80',
        'time_set_sleep': '300',
        'on_off_interval': '10',
        'power_process_name': 'dnplayer.exe',
        'selected_method': 'launcher重启',
        'test_project': 'megabook（单安卓或双系统切换）',
        'stop_type': '是',
        'switch_mode': '重启切换',
        'android_click_x': '1968',
        'android_click_y': '286',
        'bt_name': '',
        'selected_test_items': {item: True for item in test_items},
    }
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
    except:
        error_msg = traceback.format_exc()
        logger.info(f"错误日志信息{error_msg}")
        config = default_config
    return config


def save_config(config, config_path):
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)


def on_type_changed(event=None):
    global type_var
    global method_var
    global stop_var
    global method_combobox

    # 更新测试方法的选项
    if type_var.get() == 'megabook（单安卓或双系统切换）':
        method_combobox['values'] = (
            '双系统切换', 'launcher重启', 'launcher关机+home键开机+按键盘进入桌面', '电源键睡眠+键盘唤醒', '电源键睡眠+电源键唤醒+键盘进入桌面', '安卓下无操作睡眠+键盘唤醒',
            '电源键强制关机+电源键开机+键盘进入桌面', "无操作")
    elif type_var.get() == '单win（非双系统切换）':
        method_combobox['values'] = (
            'win菜单重启', 'win下电源键关机+电源键开机', 'win菜单关机+电源键开机', 'win下无操作息屏+键盘唤醒', 'win下无操作息屏+电源键唤醒+键盘进入桌面', 'win下无操作睡眠+键盘唤醒',
            'win下无操作睡眠+电源键唤醒+键盘进入桌面', 'win下电源键睡眠+电源键唤醒+按键盘进入桌面', 'win下电源键睡眠+按键盘进入桌面',
            'win菜单睡眠+电源键唤醒+按键盘进入系统', 'win菜单睡眠+按键盘进入系统', 'win下电源键休眠+电源键唤醒+按键盘进入桌面', 'win菜单休眠+电源键唤醒+按键盘进入系统',
            'win下电源键强制关机+电源键开机',"无操作")
    # 更新测试条目和配置项的可见性
    on_method_changed()


def on_method_changed(event=None):
    global type_var
    global method_var
    global stop_var
    global test_items_vars
    global test_items_checkbuttons  # 使用全局变量
    if type_var.get() == 'megabook（单安卓或双系统切换）':
        # 双系统切换时也允许选择"光感检测"（执行层仅在win下检查，安卓下自动跳过，见主循环'光感检测'分支）
        if method_var.get() == '双系统切换':
            megabook_visible = ['黑屏检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测','桌面组件检测', '麦克风+monkey检测', '空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测',
                                '充电检测', '光感检测', '蓝牙检测']
            megabook_hidden = ['驱动检测']
        else:
            megabook_visible = ['黑屏检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测','桌面组件检测', '麦克风+monkey检测', '空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测',
                                '充电检测', '蓝牙检测']
            megabook_hidden = ['驱动检测', '光感检测']
        for item in megabook_visible:
            test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
        for item1 in megabook_hidden:
            test_items_vars[item1].set(False)
            test_items_checkbuttons[item1].pack_forget()
    if type_var.get() == '单win（非双系统切换）':
        for item in ['黑屏检测', '驱动检测', '扬声器检测', '麦克风检测', '空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测', '充电检测', '光感检测', '蓝牙检测']:
            test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
        for item1 in ['扬声器+monkey检测', '麦克风+monkey检测','桌面组件检测']:
            test_items_vars[item1].set(False)
            test_items_checkbuttons[item1].pack_forget()

    update_config_visibility()


# 更新配置项的显示状态
def update_config_visibility():
    # 确保使用全局变量
    global method_var
    global stop_var
    global type_var
    global test_items_vars
    global config_labels
    global config_entries
    global config_items

    # 根据选择的测试方法更新配置项的可见性
    if method_var.get() in ['win菜单重启']:
        # 隐藏特定的配置项
        for key in ['power_ip', 'power_path', 'power_process_name', 'power_name', 'power_name_botton', 'android_or_win',
                    'on_off_interval', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval']:
            config_labels[key].grid()
            config_entries[key].grid()

    # 根据选择的测试方法更新配置项的可见性
    if method_var.get() in ['无操作']:
        # 隐藏特定的配置项
        for key in ['power_ip', 'power_path', 'power_process_name', 'power_name', 'power_name_botton', 'android_or_win',
                    'on_off_interval', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval']:
            config_labels[key].grid()
            config_entries[key].grid()


    elif method_var.get() in ['launcher重启']:
        # 隐藏特定的配置项
        for key in ['power_name_botton', 'android_or_win', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval', 'power_ip', 'power_path', 'power_process_name', 'power_name', 'on_off_interval']:
            config_labels[key].grid()
            config_entries[key].grid()

    elif method_var.get() in ['win下无操作睡眠+键盘唤醒', '安卓下无操作睡眠+键盘唤醒']:
        # 隐藏特定的配置项
        for key in ['power_name_botton', 'android_or_win']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval', 'power_ip', 'power_path', 'power_process_name', 'power_name', 'on_off_interval',
                    'time_set_sleep']:
            config_labels[key].grid()
            config_entries[key].grid()

    elif method_var.get() in ['win下无操作息屏+键盘唤醒']:
        # 隐藏特定的配置项
        for key in ['power_name_botton', 'android_or_win', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval', 'power_ip', 'power_path', 'power_process_name', 'power_name', 'on_off_interval']:
            config_labels[key].grid()
            config_entries[key].grid()

    elif method_var.get() in ['win下电源键关机+电源键开机', 'win菜单关机+电源键开机', 'win下电源键强制关机+电源键开机']:
        # 隐藏特定的配置项
        for key in ['power_name', 'android_or_win', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval', 'power_ip', 'power_path', 'power_process_name', 'power_name_botton',
                    'on_off_interval']:
            config_labels[key].grid()
            config_entries[key].grid()

    elif method_var.get() in ['win下电源键睡眠+电源键唤醒+按键盘进入桌面', 'win下电源键休眠+电源键唤醒+按键盘进入桌面', 'win菜单休眠+电源键唤醒+按键盘进入系统',
                              'win菜单睡眠+电源键唤醒+按键盘进入系统', 'launcher关机+home键开机+按键盘进入桌面', '电源键睡眠+电源键唤醒+键盘进入桌面',
                              '电源键强制关机+电源键开机+键盘进入桌面', '电源键睡眠+键盘唤醒']:
        # 隐藏特定的配置项
        for key in ['android_or_win', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval', 'power_ip', 'power_path', 'power_process_name', 'power_name', 'power_name_botton',
                    'on_off_interval']:
            config_labels[key].grid()
            config_entries[key].grid()

    elif method_var.get() in ['win下无操作息屏+电源键唤醒+键盘进入桌面']:
        # 隐藏特定的配置项
        for key in ['android_or_win', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['test_interval', 'power_ip', 'power_path', 'power_process_name', 'power_name', 'power_name_botton',
                    'on_off_interval']:
            config_labels[key].grid()
            config_entries[key].grid()


    elif method_var.get() == '双系统切换':
        for key in ['on_off_interval', 'power_name_botton', 'time_set_sleep']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['android_or_win', 'power_ip', 'power_path', 'power_name', 'test_interval', 'power_process_name',
                    'android_click_x', 'android_click_y']:
            config_labels[key].grid()
            config_entries[key].grid()
        if switch_mode_label_widget:
            switch_mode_label_widget.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))
            switch_mode_combobox_widget.pack(side=tk.TOP, fill=tk.X)

    if not test_items_vars['扬声器检测'].get() and not test_items_vars['扬声器+monkey检测'].get():
        config_labels['rms_speaker'].grid_remove()
        config_entries['rms_speaker'].grid_remove()
    else:
        config_labels['rms_speaker'].grid()
        config_entries['rms_speaker'].grid()

    if not test_items_vars['麦克风检测'].get() and not test_items_vars['麦克风+monkey检测'].get():
        config_labels['rms_mic'].grid_remove()
        config_entries['rms_mic'].grid_remove()
    else:
        config_labels['rms_mic'].grid()
        config_entries['rms_mic'].grid()

    if not test_items_vars['扬声器检测'].get() and not test_items_vars['麦克风检测'].get() and not test_items_vars[
        '扬声器+monkey检测'].get() and not test_items_vars['麦克风+monkey检测'].get():
        config_labels['record_time'].grid_remove()
        config_entries['record_time'].grid_remove()
    else:
        config_labels['record_time'].grid()
        config_entries['record_time'].grid()

    if not test_items_vars['U盘检测'].get():
        config_labels['u_disk_name'].grid_remove()
        config_entries['u_disk_name'].grid_remove()
    else:
        config_labels['u_disk_name'].grid()
        config_entries['u_disk_name'].grid()

    if not test_items_vars['蓝牙检测'].get():
        config_labels['bt_name'].grid_remove()
        config_entries['bt_name'].grid_remove()
    else:
        config_labels['bt_name'].grid()
        config_entries['bt_name'].grid()

    if not test_items_vars['充电检测'].get():
        config_labels['power_name_power'].grid_remove()
        config_entries['power_name_power'].grid_remove()
        config_labels['power_sn'].grid_remove()
        config_entries['power_sn'].grid_remove()

    else:
        config_labels['power_name_power'].grid()
        config_entries['power_name_power'].grid()
        config_labels['power_sn'].grid()
        config_entries['power_sn'].grid()
        config_labels['on_off_interval'].grid()
        config_entries['on_off_interval'].grid()

    if not test_items_vars['黑屏检测'].get() and not test_items_vars['相机检测'].get() and not test_items_vars['桌面组件检测'].get():
        config_labels['similarity'].grid_remove()
        config_entries['similarity'].grid_remove()
    else:
        config_labels['similarity'].grid()
        config_entries['similarity'].grid()

    if not test_items_vars['桌面组件检测'].get():
        config_labels['launcher_num'].grid_remove()
        config_entries['launcher_num'].grid_remove()
    else:
        config_labels['launcher_num'].grid()
        config_entries['launcher_num'].grid()

    if type_var.get() == '单win（非双系统切换）':
        config_labels['device_ip'].grid_remove()
        config_entries['device_ip'].grid_remove()
    else:
        config_labels['device_ip'].grid()
        config_entries['device_ip'].grid()

    if method_var.get() != '双系统切换':
        config_labels['android_click_x'].grid_remove()
        config_entries['android_click_x'].grid_remove()
        config_labels['android_click_y'].grid_remove()
        config_entries['android_click_y'].grid_remove()
        if switch_mode_label_widget:
            switch_mode_label_widget.pack_forget()
            switch_mode_combobox_widget.pack_forget()


def frame_main():
    # 确保使用全局变量
    global method_var
    global stop_var
    global type_var
    global test_items_vars
    global config_labels
    global config_entries
    global config_items
    global start_button
    global stop_button
    global pause_button
    global test_count_var
    global test_fail_count_var
    global log_text
    global method_combobox
    global stop_combobox
    global logger

    test_items_vars = {}

    # 创建主窗口
    root = tk.Tk()
    root.title(root_title)

    def on_closing():
        logging.shutdown()  # 清理日志系统
        root.destroy()

    def refresh_camera_list():
        """刷新摄像头列表"""
        camera_list = get_camera_list()  # 获取最新的摄像头列表
        camera_combobox['values'] = camera_list  # 更新Combobox的值列表
        if camera_list:
            camera_combobox.set(camera_list[0])  # 默认选择第一个摄像头（可根据实际要求调整）
        else:
            camera_combobox.set("")  # 如果没有摄像头，清空选择

    root.protocol("WM_DELETE_WINDOW", on_closing)

    test_count_var = tk.StringVar()
    test_fail_count_var = tk.StringVar()

    # 加粗且放大字体
    bold_large_font = font.Font(family='Helvetica', size=12, weight='bold')
    # 只加粗不放大字体
    bold_font = font.Font(family='Helvetica', size=10, weight='bold')  # 假设默认大小为10

    # 创建主Frame用于放置所有的控件
    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 创建左侧的Frame用于放置选择测试方法和测试项的控件
    left_frame = ttk.LabelFrame(main_frame, text="测试选择", padding="10 10 10 10",
                                labelwidget=ttk.Label(text="测试选择", font=bold_large_font))
    left_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # 创建右侧的Frame用于放置测试配置的控件
    right_frame = ttk.LabelFrame(main_frame, text="配置", padding="10 10 10 10",
                                 labelwidget=ttk.Label(text="配置", font=bold_large_font))
    right_frame.grid(column=1, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    main_frame.columnconfigure(1, weight=1)

    # 创建用于显示日志的Text控件
    log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10 10 10 10",
                               labelwidget=ttk.Label(text="日志", font=bold_large_font))
    log_frame.grid(column=2, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    main_frame.columnconfigure(2, weight=1)
    log_text = tk.Text(log_frame, wrap='word', state='disabled', height=15, width=50)
    log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    logger = get_logger('audio_test', text_widget=log_text)

    # 第一项 - 选择测试项目
    type_label = ttk.Label(left_frame, text="选择测试项目", font=bold_font)
    type_label.pack(side=tk.TOP, anchor=tk.W)

    type_var = tk.StringVar()
    type_combobox = ttk.Combobox(left_frame, textvariable=type_var, state='readonly')
    type_combobox['values'] = ('megabook（单安卓或双系统切换）', "单win（非双系统切换）")
    type_combobox.pack(side=tk.TOP, fill=tk.X)
    type_var.set("megabook（单安卓或双系统切换）")
    type_combobox.bind('<<ComboboxSelected>>', on_type_changed)

    # 第二项 - 选择测试方法
    method_label = ttk.Label(left_frame, text="选择测试方法", font=bold_font)
    method_label.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))

    method_var = tk.StringVar()
    method_combobox = ttk.Combobox(left_frame, textvariable=method_var, state='readonly')
    method_combobox['values'] = (
        'win菜单重启', 'win下无操作息屏+键盘唤醒', 'win下无操作息屏+电源键唤醒+键盘进入桌面', 'win下无操作睡眠+键盘唤醒', 'win下电源键关机+电源键开机', 'win菜单关机+电源键开机',
        'win下电源键睡眠+电源键唤醒+按键盘进入桌面',
        'win下电源键休眠+电源键唤醒+按键盘进入桌面', 'win下电源键强制关机+电源键开机', 'win菜单休眠+电源键唤醒+按键盘进入系统', 'win菜单睡眠+电源键唤醒+按键盘进入系统', 'launcher重启',
        '安卓下无操作睡眠+键盘唤醒', '双系统切换', 'launcher关机+home键开机+按键盘进入桌面', '电源键睡眠+电源键唤醒+键盘进入桌面',
        '电源键强制关机+电源键开机+键盘进入桌面', '电源键睡眠+键盘唤醒', "无操作")
    method_combobox.pack(side=tk.TOP, fill=tk.X)
    method_var.set("launcher重启")
    method_combobox.bind('<<ComboboxSelected>>', on_method_changed)

    # 双系统切换方式（重启切换 / 休眠切换），仅在选择双系统切换时显示
    global switch_mode_var
    global switch_mode_label_widget
    global switch_mode_combobox_widget
    switch_mode_var = tk.StringVar()
    switch_mode_label_widget = ttk.Label(left_frame, text="双系统切换方式", font=bold_font)
    switch_mode_combobox_widget = ttk.Combobox(left_frame, textvariable=switch_mode_var, state='readonly')
    switch_mode_combobox_widget['values'] = ('重启切换', '休眠切换', '快速切换')
    switch_mode_var.set('重启切换')
    # 默认隐藏，等 update_config_visibility 按需显示

    # 第三项 - 选择失败是否停止
    stop_label = ttk.Label(left_frame, text="失败是否停止", font=bold_font)
    stop_label.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))

    stop_var = tk.StringVar()
    stop_combobox = ttk.Combobox(left_frame, textvariable=stop_var, state='readonly')
    stop_combobox['values'] = ('是', '否')
    stop_combobox.pack(side=tk.TOP, fill=tk.X)
    stop_var.set("是")

    # 第五项：定义摄像头选项的一些变量
    global camera_var
    camera_var = tk.StringVar()
    camera_list = get_camera_list()
    # 准备刷新图标
    try:
        refresh_icon = PhotoImage(file=refresh_img_path)  # 图标路径
    except Exception as e:
        logger.info(f"无法加载图标: {e}")
        refresh_icon = None  # 如果图片加载失败，处理此情况

    # 创建和设置摄像头选择部分，位于选择方法和配置之间
    camera_label = ttk.Label(left_frame, text="选择摄像头", font=bold_font)
    camera_label.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))

    camera_frame = ttk.Frame(left_frame)  # 用于放置下拉框和按钮的Frame
    camera_frame.pack(side=tk.TOP, fill=tk.X)

    camera_combobox = ttk.Combobox(camera_frame, textvariable=camera_var, state='readonly')
    camera_list = get_camera_list()
    camera_combobox['values'] = camera_list
    camera_combobox.set("")  # 默认文本提示
    camera_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # 创建一个刷新摄像头的小图标按钮并绑定事件
    refresh_button = ttk.Button(camera_frame, image=refresh_icon, command=refresh_camera_list)
    refresh_button.pack(side=tk.LEFT, padx=5)

    # 第四项 - 选择测试项
    test_items_label = ttk.Label(left_frame, text="选择测试项", font=bold_font)
    test_items_label.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))

    # 填充测试项到列表框中，并默认全选这些项
    test_items = ['黑屏检测', '驱动检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测','桌面组件检测', '麦克风+monkey检测', '空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测',
                  '充电检测', '光感检测', '蓝牙检测']

    # 创建勾选框
    test_items_vars = {item: tk.BooleanVar(value=True) for item in test_items}
    for item, var in test_items_vars.items():
        checkbutton = ttk.Checkbutton(left_frame, text=item, variable=var)
        checkbutton.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)
        test_items_checkbuttons[item] = checkbutton  # 保存引用

    # 第六项 - 填写测试配置
    config_label = ttk.Label(right_frame, text="填写测试配置", font=bold_font)
    config_label.grid(column=0, row=0, columnspan=2, sticky=tk.W, pady=5)

    # 测试配置项的名称和提示文本
    config_items = [
        ('device_ip', '大屏IP'),
        ('android_or_win', '当前系统（android or win）'),
        ('similarity', '相似度阈值（0~1之间的小数）'),
        ('launcher_num', 'launcher页面数量(填整数)'),
        ('power_ip', '模拟器IP'),
        ('connect_wifi_name', '连接的wifi名称(不连wifi填无)'),
        ('wifi_password', 'wifi密码（无密码填无）'),
        ('time_set_sleep', '安卓下无操作睡眠时间（单位为秒）'),
        ('rms_speaker', '扬声器阈值'),
        ('rms_mic', '麦克风阈值'),
        ('record_time', '录音时长'),
        ('u_disk_name', 'U盘名称(多个以英文,分隔)'),
        ('bt_name', '蓝牙名称(多个以英文,分隔)'),
        ('power_path', '模拟器应用的安装地址'),
        ('power_process_name', '模拟器进程名称'),
        ('power_name', '键盘处智能设备名称'),
        ('power_name_botton', '电源键处智能设备名称'),
        ('android_click_x', '安卓切换Win点击坐标X'),
        ('android_click_y', '安卓切换Win点击坐标Y'),
        ('power_name_power', '智能插座名称'),
        ('power_sn', '智能插座端口'),
        ('on_off_interval', '关机-开机间隔（只填数字，单位S）'),
        ('test_interval', '开机-执行间隔（只填数字，单位S）'),
        ('test_message', '测试项目-机器-人员')
    ]

    for checkbutton_var in test_items_vars.values():
        checkbutton_var.trace('w', lambda *args: update_config_visibility())
    # 用于存储配置项输入框变量的字典
    config_vars = {}
    config_labels = {}
    config_entries = {}
    # 读取配置文件
    config_path = 'config_megabook.json'
    loaded_config = load_config(config_path, test_items)
    # 为每个配置项创建一个标签和一个输入框
    for index, (key, label_text) in enumerate(config_items):
        # 创建标签
        label = ttk.Label(right_frame, text=label_text)
        label.grid(column=0, row=index + 1, sticky=tk.W, pady=2)
        config_labels[key] = label

        entry_var = tk.StringVar()
        entry = ttk.Entry(right_frame, textvariable=entry_var)
        entry.grid(column=1, row=index + 1, sticky=(tk.W, tk.E), pady=2)
        config_entries[key] = entry
        config_vars[key] = entry_var

    for key, value in loaded_config.items():
        if key == 'test_project':
            type_var.set(value)  # 设置测试项目
        if key == 'selected_method':
            method_var.set(value)  # 设置测试方法
        if key == 'stop_type':
            stop_var.set(value)  # 设置停止方式
        if key == 'switch_mode':
            switch_mode_var.set(value)  # 设置双系统切换方式
        elif key == 'selected_test_items':
            for item, selected in value.items():
                test_items_vars[item].set(selected)  # 设置测试项
        else:
            clean_key = key.strip()
            if clean_key in config_vars:
                config_vars[clean_key].set(value)

    # 初始化界面
    update_config_visibility()
    on_type_changed()

    right_frame.columnconfigure(1, weight=1)

    for i in range(len(config_items) + 1):
        right_frame.rowconfigure(i, weight=1)

    # 第四项-创建底部按钮Frame
    bottom_frame = ttk.Frame(main_frame, padding="10 10 10 10")
    bottom_frame.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E))
    main_frame.rowconfigure(1, weight=0)

    # 创建一个用于均匀分布控件的容器Frame
    buttons_frame = ttk.Frame(bottom_frame)
    buttons_frame.pack(side=tk.LEFT, expand=False, fill=tk.X)

    # 创建一个用于显示标签和按钮的容器Frame
    labels_frame = ttk.Frame(bottom_frame)
    labels_frame.pack(side=tk.LEFT, expand=True, fill=tk.Y)

    # 创建显示当前压测次数的标签
    test_count_var.set("压测次数：0次")
    test_count_label = ttk.Label(labels_frame, textvariable=test_count_var)
    test_count_label.pack(side=tk.TOP, expand=True)

    # 创建显示当前压测失败次数的标签，并使用红色字体
    test_fail_count_var.set("失败次数：0次")
    test_fail_count_label = ttk.Label(labels_frame, textvariable=test_fail_count_var, style='Red.TLabel')
    test_fail_count_label.pack(side=tk.TOP, expand=True)

    # 创建开始按钮
    start_button = ttk.Button(bottom_frame, text="开始",
                              command=lambda: on_start_button_clicked(config_vars, root, logger))
    start_button.pack(side=tk.LEFT, expand=True)

    # 创建暂停按钮
    pause_button = ttk.Button(bottom_frame, text="暂停", command=lambda: toggle_pause(logger), state=tk.DISABLED)
    pause_button.pack(side=tk.LEFT, expand=True)

    # 创建结束按钮
    stop_button = ttk.Button(bottom_frame, text="结束", command=lambda: on_stop_button_clicked(logger), state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, expand=True)

    # 创建结束按钮
    open_logs = ttk.Button(bottom_frame, text="打开日志文件夹", command=on_open_log_folder_clicked)
    open_logs.pack(side=tk.LEFT, expand=True)

    # 设置主窗口的最小大小
    root.minsize(1200, 700)

    # 设置main_frame的网格权重，确保它可以扩展到整个窗口
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # 开始主循环
    root.mainloop()


def update_button_states(logger):
    start_button['state'] = tk.NORMAL  # 启用开始按钮
    pause_button['state'] = tk.DISABLED  # 禁用暂停按钮
    stop_button['state'] = tk.DISABLED  # 禁用结束按钮


def update_button_pause_end():
    pause_button['state'] = tk.DISABLED  # 禁用暂停按钮
    stop_button['state'] = tk.DISABLED  # 禁用结束按钮


def update_button_text():
    global pause_button
    if is_paused:
        pause_button.config(text="继续")
        pause_button['state'] = tk.NORMAL  # 启用暂停按钮
    else:
        pause_button.config(text="暂停")
        stop_button['state'] = tk.NORMAL  # 启用结束按钮
        pause_button['state'] = tk.NORMAL  # 启用暂停按钮


# 定义结束按钮的事件函数
def on_stop_button_clicked(logger):
    # 使用 global 关键字声明修改全局变量
    global is_running
    is_running = False
    logger.info("测试结束按钮已被点击,程序即将停止运行,请等待")
    update_button_pause_end()  # 调用更新按钮状态的函数


def on_start_button_clicked(config_vars, root, logger):
    log_text.configure(state="normal")
    log_text.delete("1.0", tk.END)
    log_text.configure(state="disabled")

    selected_camera = camera_var.get()
    if test_items_vars['黑屏检测'].get():
        if not selected_camera:
            tk.messagebox.showerror("错误", "请选择一个摄像头")
            return

    # 获取所有配置项的值
    configs_to_save = {k: v.get() for k, v in config_vars.items()}

    # 获取并保存测试项目
    configs_to_save['test_project'] = type_var.get()

    # 获取并保存测试方法
    configs_to_save['selected_method'] = method_var.get()

    # 获取并保存停止方式
    configs_to_save['stop_type'] = stop_var.get()

    # 获取并保存双系统切换方式
    configs_to_save['switch_mode'] = switch_mode_var.get()

    # 获取并保存选中的测试项
    configs_to_save['selected_test_items'] = {item: var.get() for item, var in test_items_vars.items()}
    # 保存到配置文件
    save_config(configs_to_save, 'config_megabook.json')

    # 获取测试项目
    test_project = type_var.get()

    # 获取测试方法
    selected_method = method_var.get()

    # 获取停止方式
    stop_type = stop_var.get()

    # 获取双系统切换方式
    switch_mode = switch_mode_var.get()

    # 获取所有选中的测试项
    selected_test_items = [item for item, var in test_items_vars.items() if var.get()]

    # 获取测试配置
    test_configs = {key: var.get() for key, var in config_vars.items()}
    missing_configs = [key for key, value in test_configs.items() if
                       value == '' and config_entries[key].winfo_viewable()]
    if missing_configs:
        # 弹出提示框，告知用户哪些配置项未填写
        missing_configs_str = ", ".join(missing_configs)
        tk.messagebox.showerror("错误", f"以下测试配置项未填写，请填写后再开始测试：{missing_configs_str}")
        return  # 退出函数，不开始测试

    test_thread = threading.Thread(target=on_start,
                                   args=(test_project, selected_method, stop_type, selected_test_items, test_configs,
                                         selected_camera, switch_mode, root, logger))
    test_thread.start()
    start_button['state'] = tk.DISABLED  # 禁用开始按钮
    pause_button['state'] = tk.NORMAL  # 启用暂停按钮
    stop_button['state'] = tk.NORMAL  # 启用结束按钮


# 定义按钮点击事件的处理函数
def on_open_log_folder_clicked():
    os.startfile(log_path)


def run_command(command):
    process = subprocess.Popen(
        command,
        bufsize=10000,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    out, err = process.communicate()

    # 没有必要关闭 process.stdin, 因为没有使用
    if process.stdout:
        process.stdout.close()
    if process.stderr:
        process.stderr.close()

    try:
        process.kill()
    except OSError:
        pass

    return out.decode()


def get_adb_devices():
    # 运行 'adb devices' 命令并解析设备列表
    output = run_command('adb devices')
    devices = output.strip().split('\n')[1:]
    return devices


# 安卓设备回到桌面
def start_test(d, logger):
    d.app_stop_all()
    logger.info("已关闭所有应用")
    time.sleep(5)


def back_to_home(ip, logger):
    run_command(f"adb -s {ip} shell input keyevent 3 ")
    logger.info("已回到桌面")
    time.sleep(5)


# 安卓设备开始录屏
def android_record(d):
    d.open_notification()
    d(descriptionContains="屏幕录制").long_click()
    if "关" in d(resourceId="com.h3c.screencap:id/microphoneIv").get_text():  # 判断如何没有开麦克风的话，需要开启麦克风
        d(resourceId="com.h3c.screencap:id/microphoneIv").click()
    d(text="开始录制").long_click()


# 安卓设备结束录屏,并保存录屏文件到本地
def android_stop_record(d):
    try:
        d(descriptionContains="正在录制屏幕").click()
        d(text="确定").click()
    except:
        d.open_notification()
        d(descriptionContains="结束录制").click()


# 安卓设备录屏后复制录屏文件到本地,并分解录屏文件为录音文件
def copy_to_local(ip, logger):
    logger.info("从安卓设备复制录音文件到本地")
    file_name = adb_check_files(ip)[0]
    run_command(
        f"adb -s {ip} pull /sdcard/Movies/{file_name} {globals_file_path}/{file_name}")
    cmd_command = f"ffmpeg.exe -i {file_name} -vn recorded_mic_audio.wav"
    os.chdir(globals_file_path)  # 将当前工作目录更改为指定的文件夹路径
    run_command(cmd_command)


# 复制本地的音频文件到安卓设备
def copy_to_android(device_ip, logger):
    try:
        run_command(f"adb -s {device_ip} shell  mkdir /sdcard/AAA")
    except Exception as makdir_error:
        logger.info(makdir_error)
    logger.info("复制本地的音频文件到安卓设备")
    run_command(f"adb -s {device_ip} push {current_working_dir}/test.wav /sdcard/AAA")


# 安卓设备上播放音频
def play_audio_android(ip, d):
    run_command(f"adb -s {ip} shell am start com.h3c.filemanager/.ui.ActivityMain")
    time.sleep(5)
    d(text="本地").click(timeout=2)
    time.sleep(5)
    d(text="AAA").click(timeout=2)
    d(text="test.wav").click(timeout=2)
    if d(text="MX 播放器").exists(timeout=2):
        d(text="MX 播放器").click()
    if d(text="音视频播放器").exists(timeout=2):
        d(text="音视频播放器").click()
    if d(text="VLC").exists(timeout=2):
        d(text="VLC").click()
    if d(text="始终").exists(timeout=1):
        d(text="始终").click()


# 本地设备上播放音频
def play_audio_local(file_path):
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


# 本地设备开始录音
def local_record(duration, file_path):
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


# 分析录音数据
def analysis_audio(record_path, logger):
    logger.info("开始分析录音数据")
    with wave.open(record_path, 'rb') as wf:
        signal = wf.readframes(-1)
        arr = np.frombuffer(signal, dtype=np.int16)
        spectrum = np.abs(np.fft.fft(arr))
        rms = np.sum(spectrum)
    logger.info(f"声音值为：{rms}")
    return rms


# 重启安卓设备-电源菜单重启
def reboot_android(logger, d, ip):
    back_to_home(ip, logger)
    d.open_notification()
    d(description="电源菜单").click()
    d(text="重启").click()


# 关机安卓设备-电源菜单关机
def shutdown_android(logger, d, ip):
    back_to_home(ip, logger)
    d.open_notification()
    d(description="电源菜单").click()
    d(text="关机").click()


def kill_process_by_name(process_name, logger):
    # 自动补全.exe后缀并转小写
    target_name = process_name.lower().rstrip(".exe") + ".exe"
    killed = False

    try:
        # 使用taskkill强制终止进程
        subprocess.run(
            ["taskkill", "/F", "/IM", target_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logger.info(f"进程 {target_name} 已被终止")
        killed = True
    except subprocess.CalledProcessError as e:
        # 解析错误信息（兼容中英文系统）
        error_msg = e.stderr.decode(getpreferredencoding(), errors="ignore").strip().lower()

        if any(keyword in error_msg for keyword in ["could not find", "not found", "找不到", "没有找到"]):
            logger.info(f"没有找到进程 {target_name}")
        else:
            logger.error(f"终止进程时发生错误: {error_msg.split(':')[-1].strip()}")

    return killed


def reopen_power(power_process_name, power_path, logger, power_ip):
    _reset_anr_watchers(power_ip)  # 重启前清掉旧模拟器上的ANR watcher，重连后在新模拟器上重建
    logger.info("杀掉模拟器进程")
    # 雷电是多进程：只杀dnplayer.exe不够，残留的多开器/VBox虚拟机进程会占用资源导致再次启动被拒(WinError5)
    for _pname in dict.fromkeys([power_process_name, "dnplayer.exe", "dnmultiplayer.exe", "LdVBoxHeadless.exe"]):
        kill_process_by_name(_pname, logger)
    interruptible_sleep(10)
    logger.info("重新打开模拟器")
    if not os.path.isfile(power_path):
        logger.error(f"模拟器路径无效(不是文件): {power_path}，请检查配置 power_path 是否为 dnplayer.exe 的完整路径")
        return
    try:
        app1 = subprocess.Popen([power_path], cwd=os.path.dirname(power_path))
    except PermissionError as e:
        logger.error(f"启动模拟器被拒绝(WinError5): {e}。排查方向：①安全软件/Defender受控文件夹访问拦截脚本启动模拟器，请将本程序和dnplayer.exe加入白名单；②上一轮模拟器后台进程(LdVBoxHeadless.exe等)未清干净；③管理员权限与模拟器不匹配(可手动右键以管理员身份运行雷电验证)。临时可手动打开雷电后重试。")
        return
    for i in range(30):
        if not is_running:
            return
        try:
            d = safe_u2_connect(power_ip)
            if d(text="智能生活").exists() or d(text="向日葵远程控制").exists():
                break
        except:
            logger.info("还未连接模拟器")
        time.sleep(5)


def common_to_home_on(power_ip, power_name, logger):
    d = safe_u2_connect(power_ip)
    # 获取设备的屏幕尺寸
    screen_height = d.info['displayHeight']
    screen_width = d.info['displayWidth']
    outer_retry = 0
    while d(text="空闲").exists(timeout=5) is False or d(text=power_name).exists(timeout=5) is False:
        if not is_running:
            return
        # 整体重试上限：避免模拟器异常时无限空转；超限抛异常由 check_home_open 兜底重启模拟器
        outer_retry += 1
        if outer_retry > 10:
            raise RuntimeError("多次尝试仍无法进入拇指机器人「空闲」页面，判定模拟器/桌面异常，触发重启模拟器")
        recheck = 0
        # 当前在其他机器人详情页（能看到"空闲"但找不到目标机器人名称），需重新打开应用回到列表
        if d(text="空闲").exists(timeout=2) and d(text=power_name).exists(timeout=2) is False:
            logger.info(f"当前在其他机器人页面，重新打开应用寻找{power_name}")
            start_test(d, logger)
            interruptible_sleep(15)
        # 找不到「智能生活」图标的重试上限：原为无限循环，模拟器launcher异常(如ANR无响应)时会一直刷
        # "已关闭所有应用"卡死；超限即抛异常，由 check_home_open 的 except 触发 reopen_power 重启模拟器自愈。
        smart_life_retry = 0
        while d(text="智能生活").exists(timeout=5) is False:
            if not is_running:
                return
            smart_life_retry += 1
            if smart_life_retry > 6:
                raise RuntimeError("多次未找到「智能生活」图标，判定模拟器launcher/桌面异常(疑似ANR无响应)，触发重启模拟器")
            logger.info(f"未找到「智能生活」图标，第{smart_life_retry}次重试(关闭所有应用后重看)")
            start_test(d, logger)
            interruptible_sleep(15)
        logger.info("点击智能生活")
        d(text="智能生活").click()
        while d(text=power_name).exists(timeout=5) is False:
            d.swipe(screen_width / 2, screen_height * 0.8, screen_width / 2, screen_height * 0.2)
            time.sleep(2)
            recheck += 1
            if recheck > 5:
                break
        logger.info(f"检查{power_name}")
        if d(text=power_name).exists(timeout=2):
            logger.info(f"点击{power_name}")
            d(text=power_name).click()
            interruptible_sleep(20)
        else:
            logger.info(f"未找到{power_name}，重新打开应用重试")
            start_test(d, logger)
            time.sleep(5)


def common_to_power(power_ip, power_sn, power_name, logger):
    # 获取ADB设备列表
    recheck = 0
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接，devices信息为{devices}")
    d = safe_u2_connect(power_ip)
    run_command(f"adb -s {power_ip} shell am start com.oray.sunlogin/com.oray.sunlogin.application.Main")
    while not d(resourceId=f"com.oray.sunlogin:id/iv_power_strip_s{power_sn}").exists(timeout=5):
        if d(text="向日葵远程控制").exists(timeout=1):
            d(text="向日葵远程控制").click()
        if d(text="开机设备").exists(timeout=1):
            d(text="开机设备").click()
        if d(text=power_name).exists(timeout=1):
            d(text=power_name).click()
        if d(text="显示列表").exists(timeout=1):
            d(text="显示列表").click()
        if d(text="确定").exists(timeout=1):
            d(text="确定").click()
        if d(resourceId="com.oray.sunlogin:id/tv_offline_power_strip_tip").exists(timeout=1):
            d(resourceId="com.oray.sunlogin:id/fl_back").click()
            time.sleep(2)
            d(text=power_name).click()
        time.sleep(10)
        recheck += 1
        if recheck > 10:
            raise RuntimeError("命令执行失败: 尝试打开模拟器进入到电源按钮界面失败")


# 保证模拟器正常打开
def check_power_connect(power_ip, power_process_name, power_path, logger):
    devices = get_adb_devices()
    logger.info(f"首次检查设备状态{devices}")
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    while power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        run_command(f"adb disconnect")
        reopen_power(power_process_name, power_path, logger, power_ip)
        devices = get_adb_devices()
        logger.info(f"重新检查设备状态{devices}")
        device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}


# 保证模拟器正常进入到拇指机器人的点击页面
def check_home_open(power_ip, power_process_name, power_name, power_path, logger):
    reopen_count = 0
    while True:
        if not is_running:
            return
        check_power_connect(power_ip, power_process_name, power_path, logger)
        try:
            common_to_home_on(power_ip, power_name, logger)
            break
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.info(f"错误日志信息{error_msg}")
            reopen_count += 1
            # 连续多次重启模拟器仍无法进入机器人页面：判定模拟器严重异常，飞书告警(仅提醒一次)后继续尝试
            if reopen_count == 3:
                logger.info("已连续3次重启模拟器仍无法进入机器人页面，模拟器可能严重异常，发送告警")
                try:
                    send_message("模拟器多次重启仍无法进入拇指机器人页面，疑似模拟器/launcher严重异常，请人工检查", logger)
                except Exception:
                    pass
            reopen_power(power_process_name, power_path, logger, power_ip)
            continue


# 保证模拟器正常进入到智能排插的点击页面
def check_power_open(power_ip, power_process_name, power_name, power_path, logger, power_sn):
    while True:
        if not is_running:
            return
        check_power_connect(power_ip, power_process_name, power_path, logger)
        try:
            common_to_power(power_ip, power_sn, power_name, logger)
            break
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.info(f"错误日志信息{error_msg}")
            reopen_power(power_process_name, power_path, logger, power_ip)
            continue


def check_devices_offline(device_ip):
    devices = get_adb_devices()
    logger.info(devices)
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if f"{device_ip}:5555" in device_status.keys() and device_status[f"{device_ip}:5555"].strip() == 'device':
        return True
    else:
        return False


def check_devices_status(device_ip, power_ip, power_process_name, power_name, power_name_botton, power_path, logger,
                         test_type):
    run_command(f"adb connect {device_ip}")
    time.sleep(5)  # 等待 ADB 状态刷新
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    logger.info(f"首次检查设备连接状态信息：{devices}")
    retry_times = 0
    while True:
        if not is_running:
            return
        if f"{device_ip}:5555" in device_status.keys() and device_status[f"{device_ip}:5555"].strip() == 'device':
            logger.info("连接正常，退出状态检测")
            return
        else:
            for i in range(2):
                if not is_running:
                    return
                for j in range(5):
                    home_on(power_ip, power_process_name, power_name, power_path, logger)
                time.sleep(5)
                run_command(f"adb connect {device_ip}")
                interruptible_sleep(15)
                devices = get_adb_devices()
                device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
                logger.info(f"第{i + 1}次连续按键解锁后检查设备连接状态信息：{devices}")
                if f"{device_ip}:5555" in device_status.keys() and device_status[
                    f"{device_ip}:5555"].strip() == 'device':
                    logger.info("连接正常，退出状态检测")
                    return
            if f"{device_ip}:5555" in device_status.keys() and device_status[f"{device_ip}:5555"].strip() == 'device':
                logger.info("连接正常，退出状态检测")
                return
            else:
                run_command(f"adb disconnect {device_ip}")
                run_command(f'adb connect {device_ip}')
                time.sleep(5)
            devices = get_adb_devices()
            device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
            logger.info(f"adb断开重连后检查连接状态信息：{devices}")
            if f"{device_ip}:5555" in device_status.keys() and device_status[f"{device_ip}:5555"].strip() == 'device':
                logger.info("连接正常，退出状态检测")
                return
            else:
                run_command("adb kill-server")
                run_command(f'adb connect {device_ip}')
                time.sleep(5)  # 等待 ADB 状态刷新
            devices = get_adb_devices()
            device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
            logger.info(f"杀掉adb服务再启动adb后检查连接状态信息：{devices}")
            retry_times += 1
            if retry_times >= 10:
                if test_type in ['launcher关机+home键开机+按键盘进入桌面', '电源键强制关机+电源键开机+键盘进入桌面']:
                    logger.info("上一次按键没有响应，重按一次")
                    home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
                    retry_times = 0


# 检查大屏的扬声器
def check_speaker(rms_single_speaker, record_time, logger, ip, d):
    logger.info("开始检查扬声器")
    logger.info("大屏开始播放音频")
    play_audio_android(ip, d)
    logger.info("本地设备开始录音")
    local_record(record_time, test_wav_speaker_path)
    interruptible_sleep(20)
    rms_data_speaker = analysis_audio(test_wav_speaker_path, logger)
    if rms_data_speaker < rms_single_speaker:
        logger.info("扬声器无声")
        return False
    if rms_data_speaker > rms_single_speaker:
        logger.info("扬声器正常")
        return True


def adb_check_files(ip):
    # 执行 ADB 命令
    cmd = f'adb -s {ip} shell "if [ -d /sdcard/Movies ]; then ls /sdcard/Movies; fi"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

    # 解析结果
    output = result.stdout.strip()
    output_files = output.splitlines()
    return output_files


# 检查大屏的麦克风
def check_mic(d, rms_single_mic, ip, logger):
    run_command(f"adb -s {ip} shell am force-stop com.h3c.filemanager")
    run_command(f"adb -s {ip} shell am force-stop com.h3c.screencap")
    run_command(f"adb -s {ip} shell am force-stop org.videolan.vlc")
    back_to_home(ip, logger)
    logger.info("开始检查麦克风")
    logger.info("大屏开始录音")
    d.shell(f'rm -rf sdcard/Movies/*')
    time.sleep(5)
    while len(adb_check_files(ip)) != 1:
        d.shell(f'rm -rf sdcard/Movies/*')
        android_record(d)
        logger.info("本地开始播放音频")
        time.sleep(2)
        play_audio_local(test_wav_path)
        logger.info("大屏结束录音")
        android_stop_record(d)
        time.sleep(10)
    copy_to_local(ip, logger)  # 复制录音后文件到本地
    rms_data_mic = analysis_audio(test_wav_mic_path, logger)
    if rms_data_mic < rms_single_mic:
        logger.info("麦克风无声")
        return False
    if rms_data_mic > rms_single_mic:
        logger.info("麦克风正常")
        delete_file(f"{globals_file_path}/{adb_check_files(ip)[0]}", logger)
        return True


# 检查相机是否连接正常
def check_camera(d, logger, device_ip, similarity):
    for i in range(10):
        similarity_image_path_name = datetime.now().strftime("%Y%m%d%H%M%S")
        similarity_image_path_name = os.path.join(image_path, similarity_image_path_name)
        os.makedirs(similarity_image_path_name)
        time.sleep(5)
        video_test_image1 = os.path.join(os.path.join(similarity_image_path_name, f"camera_1_{i}.jpg"))
        video_test_image2 = os.path.join(os.path.join(similarity_image_path_name, f"camera_2_{i}.jpg"))
        back_to_home(device_ip, logger)
        d.app_stop("com.h3c.camera2")
        interruptible_sleep(15)
        run_command(f"adb -s {device_ip} shell am start com.h3c.camera2/com.android.camera.CameraLauncher")
        time.sleep(10)
        d(text="照片").click()
        time.sleep(10)
        take_screenshot(d, video_test_image1, logger)
        d(resourceId="com.h3c.camera2:id/h3c_camera_toggle_button").click()
        time.sleep(10)
        take_screenshot(d, video_test_image2, logger)
        time.sleep(5)
        if match_image(video_test_template1, video_test_image1, logger, threshold=similarity) or match_image(
                video_test_template2, video_test_image1, logger, threshold=similarity):
            if match_image(video_test_template1, video_test_image2, logger, threshold=similarity) or match_image(
                    video_test_template2, video_test_image2, logger, threshold=similarity):
                shutil.rmtree(similarity_image_path_name)  # 清除整个目录
                logger.info("删除截图文件夹成功")
                return True
            else:
                continue
        else:
            continue
    return False

def check_desktop_widget(d, logger, device_ip, similarity,launcher_num):
    success_tag = True
    similarity_image_path_name = datetime.now().strftime("%Y%m%d%H%M%S")
    similarity_image_path_name = os.path.join(image_path, similarity_image_path_name)
    os.makedirs(similarity_image_path_name)
    back_to_home(device_ip, logger)
    time.sleep(5)
    if launcher_num <= 1:
        desktop_widget_test_image = os.path.join(os.path.join(similarity_image_path_name, f"desktop_widget_1.jpg"))
        take_screenshot(d, desktop_widget_test_image, logger)
        if match_image(os.path.join(image_path, "desktop_widget_template1.jpg"), desktop_widget_test_image, logger, threshold=similarity):
            shutil.rmtree(similarity_image_path_name)  # 清除整个目录
            logger.info("删除截图文件夹成功")
            return True
        else:
            return False
    else:
        for i in range(launcher_num):
            desktop_widget_test_image = os.path.join(os.path.join(similarity_image_path_name, f"desktop_widget_{i+1}.jpg"))
            take_screenshot(d, desktop_widget_test_image, logger)
            if match_image(os.path.join(image_path, f"desktop_widget_template{i+1}.jpg"), desktop_widget_test_image, logger, threshold=similarity):
                logger.info(f"第{i+1}张图片验证通过")
            else:
                success_tag = False
            d.swipe_ext("left", scale=0.6)
            time.sleep(10)
        if success_tag == True:
            shutil.rmtree(similarity_image_path_name)  # 清除整个目录
            logger.info("删除截图文件夹成功")
        return success_tag

def power_check_android(ip):
    # 执行 adb 命令来获取电池状态
    result = subprocess.run(['adb', "-s", f"{ip}", 'shell', 'dumpsys', 'battery'],
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='ignore')
    # 检查命令是否成功执行
    if result.returncode != 0:
        print("无法执行 adb 命令。请确保设备已连接并启用了 USB 调试。")
        return False

    output = result.stdout

    # 查找充电状态
    for line in output.splitlines():
        if 'status' in line:
            status_value = line.split(':')[1].strip()
            # Android 的电池状态，2 表示正在充电，5 表示已充满
            if status_value in ['2', '5']:
                return True
            else:
                return False


def power_check_win(logger):
    while True:
        conn.sendall(b'120')  # 3表示开始检测win下扬声器
        logger.info('已发送码120，进入检测win下充电')
        response = conn.recv(1024)
        if response.decode() == '121':
            logger.info("win-检测未在充电")
            return False
        if response.decode() == '122':
            logger.info("win-检测正在充电")
            return True


# 检查U盘是否正常识别
def check_udisk(logger, d, u_disk_name, ip):
    back_to_home(ip, logger)
    try:
        u_disk_name_list = u_disk_name.split(",")
    except:
        u_disk_name_list = u_disk_name
    d.app_start("com.h3c.filemanager", "com.h3c.filemanager.ui.ActivityMain")
    interruptible_sleep(20)
    for u_disk in u_disk_name_list:
        status = d(text=u_disk).exists(timeout=5)
        if not status:
            logger.info(f"名称为{u_disk}的U盘未检测到")
            send_message(f"名称为{u_disk}的U盘未检测到", logger)
            return False
    return True


def delete_file(file_path, logger):
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info("缓存文件都已删除")
    else:
        logger.info("文件不存在")


def push_report(web_hook, message_body, logger):
    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    ChatRob = requests.post(url=web_hook, json=message_body, headers=header)
    opener = ChatRob.json()
    logger.info("opener:{}".format(opener))
    if opener["StatusMessage"] == "success":
        logger.info(u"%s 通知消息发送成功！" % opener)
    else:
        logger.info(u"通知消息发送失败，原因：{}".format(opener))


def send_message(message, logger):
    webhook = 'YOUR_FEISHU_WEBHOOK_URL'
    message_body = {
        "msg_type": "text",
        "content": {
            "text": f"测试项目-机器-人员：{test_message}\n报错信息：{message}"
        }
    }
    push_report(webhook, message_body, logger)


# 获取摄像头列表
def get_camera_list():
    camera_list = []
    graph = FilterGraph()
    camera_name_lists = graph.get_input_devices()
    for camera_name in camera_name_lists:
        camera_list.append(camera_name)
    return camera_list


# 通过摄像头名称获取摄像头序号
def get_camera_index(camera_name):
    pythoncom.CoInitialize()  # 初始化 COM 库
    try:
        graph = FilterGraph()
        devices = graph.get_input_devices()
        index = devices.index(camera_name) if camera_name in devices else -1
    finally:
        pythoncom.CoUninitialize()  # 反初始化 COM 库
    return index


def catch_logs(ip, logger, type):
    # 切换到root用户
    run_command(f"adb -s {ip} shell setprop persist.h3c.root_state 123@qwe")
    run_command(f"adb -s {ip} root")

    # 创建目标目录
    timestamp = time.strftime("%m%d%H%M%S", time.localtime())
    target_dir = f"{globals_file_path}/logs/{timestamp}_{type}"
    zip_file_path = f"{globals_file_path}/logs/{timestamp}_{type}.zip"
    os.makedirs(target_dir, exist_ok=True)

    # 拉取日志文件的压缩包到本地
    run_command(f"adb -s {ip} pull /data/misc/logd {target_dir}")
    run_command(f"adb -s {ip} pull /data/vendor/logs {target_dir}")

    # 拉取日志文件到目标目录
    run_command(f"adb -s {ip} pull /data/tombstones {target_dir}")
    run_command(f"adb -s {ip} pull /data/anr {target_dir}")

    # 转存dmesg文件
    run_command(f'adb -s {ip} shell "dmesg >/data/dmesg.txt"')
    time.sleep(10)
    run_command(f"adb -s {ip} pull /data/dmesg.txt {target_dir}")

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, target_dir))

    try:
        if os.path.exists(target_dir):
            for filename in os.listdir(target_dir):
                file_path = os.path.join(target_dir, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            shutil.rmtree(target_dir)
            logger.info("日志文件夹已清空")
        else:
            logger.info("日志文件夹不存在")
    except Exception as e:
        error_msg = traceback.format_exc()
        logger.info(f"清空日志文件夹时发生异常{error_msg}")

    logger.info(f"所有日志文件都已下载至 {target_dir}.")


def check_balck(logger, path, camera_index, similarity):
    similarity_tag = False
    # 打开摄像头（默认设备ID为0）
    cap = cv2.VideoCapture(camera_index)
    for i in range(20):
        similarity_image_path = os.path.join(path, f"captured_frame_{i}.jpg")
        # 如果帧读取错误，退出循环
        if not cap.isOpened():
            logger.info("无法打开摄像头")
            exit()
        ret, frame = cap.read()
        if not ret:
            logger.info("无法接收帧 (stream end?)")
        cv2.imwrite(similarity_image_path, frame)
        logger.info(f"图像已保存为:captured_frame_{i}.jpg")
        time.sleep(5)
        if match_image(template_similarity_image_path, similarity_image_path, logger, threshold=similarity):
            logger.info(f"captured_frame_{i}.jpg 相似度通过")
            return True
        else:
            logger.info(f"captured_frame_{i}.jpg 相似度不通过")
        time.sleep(5)
        check_pause_and_stop()  # 检查是否有停止或暂停信号
    # 释放摄像头和关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()
    return similarity_tag


def match_image(template_path, screenshot_path, logger, threshold=0.8):
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

    # 获取最小匹配值、最大匹配值、匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    logger.info(max_val)
    return max_val >= threshold


def take_screenshot(device, filename, logger):
    logger.info("正在截取屏幕...")
    device.screenshot(filename)
    time.sleep(3)
    if os.path.exists(filename):
        logger.info(f"截图保存在 {filename}")
    else:
        logger.error(f"截图保存失败，{filename}")


def run_monkey(logger, ip):
    run_command(f"adb -s {ip} shell setprop persist.h3c.root_state 123@qwe")
    run_command(f"adb -s {ip} root")
    logger.info("开始运行monkey指令-launcher")
    run_command(
        f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 70 --pct-motion 30 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.launcher --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-录屏")
    run_command(
        f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 100 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.screencap --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-文件管理器")
    run_command(
        f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 100 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.filemanager --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-截屏")
    run_command(
        f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 70 --pct-motion 30 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.screenshot --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-批注")
    run_command(
        f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 30 --pct-motion 70 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.commentary --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("关闭应用-文件管理器")
    run_command(f"adb -s {ip} shell am force-stop com.h3c.filemanager")
    logger.info("关闭应用-录屏")
    run_command(f"adb -s {ip} shell am force-stop com.h3c.screencap")
    logger.info("关闭应用-截屏")
    run_command(f"adb -s {ip} shell am force-stop com.h3c.screenshot")
    logger.info("关闭应用-批注")
    run_command(f"adb -s {ip} shell am force-stop com.h3c.commentary")


def root_devices(ip):
    # 切换到root用户
    run_command(f"adb -s {ip} shell setprop persist.h3c.root_state 123@qwe")
    run_command(f"adb -s {ip} root")


# 获取已连接的wifi名称
def get_connected_wifi_name():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'],
                                capture_output=True,
                                text=True,
                                encoding='utf-8',
                                errors='ignore')

        # 检查命令执行是否成功
        if result.returncode != 0:
            return None

        stdout = result.stdout or ""  # 处理可能的None值
        for line in stdout.splitlines():
            if "SSID" in line and "BSSID" not in line:  # 更精确的匹配
                parts = line.split(":")
                if len(parts) >= 2:
                    return parts[1].strip()
        return None
    except Exception as e:
        error_msg = traceback.format_exc()
        logger.info(f"获取WiFi名称出错{error_msg}")
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


def android_to_win(d, logger, ip, click_x=1968, click_y=286):
    back_to_home(ip, logger)
    d.open_notification()  # 直接打开通知栏
    time.sleep(5)
    d.click(int(click_x), int(click_y))
    time.sleep(3)
    d(text="确认").click()


def win_check_driver(logger):
    while True:
        conn.sendall(b'14')  # 3表示开始检测win下扬声器
        logger.info('已发送码14，进入检测win下驱动')
        response = conn.recv(1024)
        if response.decode() == '140':
            logger.info("win-驱动异常")
            return False
        if response.decode() == '141':
            logger.info("win-驱动正常")
            return True


def win_check_screen_off(logger):
    while True:
        conn.sendall(b'15')  # 3表示开始检测win下扬声器
        logger.info('已发送码15，进入检测win画面')
        response = conn.recv(1024)
        if response.decode() == '151':
            logger.info("win-息屏状态异常")
            return False
        if response.decode() == '150':
            logger.info("win-息屏状态正常")
            return True


def win_check_screen_on(logger):
    while True:
        conn.sendall(b'16')  # 3表示开始检测win下扬声器
        logger.info('已发送码16，进入检测win画面')
        response = conn.recv(1024)
        if response.decode() == '161':
            logger.info("win-唤醒状态异常")
            return False
        if response.decode() == '160':
            logger.info("win-唤醒状态正常")
            return True


def win_check_speaker(logger, record_time, win_speaker_record_path, rms_speaker_win):
    check_speaker_tag = 0
    retry = 0
    while True:
        conn.sendall(b'3')  # 3表示开始检测win下扬声器
        logger.info('已发送码3，进入检测win下扬声器')
        response = conn.recv(1024)
        while check_speaker_tag == 0:
            if response.decode() == '32':
                logger.info('已收到码32，大屏开始播放声音，本地开始录音')
                local_record(record_time, win_speaker_record_path)
                logger.info("分析录音数据")
                rms = analysis_audio(win_speaker_record_path, logger)
                if rms < rms_speaker_win:
                    logger.info("win-检测扬声器无声")
                    check_speaker_tag = 2
                if rms > rms_speaker_win:
                    logger.info("win-检测扬声器正常")
                    check_speaker_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break
        if check_speaker_tag == 1:
            return True
        if check_speaker_tag == 2:
            return False


def check_win_microphone(logger):
    check_microphone_tag = 0
    retry = 0
    while True:
        conn.sendall(b'4')  # 3表示开始检测win下扬声器
        logger.info('已发送码4，进入检测win下麦克风')
        while check_microphone_tag == 0:
            response = conn.recv(1024)
            if response.decode() == '42':
                logger.info('已收到码42，大屏开始录音，本地开始播放音频')
                play_audio_local(test_wav_path)
            if response.decode() == '40':
                logger.info("win-检测麦克风无声")
                check_microphone_tag = 2
            if response.decode() == '41':
                logger.info("win-检测麦克风正常")
                check_microphone_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break

        if check_microphone_tag == 1:
            return True
        if check_microphone_tag == 2:
            return False


def check_win_u_disk(logger):
    check_u_disk_tag = 0
    retry = 0
    while True:
        conn.sendall(b'7')  # 3表示开始检测win下U盘
        logger.info('已发送码7，进入检测win下U盘')
        while check_u_disk_tag == 0:
            response = conn.recv(1024)
            if response.decode() == '71':
                logger.info("win-检测U盘不通过")
                check_u_disk_tag = 2
            if response.decode() == '70':
                logger.info("win-检测U盘通过")
                check_u_disk_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break

        if check_u_disk_tag == 1:
            return True
        if check_u_disk_tag == 2:
            return False


def check_win_camera(logger):
    check_camera_tag = 0
    retry = 0
    while True:
        conn.sendall(b'8')  # 3表示开始检测win下相机
        logger.info('已发送码8，进入检测win下相机')
        while check_camera_tag == 0:
            response = conn.recv(1024)
            if response.decode() == '81':
                logger.info("win-检测相机不通过")
                check_camera_tag = 2
            if response.decode() == '80':
                logger.info("win-检测相机通过")
                check_camera_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break

        if check_camera_tag == 1:
            return True
        if check_camera_tag == 2:
            return False


def check_win_light_sensor(logger):
    check_tag = 0
    retry = 0
    while True:
        conn.sendall(b'200')
        logger.info('已发送码200，进入检测win下光感')
        while check_tag == 0:
            response = conn.recv(1024)
            if response.decode() == '201':
                logger.info("win-光感检测不通过（传感器不存在或无法读取）")
                check_tag = 2
            if response.decode() == '202':
                logger.info("win-光感检测通过")
                check_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break
        if check_tag == 1:
            return True
        if check_tag == 2:
            return False


def check_win_bluetooth(logger):
    """Win侧蓝牙检测：发码200对应光感，蓝牙用码210。
    客户端先查蓝牙开关，再查指定蓝牙设备是否已连接，整体通过回212，否则回211。"""
    check_tag = 0
    retry = 0
    while True:
        conn.sendall(b'210')
        logger.info('已发送码210，进入检测win下蓝牙')
        while check_tag == 0:
            response = conn.recv(1024)
            if response.decode() == '211':
                logger.info("win-蓝牙检测不通过（开关未开或目标设备未连接）")
                check_tag = 2
            if response.decode() == '212':
                logger.info("win-蓝牙检测通过")
                check_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break
        if check_tag == 1:
            return True
        if check_tag == 2:
            return False


def check_android_bt_switch(ip, logger):
    """安卓侧检测一：蓝牙开关是否已打开。
    优先用 settings get global bluetooth_on（1=开），回退解析 dumpsys 状态。"""
    try:
        out = run_command(f"adb -s {ip} shell settings get global bluetooth_on").strip()
        last = out.splitlines()[-1].strip() if out else ''
        logger.info(f"[安卓蓝牙] bluetooth_on 读数：{out!r}")
        if last == '1':
            logger.info("[安卓蓝牙] 蓝牙开关：已打开")
            return True
        # 回退：dumpsys 状态
        dump = run_command(f"adb -s {ip} shell dumpsys bluetooth_manager")
        if 'state: ON' in dump or 'enabled: true' in dump:
            logger.info("[安卓蓝牙] 蓝牙开关：已打开(dumpsys)")
            return True
        logger.info("[安卓蓝牙] 蓝牙开关：未打开")
        return False
    except Exception:
        logger.info(f"[安卓蓝牙] 开关检测异常{traceback.format_exc()}")
        return False


def _parse_android_connected_bt(dump):
    """从 dumpsys bluetooth_manager 提取"当前已连接"的蓝牙设备名列表。
    要点：
      1) 部分设备会对 MAC 打码(如 XX:XX:XX:XX:89:CC)，故 MAC 正则放宽允许 X/x 占位，
         同一打码 MAC 在 Bonded 段与状态机块头里是同一字符串，仍可关联；
      2) "已连接"以各 Profile 状态机为准：块头形如 "XxxStateMachine for <MAC>"，
         块内出现 mConnectionState: STATE_CONNECTED / mCurrentState: Connected / state=Connected
         即认为该 MAC 当前已连接（仅靠 Bonded 段只能说明已配对，不代表已连接）；
      3) 用 Bonded 段的 MAC->Name 映射把已连接 MAC 还原成设备名。"""
    import re
    mac_token = r'([0-9A-Fa-fXx]{2}(?::[0-9A-Fa-fXx]{2}){5})'
    mac_re = re.compile(mac_token)
    header_re = re.compile(r'StateMachine for\s+' + mac_token)

    # ① Bonded devices 段：MAC -> Name（行形如 "MAC [BR/EDR][ 0x240404 ] EDIFIER W820NB"）
    mac_to_name = {}
    in_bonded = False
    for line in dump.splitlines():
        if 'Bonded devices:' in line:
            in_bonded = True
            continue
        if in_bonded:
            if not line.strip():
                in_bonded = False
                continue
            m = mac_re.search(line)
            if m:
                mac = m.group(1).upper()
                rest = re.sub(r'\[[^\]]*\]', '', line[m.end():]).strip()  # 去掉 [BR/EDR][ 0x240404 ]
                if rest:
                    mac_to_name[mac] = rest
            else:
                in_bonded = False

    # ② 各 Profile 状态机块：找出当前已连接的 MAC
    connected_macs = set()
    cur = None
    for line in dump.splitlines():
        h = header_re.search(line)
        if h:
            cur = h.group(1).upper()
        if cur and ('mConnectionState: STATE_CONNECTED' in line
                    or 'mCurrentState: Connected' in line
                    or re.search(r'\bstate=Connected\b', line)):
            connected_macs.add(cur)

    return [mac_to_name.get(mac, mac) for mac in connected_macs]


def check_android_bt_connected(ip, bt_name, logger):
    """安卓侧检测二：指定蓝牙设备是否已连接。bt_name 为英文逗号分隔的设备名，空则跳过。"""
    names = [n.strip() for n in str(bt_name).split(',') if n.strip()]
    if not names:
        logger.info("[安卓蓝牙] 未配置蓝牙名称，跳过已连接检测")
        return True
    try:
        dump = run_command(f"adb -s {ip} shell dumpsys bluetooth_manager")
    except Exception:
        logger.info(f"[安卓蓝牙] 读取dumpsys异常{traceback.format_exc()}")
        return False
    connected = _parse_android_connected_bt(dump)
    logger.info(f"[安卓蓝牙] 已连接设备：{connected if connected else '无'}")
    missing = [n for n in names if not any(n in c for c in connected)]
    if missing:
        logger.info(f"[安卓蓝牙] 未连接的目标设备：{missing}")
        return False
    logger.info("[安卓蓝牙] 所有目标蓝牙设备均已连接")
    return True


def _send_win_cmd(cmd, ack, desc, logger):
    """发送Win命令码并等待ACK，结构与原各win_*函数保持一致"""
    tag = 0
    retry = 0
    while True:
        conn.sendall(cmd.encode())
        logger.info(f'已发送码{cmd}，{desc}')
        response = conn.recv(1024)
        while tag == 0:
            if response.decode() == ack:
                logger.info(f'已收到码{ack}')
                tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break
        if tag == 1:
            return True


def win_to_android(logger):  return _send_win_cmd('5',   '52',  '进入切换系统', logger)
# 快速切换：通知客户端走 H3C SystemControl 的 IPC 直接切换(免点击控制中心)，客户端 win_to_android_fast 执行
def win_to_android_fast(logger): return _send_win_cmd('6', '62', '进入快速切换系统(IPC)', logger)
def win_restart(logger):     return _send_win_cmd('9',   '92',  '准备重启win系统', logger)
def win_shutdown(logger):    return _send_win_cmd('110', '112', '准备win系统关机', logger)
def win_sleep(logger):       return _send_win_cmd('130', '132', '准备win系统睡眠', logger)
def win_hibernate(logger):   return _send_win_cmd('170', '172', '准备win系统休眠', logger)
def win_unuse(logger):       return _send_win_cmd('180', '182', '设置指定无操作睡眠息屏时间', logger)


def swipe_screen_ratio(d, ratio=0.3, duration=0.5):
    width, height = d.window_size()

    # 计算起点和终点坐标
    start_x = width // 2  # 水平中心
    start_y = height * 0.9  # 起点：屏幕底部90%位置
    end_x = start_x  # 水平不变
    end_y = start_y - (height * ratio)  # 终点：向上滑动指定比例

    # 执行滑动
    d.swipe(start_x, start_y, end_x, end_y, duration)


def home_on(power_ip, power_process_name, power_name, power_path, logger):
    check_home_open(power_ip, power_process_name, power_name, power_path, logger)
    d = safe_u2_connect(power_ip)
    logger.info("拇指机器人按键一次")
    if d(text="空闲").exists(timeout=5):
        d(text="空闲").click()


# ------------------------------------------------------------------------------------------------------------------------------------
def power_on(power_ip, power_process_name, power_name, power_path, logger, power_sn):
    check_power_open(power_ip, power_process_name, power_name, power_path, logger, power_sn)
    d = safe_u2_connect(power_ip)
    while not d(resourceId=f"com.oray.sunlogin:id/cd_view_s{power_sn}").exists(timeout=3):
        logger.info("检测到当前电源为关闭状态，开启电源\n\n\n")
        time.sleep(3)
        try:
            d(resourceId=f"com.oray.sunlogin:id/iv_power_strip_s{power_sn}").click()
            if d(text="确认").exists(timeout=2):
                d(text="确认").click()
            d(resourceId="com.oray.sunlogin:id/fl_back").click()
            d(text=power_name).click()
            time.sleep(5)
        except:
            error_msg = traceback.format_exc()
            logger.info(f"异常信息{error_msg}")
            d(resourceId="com.oray.sunlogin:id/fl_back").click()
            time.sleep(2)
            d(text=power_name).click()


def power_off(power_ip, power_process_name, power_name, power_path, logger, power_sn):
    check_power_open(power_ip, power_process_name, power_name, power_path, logger, power_sn)
    d = safe_u2_connect(power_ip)
    while d(resourceId=f"com.oray.sunlogin:id/cd_view_s{power_sn}").exists(timeout=3) or d(
            resourceId="com.oray.sunlogin:id/tv_offline_power_strip_tip").exists(timeout=3):
        logger.info("检测到当前电源为开启状态，关闭电源\n\n\n")
        time.sleep(3)
        try:
            d(resourceId=f"com.oray.sunlogin:id/iv_power_strip_s{power_sn}").click()
            if d(text="确认").exists(timeout=2):
                d(text="确认").click()
            d(resourceId="com.oray.sunlogin:id/fl_back").click()
            d(text=power_name).click()
            time.sleep(5)
        except:
            error_msg = traceback.format_exc()
            logger.info(f"异常信息{error_msg}")
            d(resourceId="com.oray.sunlogin:id/fl_back").click()
            time.sleep(2)
            d(text=power_name).click()


def interruptible_sleep(seconds):
    """分段睡眠，每 0.5 秒检查 is_running / is_paused，响应更及时。
    停止时提前返回（由调用处的 while is_running 或 check_pause_and_stop 负责清理）；
    暂停时不计入等待时间，恢复后继续倒计时。"""
    elapsed = 0.0
    while elapsed < seconds:
        if not is_running:
            return
        if is_paused:
            time.sleep(0.5)
            continue
        time.sleep(0.5)
        elapsed += 0.5


def on_start(test_project_type, test_type, stop_type_select, test_select, test_Config, selected_camera, switch_mode, root, logger):
    global check_pause_and_stop
    global android_or_win  # 声明为全局变量
    global conn

    def check_pause_and_stop():
        while is_paused:
            time.sleep(0.1)
            root.after(0, update_button_text)  # 传函数引用，不加()
        if not is_running:
            update_button_states(logger)
            logger.info("已成功停止运行。")
            sys.exit()

    def control_devices(power_ip, logger, device_ip, on_off_interval, power_process_name, power_path, power_name,
                        power_name_botton, time_set):
        global android_or_win
        global conn

        if test_type == "无操作":
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == "launcher重启":
            reboot_android(logger, d, device_ip)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == "安卓下无操作睡眠+键盘唤醒":
            run_command(f"adb -s {device_ip} shell settings put system screen_off_timeout {time_set * 1000}")
            logger.info(f"已设置睡眠时间为{time_set}秒")
            interruptible_sleep(on_off_interval)
            if check_devices_offline(device_ip) is True:
                logger.info("设备的状态仍为连接状态，未息屏成功，程序停止")
                update_button_states(logger)  # 调用更新按钮状态的函数
                sys.exit()
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == "双系统切换":
            if android_or_win == "android":
                android_to_win(d, logger, device_ip, android_click_x, android_click_y)
                android_or_win = "win"
                if switch_mode == "休眠切换":
                    logger.info("休眠切换模式：等待Win从休眠恢复后按键解锁")
                    interruptible_sleep(30)
                    for i in range(5):
                        home_on(power_ip, power_process_name, power_name, power_path, logger)
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                return True
            if android_or_win == "win":
                # 快速切换：走 IPC(客户端 win_to_android_fast)，免点击控制中心；其余模式仍点击控制中心
                if switch_mode == "快速切换":
                    win_to_android_fast(logger)
                else:
                    win_to_android(logger)
                android_or_win = "android"
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                return True

        if test_type == "launcher关机+home键开机+按键盘进入桌面":
            shutdown_android(logger, d, device_ip)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == '电源键睡眠+电源键唤醒+键盘进入桌面':
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(on_off_interval)
            if check_devices_offline(device_ip) is True:
                logger.info("设备的状态仍为连接状态，未息屏成功，程序停止")
                update_button_states(logger)  # 调用更新按钮状态的函数
                sys.exit()
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == '电源键强制关机+电源键开机+键盘进入桌面':
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == '电源键睡眠+键盘唤醒':
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(on_off_interval)
            if check_devices_offline(device_ip) is True:
                logger.info("设备的状态仍为连接状态，未息屏成功，程序停止")
                update_button_states(logger)  # 调用更新按钮状态的函数
                sys.exit()
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        # win下的操作，上面是安卓下的操作
        if test_type == "win菜单重启":
            win_restart(logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == "win下无操作息屏+键盘唤醒":
            # win_unuse(logger)
            interruptible_sleep(on_off_interval)
            if win_check_screen_off(logger) is False:
                update_button_states(logger)  # 调用更新按钮状态的函数
                sys.exit()
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
            interruptible_sleep(10)
            if win_check_screen_on(logger) is False:
                update_button_states(logger)  # 调用更新按钮状态的函数
                sys.exit()
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == "win下无操作息屏+电源键唤醒+键盘进入桌面":
            win_unuse(logger)
            interruptible_sleep(on_off_interval)
            if win_check_screen_off(logger) is False:
                update_button_states(logger)  # 调用更新按钮状态的函数
                sys.exit()
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(10)
            if win_check_screen_on(logger) is False:
                update_button_states(logger)  # 调用更新按钮状态的函数
                sys.exit()
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win下无操作睡眠+键盘唤醒':
            # win_unuse(logger)
            interruptible_sleep(on_off_interval)
            for i in range(10):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win下无操作睡眠+电源键唤醒+键盘进入桌面':
            win_unuse(logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win下电源键关机+电源键开机':
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win下电源键强制关机+电源键开机':
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win菜单关机+电源键开机':
            win_shutdown(logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win下电源键睡眠+电源键唤醒+按键盘进入桌面' or test_type == 'win下电源键休眠+电源键唤醒+按键盘进入桌面':
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            time.sleep(5)
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win下电源键睡眠+按键盘进入桌面':
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            interruptible_sleep(on_off_interval)
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
                time.sleep(2)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win菜单休眠+电源键唤醒+按键盘进入系统':
            win_hibernate(logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            time.sleep(5)
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
                time.sleep(2)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win菜单睡眠+电源键唤醒+按键盘进入系统':
            win_sleep(logger)
            interruptible_sleep(on_off_interval)
            home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
            time.sleep(5)
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
                time.sleep(2)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

        if test_type == 'win菜单睡眠+按键盘进入系统':
            win_sleep(logger)
            interruptible_sleep(on_off_interval)
            for i in range(5):
                home_on(power_ip, power_process_name, power_name, power_path, logger)
                time.sleep(2)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

    try:
        rms_single_speaker = int(test_Config['rms_speaker'])  # 本地rms阈值---
    except:
        pass
    try:
        rms_single_mic = int(test_Config['rms_mic'])  # 大屏rms阈值----
    except:
        pass
    try:
        record_time = int(test_Config['record_time'])  # 录音时长---
    except:
        pass
    try:
        power_ip = test_Config['power_ip']  # adb连接的插线板IP地址---
    except:
        pass

    try:
        connect_wifi_name = test_Config['connect_wifi_name']  # adb连接的插线板IP地址---
    except:
        pass
    try:
        similarity = float(test_Config['similarity'])  # adb连接的插线板IP地址---
    except:
        pass

    try:
        launcher_num = int(test_Config['launcher_num'])  # adb连接的插线板IP地址---
    except:
        pass


    try:
        wifi_password = test_Config['wifi_password']  # adb连接的插线板IP地址---
    except:
        pass

    try:
        u_disk_name = test_Config['u_disk_name']  # U盘名称---
    except:
        pass
    try:
        bt_name = test_Config['bt_name']  # 蓝牙名称（英文逗号分隔）---
    except:
        bt_name = ''
    try:
        power_path = test_Config['power_path']  # 模拟器打开路径---
    except:
        pass
    try:
        power_process_name = test_Config['power_process_name']  # 模拟器进程名称---
    except:
        pass
    try:
        on_off_interval = int(test_Config['on_off_interval'])  # 重启间隔---
    except:
        pass
    try:
        power_name = test_Config['power_name']  # 智能插座名称---
    except:
        power_name = 0
    try:
        power_name_botton = test_Config['power_name_botton']
    except:
        power_name_botton = 0
    try:
        power_name_power = test_Config['power_name_power']
    except:
        pass
    try:
        power_sn = test_Config['power_sn']
    except:
        pass
    try:
        device_ip = test_Config['device_ip']  # adb连接的大屏IP地址---
    except:
        pass
    try:
        camera_select = int(test_Config['camera_select'])  # 获取选择的摄像头序号---
    except:
        pass

    try:
        test_interval = int(test_Config['test_interval'])  # 重启间隔---
    except:
        pass

    try:
        time_set_sleep = int(test_Config['time_set_sleep'])  # 安卓下无操作睡眠时间
    except:
        time_set_sleep = 1800

    try:
        android_click_x = int(test_Config['android_click_x'])  # 安卓切换Win点击坐标X
    except:
        android_click_x = 1968

    try:
        android_click_y = int(test_Config['android_click_y'])  # 安卓切换Win点击坐标Y
    except:
        android_click_y = 286

    global is_running  # 使用 global 关键字
    global tester_project_type
    global tester
    global test_count_var
    global test_fail_count_var
    global is_paused
    global android_or_win
    global run_tag
    global test_message
    global test_type_tag
    test_type_tag = True
    is_running = True  # 确保每次开始时 is_running 为 True
    test_message = test_Config['test_message']  # 测试项目信息
    if test_type == "双系统切换":
        android_or_win = test_Config['android_or_win']
    if test_project_type == "单win（非双系统切换）":
        android_or_win = 'win'
    test_times_data = 0
    test_fail_times_data = 0
    mic_check_tag = 0
    speaker_check_tag = 0
    android_camera_check_tag = 0
    win_camera_check_tag = 0
    if android_or_win == 'android':
        check_devices_status(device_ip, power_ip, power_process_name, power_name, power_name_botton, power_path, logger,
                             test_type)
        logger.info("已连接大屏ip")
        try:
            root_devices(device_ip)
            d = safe_u2_connect(device_ip)
        except:
            error_msg = traceback.format_exc()
            logger.info(f"异常信息{error_msg}")
            check_devices_status(device_ip, power_ip, power_process_name, power_name, power_name_botton, power_path,
                                 logger, test_type)

    # 打开摄像头（默认设备ID为0）
    if '黑屏检测' in test_select:
        back_to_home(device_ip, logger)
        interruptible_sleep(15)
        cap = cv2.VideoCapture(get_camera_index(selected_camera))
        if not cap.isOpened():
            logger.info("无法打开摄像头")
            exit()
        # 读取摄像头的前10帧
        frame = None
        for i in range(10):
            ret, frame = cap.read()
            if not ret:
                logger.info(f"无法接收帧 (第{i + 1}帧)")
                exit()
            if i < 9:
                logger.info(f"丢弃第{i + 1}帧")
        cv2.imwrite(template_similarity_image_path, frame)
        logger.info(f"对比图像已保存")
        cap.release()
        cv2.destroyAllWindows()

    # 安卓下相机检测新方法
    if android_or_win == "android":
        if '相机检测' in test_select:
            d.app_stop("com.h3c.camera2")
            back_to_home(device_ip, logger)
            interruptible_sleep(15)
            while d(text="照片").exists() is False:
                print("打开相机应用")
                run_command(f"adb -s {device_ip} shell am start com.h3c.camera2/com.android.camera.CameraLauncher")
                time.sleep(10)
            d(text="照片").click()
            time.sleep(10)
            take_screenshot(d, video_test_template1, logger)
            d(resourceId="com.h3c.camera2:id/h3c_camera_toggle_button").click()
            time.sleep(10)
            take_screenshot(d, video_test_template2, logger)

    # 安卓下桌面组件检测新方法
    if android_or_win == "android":
        if '桌面组件检测' in test_select:
            back_to_home(device_ip, logger)
            time.sleep(10)
            if launcher_num <= 1:
                take_screenshot(d, os.path.join(image_path, "desktop_widget_template1.jpg"), logger)
            else:
                for i in range(launcher_num):
                    take_screenshot(d, os.path.join(image_path, f"desktop_widget_template{i+1}.jpg"), logger)
                    d.swipe_ext("left", scale=0.6)#此处需要滑动至下一个屏幕，另外添加一个方法来判断当前有多少个页面
                    time.sleep(10)


    while is_running:  # 使用 is_running 控制循环条件
        try:
            run_tag = 0
            if connect_wifi_name == "无":
                logger.info("设置不连接wifi")
            else:
                while get_connected_wifi_name() != connect_wifi_name:
                    if wifi_password == "无":
                        connect_to_wifi(connect_wifi_name)
                    else:
                        connect_to_wifi(connect_wifi_name, wifi_password)
                    logger.info(f'尝试连接wifi:{connect_wifi_name}...')
                    interruptible_sleep(20)
            logger.info(f'成功连接wifi:{connect_wifi_name}')
            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if test_type == "双系统切换":
                if android_or_win == 'win':
                    if switch_mode == "休眠切换":
                        logger.info("点击进入windows系统桌面")
                        for i in range(5):
                            home_on(power_ip, power_process_name, power_name, power_path, logger)
                            time.sleep(1)
                        interruptible_sleep(20)


            if android_or_win == 'android':
                run_command(f"adb connect {device_ip}")
                time.sleep(5)
                check_devices_status(device_ip, power_ip, power_process_name, power_name, power_name_botton, power_path,
                                     logger, test_type)
                logger.info("已连接大屏ip")
                interruptible_sleep(20)
                try:
                    root_devices(device_ip)
                    d = safe_u2_connect(device_ip)
                except:
                    error_msg = traceback.format_exc()
                    logger.info(f"异常信息{error_msg}")
                    check_devices_status(device_ip, power_ip, power_process_name, power_name, power_name_botton,
                                         power_path, logger, test_type)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if test_type == 'win下电源键强制关机+电源键开机':
                if test_times_data % 3 == 2:
                    logger.info(f"当前为强制开关机的恢复次数点，跳过本轮测试")
                    control_devices(power_ip, logger, device_ip, on_off_interval, power_process_name,
                                    power_path, power_name, power_name_botton, time_set_sleep)
                    interruptible_sleep(test_interval)
                    check_pause_and_stop()  # 检查是否有停止或暂停信号
                    test_times_data += 1
                    root.after(0, lambda: test_count_var.set(f"压测次数：{test_times_data}次"))
                    root.after(0, lambda: test_fail_count_var.set(f"失败次数：{test_fail_times_data}次"))
                    continue

            if android_or_win == "win":
                if test_type_tag == True:
                    global conn
                    global response
                    host = '0.0.0.0'
                    port = 12345
                    listern_times = 0
                    while True:
                        try:
                            logger.info(f"当前的listern_times次数为{listern_times}")
                            if listern_times >= 10:
                                if test_type in ['win下电源键关机+电源键开机', 'win菜单关机+电源键开机', 'win下电源键休眠+电源键唤醒+按键盘进入桌面',
                                                 'win菜单休眠+电源键唤醒+按键盘进入系统', 'win下电源键强制关机+电源键开机']:
                                    logger.info("上一次按键没有响应，重按一次")
                                    home_on(power_ip, power_process_name, power_name_botton, power_path, logger)
                                    listern_times = 0
                            if listern_times >= 4 and test_type == "双系统切换":
                                # 双保险：长时间(约4次30秒超时)等不到Win客户端连接，说明"安卓切Win"可能没真正成功(实际仍在安卓)。
                                # 重新执行一次切换到Win并唤醒后继续监听，避免服务端误认为已在Win而无限死等。
                                # 若此时实际已在Win，下面的安卓侧操作会因不可达而抛异常被忽略，不影响继续监听。
                                logger.info("双系统切换：长时间未等到Win客户端连接，疑似切换未成功，重新尝试切换到Win")
                                try:
                                    run_command(f"adb connect {device_ip}")
                                    time.sleep(5)
                                    d = safe_u2_connect(device_ip)
                                    android_to_win(d, logger, device_ip, android_click_x, android_click_y)
                                    if switch_mode == "休眠切换":
                                        interruptible_sleep(30)
                                        for i in range(5):
                                            home_on(power_ip, power_process_name, power_name, power_path, logger)
                                except Exception:
                                    error_msg = traceback.format_exc()
                                    logger.info(f"重新切换到Win时异常(可能实际已在Win)：{error_msg}")
                                listern_times = 0
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                s.bind((host, port))
                                s.listen(1)
                                s.settimeout(30)  # 设置超时时间为30秒
                                logger.info('等待客户端连接...')
                                conn, addr = s.accept()
                                logger.info(f'客户端 {addr} 已连接')
                                # 向客户端发送指令 111
                                conn.sendall(b'1')  # 1表示已接收到客户端的连接
                                logger.info('已发送连接码1,发送确认连接消息给客户端')
                                conn.settimeout(30)
                                response = conn.recv(1024)
                                handshake_retry = 0
                                while response.decode().strip() != "11":
                                    if not response:  # 对端已关闭(常见于上一轮残留的半开连接)，跳出由外层重新监听
                                        raise ConnectionResetError("客户端连接已关闭，重新监听")
                                    logger.info("正在连接中")
                                    time.sleep(2)
                                    handshake_retry += 1
                                    if handshake_retry > 15:
                                        raise socket.timeout
                                    response = conn.recv(1024)  # 关键：循环内重新接收，否则response永不变会死循环刷"正在连接中"
                                logger.info("连接成功")
                                break
                        except socket.timeout:
                            # 捕获到超时异常
                            logger.info("等待连接超时，重新开始监听")
                            listern_times += 1
                        except Exception as e:
                            error_msg = traceback.format_exc()
                            logger.info(f"异常信息{error_msg}")
                            continue

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if android_or_win == "android":
                run_command(f"adb -s {device_ip} shell settings put system screen_off_timeout {1800000}")
                logger.info("已设置永不睡眠")
                if '扬声器检测' in test_select or '麦克风检测' in test_select:
                    delete_file(f"{globals_file_path}/win_speaker_audio.wav", logger)
                    delete_file(f"{globals_file_path}/recorded_speaker_audio.wav", logger)
                    delete_file(f"{globals_file_path}/recorded_mic_audio.wav", logger)
                    delete_file(f"{globals_file_path}/recorded_mic_audio.mp4", logger)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '黑屏检测' in test_select:
                    back_to_home(device_ip, logger)
                    similarity_image_path_name = datetime.now().strftime("%Y%m%d%H%M%S")
                    similarity_image_path_name = os.path.join(os.path.join(globals_file_path, 'image'),
                                                              similarity_image_path_name)
                    os.makedirs(similarity_image_path_name)
                    time.sleep(5)
                    # 检测黑屏
                    if check_balck(logger, similarity_image_path_name, get_camera_index(selected_camera),
                                   similarity) is False:
                        send_message(f"检测图像不符", logger)
                        logger.info("检测图像不符")
                        catch_logs(device_ip, logger, "screen_check_fail")
                        if stop_type_select == "是":
                            update_button_states(logger)  # 调用更新按钮状态的函数
                            sys.exit()
                        else:
                            test_fail_times_data += 1
                            run_tag = 1
                    else:
                        if os.path.exists(similarity_image_path_name):
                            try:
                                shutil.rmtree(similarity_image_path_name)  # 清除整个目录
                                logger.info("删除截图文件夹成功")
                            except Exception as e:
                                logger.error(f"删除截图文件夹失败，错误信息：{e}")

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if android_or_win == "android":
                if '扬声器检测' in test_select or '扬声器+monkey检测' in test_select:
                    time.sleep(5)
                    # 将音频文件复制至大屏
                    copy_to_android(device_ip, logger)
                    time.sleep(5)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if '驱动检测' in test_select:
                if win_check_driver(logger) is True:
                    logger.info("win下驱动检测通过")
                else:
                    send_message(f"驱动异常", logger)
                    if stop_type_select == "是":
                        update_button_states(logger)  # 调用更新按钮状态的函数
                        sys.exit()
                    else:
                        test_fail_times_data += 1
                        run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '扬声器检测' in test_select:
                    if android_or_win == "android":
                        # 扬声器检查
                        if check_speaker(rms_single_speaker, record_time, logger, device_ip, d) is False:
                            speaker_check_tag += 1
                            if speaker_check_tag > 1:
                                send_message(f"扬声器无声", logger)
                                catch_logs(device_ip, logger, "speaker_fail")
                                if stop_type_select == "是":
                                    update_button_states(logger)  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1
                            else:
                                run_command(f"adb -s {device_ip} shell am force-stop com.h3c.filemanager")
                                run_command(f"adb -s {device_ip} shell am force-stop com.h3c.screencap")
                                run_command(f"adb -s {device_ip} shell am force-stop org.videolan.vlc")
                                back_to_home(device_ip, logger)
                                continue
                        else:
                            speaker_check_tag = 0
                    if android_or_win == "win":
                        if win_check_speaker(logger, record_time, win_speaker_path, rms_single_speaker) is True:
                            logger.info("win下扬声器检测通过")
                        else:
                            # send_message(f"win下扬声器检查无声音", logger)
                            logger.info("win下扬声器检测不通过")

                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

                    check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '麦克风检测' in test_select:
                    if android_or_win == "android":
                        # 检查麦克风,不通过则停止运行
                        if check_mic(d, rms_single_mic, device_ip, logger) is False:
                            mic_check_tag += 1
                            if mic_check_tag > 1:
                                send_message(f"麦克风无声", logger)
                                catch_logs(device_ip, logger, "microphone_fail")
                                if stop_type_select == "是":
                                    update_button_states(logger)  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1
                            else:
                                run_command(f"adb -s {device_ip} shell am force-stop com.h3c.filemanager")
                                run_command(f"adb -s {device_ip} shell am force-stop com.h3c.screencap")
                                run_command(f"adb -s {device_ip} shell am force-stop org.videolan.vlc")
                                back_to_home(device_ip, logger)
                                continue
                        else:
                            mic_check_tag = 0
                    if android_or_win == "win":
                        if check_win_microphone(logger) is True:
                            logger.info("win下麦克风检测通过")
                        else:
                            # send_message(f"win下扬声器检查无声音", logger)
                            logger.info("win下麦克风检测不通过")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if android_or_win == "android":
                if '扬声器+monkey检测' in test_select or '麦克风+monkey检测' in test_select:
                    delete_file(f"{globals_file_path}/win_speaker_audio.wav", logger)
                    delete_file(f"{globals_file_path}/recorded_speaker_audio.wav", logger)
                    delete_file(f"{globals_file_path}/recorded_mic_audio.wav", logger)
                    delete_file(f"{globals_file_path}/recorded_mic_audio.mp4", logger)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if '扬声器+monkey检测' in test_select or '麦克风+monkey检测' in test_select:
                if '扬声器检测' in test_select or '麦克风检测' in test_select:
                    run_command(f"adb -s {device_ip} shell am force-stop com.h3c.filemanager")
                    run_command(f"adb -s {device_ip} shell am force-stop com.h3c.screencap")
                    run_command(f"adb -s {device_ip} shell am force-stop org.videolan.vlc")
                    back_to_home(device_ip, logger)
                run_monkey(logger, device_ip)
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                run_command(f"adb -s {device_ip} shell am force-stop com.h3c.filemanager")
                run_command(f"adb -s {device_ip} shell am force-stop com.h3c.screencap")
                run_command(f"adb -s {device_ip} shell am force-stop org.videolan.vlc")
                back_to_home(device_ip, logger)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '扬声器+monkey检测' in test_select:
                    # 扬声器检查
                    if check_speaker(rms_single_speaker, record_time, logger, device_ip, d) is False:
                        speaker_check_tag += 1
                        if speaker_check_tag > 1:
                            send_message(f"扬声器无声", logger)
                            catch_logs(device_ip, logger, "speaker_monkey_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            run_command(f"adb -s {device_ip} shell am force-stop com.h3c.filemanager")
                            run_command(f"adb -s {device_ip} shell am force-stop com.h3c.screencap")
                            run_command(f"adb -s {device_ip} shell am force-stop org.videolan.vlc")
                            back_to_home(device_ip, logger)
                            continue
                    else:
                        speaker_check_tag = 0

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '桌面组件检测' in test_select:
                    # 扬声器检查
                    if check_desktop_widget(d, logger, device_ip, similarity,launcher_num) is True:
                        logger.info("桌面组件验证通过")
                    else:
                        logger.info("桌面组件验证不通过")
                        if stop_type_select == "是":
                            update_button_states(logger)  # 调用更新按钮状态的函数
                            sys.exit()
                        else:
                            test_fail_times_data += 1
                            run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '麦克风+monkey检测' in test_select:
                    # 检查麦克风,不通过则停止运行
                    if check_mic(d, rms_single_mic, device_ip, logger) is False:
                        mic_check_tag += 1
                        if mic_check_tag > 1:
                            send_message(f"麦克风无声", logger)
                            catch_logs(device_ip, logger, "microphone_monkey_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            run_command(f"adb -s {device_ip} shell am force-stop com.h3c.filemanager")
                            run_command(f"adb -s {device_ip} shell am force-stop com.h3c.screencap")
                            run_command(f"adb -s {device_ip} shell am force-stop org.videolan.vlc")
                            back_to_home(device_ip, logger)
                            continue
                    else:
                        mic_check_tag = 0

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if '空白等待30分钟(配合音频检测)' in test_select:
                logger.info("开始等待30分钟")
                interruptible_sleep(1800)
                logger.info("等待30分钟已完成")

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '相机检测' in test_select:
                    if android_or_win == "android":
                        # 检查相机，不通过则停止运行
                        if check_camera(d, logger, device_ip, similarity) is False:
                            logger.info("摄像头未正常加载")
                            send_message(f"摄像头未正常加载", logger)
                            catch_logs(device_ip, logger, "camera_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            logger.info("摄像头正常加载")
                            back_to_home(device_ip, logger)
                    if android_or_win == 'win':
                        if check_win_camera(logger) is True:
                            logger.info("相机正常加载")
                        else:
                            logger.info("相机未正常加载")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if 'U盘检测' in test_select:
                    if android_or_win == 'android':
                        # 检查U盘，不通过则停止运行
                        if check_udisk(logger, d, u_disk_name, device_ip) is False:
                            catch_logs(device_ip, logger, "u_disk_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        logger.info("U盘正常加载")
                    if android_or_win == 'win':
                        if check_win_u_disk(logger) is True:
                            logger.info("U盘正常加载")
                        else:
                            logger.info("U盘未正常加载")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '光感检测' in test_select:
                    if android_or_win == 'win':
                        if check_win_light_sensor(logger) is True:
                            logger.info("win下光感检测通过")
                        else:
                            logger.info("win下光感检测不通过")
                            send_message(f"光感检测异常", logger)
                            if stop_type_select == "是":
                                update_button_states(logger)
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '蓝牙检测' in test_select:
                    if android_or_win == 'android':
                        # 安卓：先查蓝牙开关，开了再查目标设备是否已连接
                        if check_android_bt_switch(device_ip, logger) is False:
                            logger.info("安卓蓝牙开关未打开，蓝牙检测不通过")
                            send_message(f"安卓蓝牙开关未打开", logger)
                            catch_logs(device_ip, logger, "bluetooth_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        elif check_android_bt_connected(device_ip, bt_name, logger) is False:
                            logger.info("安卓目标蓝牙设备未连接，蓝牙检测不通过")
                            send_message(f"安卓目标蓝牙设备未连接", logger)
                            catch_logs(device_ip, logger, "bluetooth_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            logger.info("安卓蓝牙检测通过（开关已开且目标设备已连接）")
                    if android_or_win == 'win':
                        if check_win_bluetooth(logger) is True:
                            logger.info("win下蓝牙检测通过")
                        else:
                            logger.info("win下蓝牙检测不通过")
                            send_message(f"蓝牙检测异常", logger)
                            if stop_type_select == "是":
                                update_button_states(logger)
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            # ===========================================================================================================
            if run_tag == 0:
                if '充电检测' in test_select:
                    if android_or_win == "android":
                        # 检查充电状态，不通过则停止运行
                        power_on(power_ip, power_process_name, power_name_power, power_path, logger, power_sn)
                        interruptible_sleep(20)
                        if power_check_android(device_ip) is False:
                            logger.info("当前已打开电源按钮，实际未充电")
                            # send_message(f"充电状态检测异常", logger)
                            catch_logs(device_ip, logger, "camera_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            logger.info("当前正在充电，充电检测通过")
                        interruptible_sleep(on_off_interval)
                        power_off(power_ip, power_process_name, power_name_power, power_path, logger, power_sn)
                        interruptible_sleep(20)
                        if power_check_android(device_ip) is True:
                            # logger.info("当前已关闭电源按钮，实际正在充电")
                            send_message(f"充电状态检测异常", logger)
                            catch_logs(device_ip, logger, "power_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            logger.info("当前未在充电，充电检测通过")

                    if android_or_win == 'win':
                        power_on(power_ip, power_process_name, power_name_power, power_path, logger, power_sn)
                        interruptible_sleep(20)
                        if power_check_win(logger) is False:
                            logger.info("当前已打开电源按钮，实际未充电")
                            send_message(f"充电状态检测异常", logger)
                            catch_logs(device_ip, logger, "power_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            logger.info("当前正在充电，充电检测通过")
                        interruptible_sleep(60)
                        power_off(power_ip, power_process_name, power_name_power, power_path, logger, power_sn)
                        interruptible_sleep(20)
                        if power_check_win(logger) is True:
                            logger.info("当前已关闭电源按钮，实际正在充电")
                            send_message(f"充电状态检测异常", logger)
                            catch_logs(device_ip, logger, "camera_fail")
                            if stop_type_select == "是":
                                update_button_states(logger)  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            logger.info("当前未在充电，充电检测通过")

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                logger.info(f"第{test_times_data + 1}次测试正常,{test_type}设备")
            else:
                logger.info(f"第{test_fail_times_data}次测试失败,{test_type}设备")
            control_devices(power_ip, logger, device_ip, on_off_interval, power_process_name, power_path, power_name,
                            power_name_botton, time_set_sleep)
            interruptible_sleep(test_interval)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            test_times_data += 1
            root.after(0, lambda: test_count_var.set(f"压测次数：{test_times_data}次"))
            root.after(0, lambda: test_fail_count_var.set(f"失败次数：{test_fail_times_data}次"))
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.info(f"错误日志信息{error_msg}")
            continue
        # 确保无论测试循环如何结束，都会调用更新按钮状态的函数
    update_button_states(logger)
    logger.info("程序已退出。")


def toggle_pause(logger):
    global is_paused
    is_paused = not is_paused
    update_button_text()  # 暂停时只显示"继续"，恢复时重新启用暂停+停止按钮
    if is_paused:
        logger.info("已点击暂停按钮,程序暂停中,请等待")
    else:
        logger.info("已点击继续按钮,程序恢复运行")


def is_admin():
    """检测当前进程是否拥有管理员权限"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def restart_as_admin():
    """非管理员时，弹出UAC以管理员权限重新启动本程序；返回是否已成功发起提权"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的exe：直接以自身exe重启
        exe = sys.executable
        params = subprocess.list2cmdline(sys.argv[1:])
    else:
        # 以.py脚本运行：用python重启并带上脚本路径
        exe = sys.executable
        params = subprocess.list2cmdline([os.path.abspath(sys.argv[0])] + sys.argv[1:])
    try:
        # ShellExecuteW 的 "runas" 动词会触发UAC管理员权限弹窗；返回值>32表示成功发起
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
        return ret > 32
    except Exception:
        return False


if __name__ == '__main__':
    freeze_support()
    # 本程序需管理员权限运行(powercfg/杀进程/起模拟器/模拟键鼠等)。非管理员则弹UAC以管理员身份重启自身。
    if not is_admin():
        if restart_as_admin():
            sys.exit(0)  # 已拉起管理员实例，退出当前非管理员实例
        else:
            try:
                tkMessageBox.showerror("权限不足", "本程序需要管理员权限运行。\n请右键选择“以管理员身份运行”，或在UAC弹窗中点击“是”。")
            except Exception:
                pass
            sys.exit(1)

    # 设置当前设备息屏和睡眠时间为从不
    os.system("powercfg /change monitor-timeout-ac 0")
    os.system("powercfg /change standby-timeout-ac 0")
    os.system("powercfg /change monitor-timeout-dc 0")
    os.system("powercfg /change standby-timeout-dc 0")


    def is_instance_running(process_name):
        # 调用tasklist命令查找正在运行的进程
        call_result = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq %s' % process_name], shell=True)
        # 解码命令输出，适配Python 3
        output = call_result.decode(getpreferredencoding(False))
        # 统计进程实例个数
        count = output.count(process_name)
        return count


    if is_instance_running(process_name) > 2:
        print("另一个实例已经在运行。")
        sys.exit(0)

    frame_main()
