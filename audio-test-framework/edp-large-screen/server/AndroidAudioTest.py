# -*- coding: utf-8 -*-

"""
2024-10-31 修改点：
1、新增上下电时，去通知windows端去修改ini文件的配置
2、新增记录错误次数，即报错后不停止
3、新版本定义为1.2版本

2024-10-12 修改点：
1、修改model = YOLO(model_path)语句顺序，解决打包后闪退的问题
2、本地使用python3.11.9的环境进行打包，可打包成功
3、新版本定义为1.1版本

2024-8-7  修改pywifi格式，使能连接带密码的wifi
"""

from logging import handlers
import scipy.fft
import tkinter.messagebox as tkMessageBox
import psutil
import requests
import subprocess
import logging
import sys
import cv2
import os
import time
import wave
import pyaudio
import numpy as np
from ultralytics.models import YOLO
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import font
import threading
import json
from serial import Serial
from multiprocessing import freeze_support
from locale import getpreferredencoding
import zipfile
import shutil
import socket
import pywifi
from pywifi import const
from uiautomator2 import connect

current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # 当前工作目录
log_path = os.path.join(current_working_dir, 'logs')
current_time = datetime.now()
formatted_date = current_time.strftime("%m-%d")
monkey_log_path = os.path.join(log_path, f"monkey_{formatted_date}.log")
image_path = os.path.join(log_path, 'image_path')
model_path = os.path.join(os.path.join(current_working_dir, 'model'), 'n_best.pt')
# 创建名为'image_path'的新文件夹，如果已经存在则忽略
if not os.path.exists(image_path):
    os.makedirs(image_path)

model = YOLO(model_path)



kill_app_path = os.path.join(current_working_dir, 'kill_app.sh')
test_wav_path = os.path.join(current_working_dir, 'test.wav')  # 测试音频的存放路径
win_hdmi_record_path = os.path.join(current_working_dir, 'win_recorded_hdmi_in_audio.wav') # win测试hdmiin扬声器的音频路径
win_speaker_path = os.path.join(current_working_dir, 'win_speaker_audio.wav') # win测试扬声器的音频路径
test_wav_speaker_path = os.path.join(current_working_dir, 'recorded_speaker_audio.wav')  # 安卓测试本机录音文件的地址，即验证大屏的扬声器
test_wav_hdmi_in_path = os.path.join(current_working_dir, 'recorded_hdmi_in_audio.wav')  # 安卓测试本机录音文件的地址，即验证大屏HDMI IN的扬声器
test_wav_mic_path = os.path.join(current_working_dir, 'recorded_mic_audio.wav')  # 安卓测试大屏录音文件的地址，即验证大屏的麦克风
test_wav_mp4_path = os.path.join(current_working_dir, 'recorded_mic_audio.mp4')  # 安卓测试大屏录音文件视频的地址，用来分解为音频
screenshot_path = os.path.join(os.path.join(current_working_dir,'image'), "screenshot.jpg")
is_running = True
# 定义全局变量test_count_var
global test_count_var
test_count_var = None

# 定义全局变量test_fail_count_var
global test_fail_count_var
test_fail_count_var = None

is_paused = False
android_or_win = 'android'
global test_items_checkbuttons
test_items_checkbuttons = {}

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


def get_logger(log_filename, level=logging.INFO, when='D', back_count=0, text_widget=None):
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
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    LOG_ROOT = dirname
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

    # 如果提供了Text控件，创建一个TextHandler并添加到日志器
    if text_widget:
        text_handler = TextHandler(text_widget)
        text_handler.setLevel(level)
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)

    return logger


def load_config(config_path, test_items):
    default_config = {
        'device_ip': '192.168.1.100',
        'camera_select':'0',
        'black_check_times': '50',
        'power_ip': 'emulator-5554',
        'connect_wifi_name':'setting-5G-open',
        'wifi_password':"YOUR_WIFI_PASSWORD",
        'serial_port':'3',
        'rms_hdmi_extend': '100000000000',
        'rms_hdmi_in': '100000000000',
        'rms_speaker': '100000000000',
        'rms_mic': '100000000000',
        'record_time': '10',
        'power_sn':'0',
        'power_path': r'D:\leidian\LDPlayer9\dnplayer.exe',
        'reboot_times': '20',
        'test_interval': '80',
        'power_process_name': 'dnplayer.exe',
        'selected_method': '上下电',
        'test_project': '嘿板',
        'stop_type':'是',
        'selected_test_items': {item: True for item in test_items},
    }
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
    except:
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
    if type_var.get() == '嘿板':
        method_combobox['values'] = ('重启', '上下电', "息屏唤醒", "串口开关机", "HOME键开关机")
    elif type_var.get() == '8kmega（单安卓或双系统切换）' or type_var.get() == 'edpmega（单安卓或双系统切换）':
        method_combobox['values'] = ('重启', '上下电', '息屏唤醒', '双系统切换', 'HOME键开关机')
    elif type_var.get() == "医科通单屏模式" or type_var.get() == "医科通双屏模式":
        method_combobox['values'] = ('重启', '上下电', '息屏唤醒', 'HOME键开关机')
    elif type_var.get() == '单win（非双系统切换）':
        method_combobox['values'] = ('重启', '上下电', '串口开关机', 'HOME键开关机')
    elif type_var.get() == "OEM副屏":
        method_combobox['values'] = ('上下电', 'HOME键开关机','息屏唤醒')

    # 更新测试条目和配置项的可见性
    on_method_changed()

def on_method_changed(event=None):
    global type_var
    global method_var
    global stop_var
    global test_items_vars
    global test_items_checkbuttons  # 使用全局变量
    if type_var.get() == '嘿板' or type_var.get() == '医科通单屏模式' or type_var.get() == '医科通双屏模式':
        if method_var.get() == '重启' or method_var.get() == '上下电' or method_var.get() == '串口开关机' or method_var.get() == 'HOME键开关机':
            for item in ['黑屏检测', 'HDMI Record检测', 'HDMI Extend检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测', '麦克风+monkey检测','空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测']:
                test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
            test_items_vars['公共分区检查'].set(False)
            test_items_checkbuttons['公共分区检查'].pack_forget()
        if method_var.get() == '息屏唤醒':
            for item in ['黑屏检测', 'HDMI Record检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测', '麦克风+monkey检测','空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测']:
                test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
            test_items_vars['公共分区检查'].set(False)
            test_items_vars['HDMI Extend检测'].set(False)
            test_items_checkbuttons['公共分区检查'].pack_forget()
            test_items_checkbuttons['HDMI Extend检测'].pack_forget()
    if type_var.get() == '8kmega（单安卓或双系统切换）' or type_var.get() == 'edpmega（单安卓或双系统切换）':
        if method_var.get() == '重启' or method_var.get() == '上下电' or method_var.get() == '串口开关机' or method_var.get() == '双系统切换' or method_var.get() == 'HOME键开关机':
            for item in ['黑屏检测', 'HDMI Record检测', 'HDMI Extend检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测', '麦克风+monkey检测','空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测','公共分区检查']:
                test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
        if method_var.get() == '息屏唤醒':
            for item in ['黑屏检测', 'HDMI Record检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测', '麦克风+monkey检测','空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测','公共分区检查']:
                test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
            test_items_vars['HDMI Extend检测'].set(False)
            test_items_checkbuttons['HDMI Extend检测'].pack_forget()
    if type_var.get() == '单win（非双系统切换）':
        if method_var.get() == '重启' or method_var.get() == '上下电' or method_var.get() == '串口开关机' or method_var.get() == 'HOME键开关机':
            for item in ['黑屏检测', 'HDMI Record检测','扬声器检测', '麦克风检测','空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测','公共分区检查']:
                test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
            for item1 in ['HDMI Extend检测', '扬声器+monkey检测', '麦克风+monkey检测']:
                test_items_vars[item1].set(False)
                test_items_checkbuttons[item1].pack_forget()
    if type_var.get() == 'OEM副屏':
        for item in ['黑屏检测', 'HDMI Record检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测',
                     '麦克风+monkey检测', '空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测']:
            test_items_checkbuttons[item].pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)  # 显示
        test_items_vars['HDMI Extend检测'].set(False)
        test_items_checkbuttons['HDMI Extend检测'].pack_forget()
        test_items_vars['公共分区检查'].set(False)
        test_items_checkbuttons['公共分区检查'].pack_forget()

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
    if method_var.get() == '重启' or method_var.get() == '息屏唤醒' or method_var.get() == '双系统切换':
        # 隐藏特定的配置项
        for key in ['power_ip', 'power_sn', 'power_path', 'reboot_times', 'power_process_name', 'power_name','serial_port']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        if method_var.get() == '重启':
            config_labels['test_interval'].grid()
            config_entries['test_interval'].grid()
            config_labels['android_or_win'].grid_remove()
            config_entries['android_or_win'].grid_remove()
        if method_var.get() == '息屏唤醒':
            config_labels['test_interval'].grid()
            config_entries['test_interval'].grid()
            config_labels['android_or_win'].grid_remove()
            config_entries['android_or_win'].grid_remove()
        if method_var.get() == '双系统切换':
            config_labels['android_or_win'].grid()
            config_entries['android_or_win'].grid()
    elif method_var.get() == '串口开关机':
        # 显示串口配置项，隐藏其他不相关配置项
        config_labels['serial_port'].grid()
        config_entries['serial_port'].grid()
        config_labels['test_interval'].grid()
        config_entries['test_interval'].grid()
        for key in ['power_ip', 'power_sn', 'power_path', 'reboot_times', 'power_process_name', 'power_name', 'android_or_win']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
    elif method_var.get() == '上下电':
        for key in ['serial_port','android_or_win']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['power_ip', 'power_sn', 'power_path', 'reboot_times', 'power_process_name', 'power_name', 'test_interval']:
            config_labels[key].grid()
            config_entries[key].grid()

    elif method_var.get() == 'HOME键开关机':
        for key in ['serial_port','android_or_win','power_sn']:
            config_labels[key].grid_remove()
            config_entries[key].grid_remove()
        for key in ['power_ip', 'power_path', 'reboot_times', 'power_process_name', 'test_interval','power_name']:
            config_labels[key].grid()
            config_entries[key].grid()

    # 根据测试项的勾选状态更新配置项的可见性
    if not test_items_vars['黑屏检测'].get():
        config_labels['camera_select'].grid_remove()
        config_entries['camera_select'].grid_remove()
        config_labels['black_check_times'].grid_remove()
        config_entries['black_check_times'].grid_remove()
    else:
        config_labels['camera_select'].grid()
        config_entries['camera_select'].grid()
        config_labels['black_check_times'].grid()
        config_entries['black_check_times'].grid()

    if not test_items_vars['HDMI Record检测'].get():
        config_labels['rms_hdmi_in'].grid_remove()
        config_entries['rms_hdmi_in'].grid_remove()
    else:
        config_labels['rms_hdmi_in'].grid()
        config_entries['rms_hdmi_in'].grid()

    if not test_items_vars['HDMI Extend检测'].get():
        config_labels['rms_hdmi_extend'].grid_remove()
        config_entries['rms_hdmi_extend'].grid_remove()
    else:
        config_labels['rms_hdmi_extend'].grid()
        config_entries['rms_hdmi_extend'].grid()


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


    if not test_items_vars['扬声器检测'].get() and not test_items_vars['麦克风检测'].get() and not test_items_vars['HDMI Extend检测'].get() and not test_items_vars['HDMI Record检测'].get() and not test_items_vars['扬声器+monkey检测'].get() and not test_items_vars['麦克风+monkey检测'].get():
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

    if type_var.get() == '单win（非双系统切换）':
        config_labels['test_interval'].grid_remove()
        config_entries['test_interval'].grid_remove()
        config_labels['device_ip'].grid_remove()
        config_entries['device_ip'].grid_remove()
    else:
        config_labels['device_ip'].grid()
        config_entries['device_ip'].grid()

# # 当测试方法发生变化时调用
# def on_method_changed(event=None):
#     update_config_visibility()
#
#
# # 当测试项勾选状态发生变化时调用
# def on_test_item_changed():
#     update_config_visibility()


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


    # 创建主窗口
    root = tk.Tk()
    root.title('多功能压测脚本V1.2')

    def on_closing():
        logging.shutdown()  # 清理日志系统
        root.destroy()

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
    # 获取当前时间
    current_time = datetime.now()

    # 以月-日的形式输出
    formatted_date = current_time.strftime("%m-%d")
    logger = get_logger(f'audio_test_{formatted_date}.log', text_widget=log_text)

    # 第一项 - 选择测试项目
    type_label = ttk.Label(left_frame, text="选择测试项目", font=bold_font)
    type_label.pack(side=tk.TOP, anchor=tk.W)

    type_var = tk.StringVar()
    type_combobox = ttk.Combobox(left_frame, textvariable=type_var, state='readonly')
    type_combobox['values'] = ('嘿板', '8kmega（单安卓或双系统切换）', 'edpmega（单安卓或双系统切换）',"医科通单屏模式","医科通双屏模式","单win（非双系统切换）","OEM副屏")
    type_combobox.pack(side=tk.TOP, fill=tk.X)
    type_var.set("嘿板")
    type_combobox.bind('<<ComboboxSelected>>', on_type_changed)

    # 第二项 - 选择测试方法
    method_label = ttk.Label(left_frame, text="选择测试方法", font=bold_font)
    method_label.pack(side=tk.TOP, anchor=tk.W,pady=(10, 0))

    method_var = tk.StringVar()
    method_combobox = ttk.Combobox(left_frame, textvariable=method_var, state='readonly')
    method_combobox['values'] = ('重启', '上下电',"息屏唤醒","串口开关机","双系统切换","HOME键开关机")
    method_combobox.pack(side=tk.TOP, fill=tk.X)
    method_var.set("上下电")
    method_combobox.bind('<<ComboboxSelected>>', on_method_changed)

    # 第三项 - 选择失败是否停止
    stop_label = ttk.Label(left_frame, text="失败是否停止", font=bold_font)
    stop_label.pack(side=tk.TOP, anchor=tk.W,pady=(10, 0))

    stop_var = tk.StringVar()
    stop_combobox = ttk.Combobox(left_frame, textvariable=stop_var, state='readonly')
    stop_combobox['values'] = ('是', '否')
    stop_combobox.pack(side=tk.TOP, fill=tk.X)
    stop_var.set("是")

    # 第四项 - 选择测试项
    test_items_label = ttk.Label(left_frame, text="选择测试项", font=bold_font)
    test_items_label.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))

    # 填充测试项到列表框中，并默认全选这些项
    test_items = ['黑屏检测', 'HDMI Record检测', 'HDMI Extend检测', '扬声器检测', '麦克风检测', '扬声器+monkey检测', '麦克风+monkey检测','空白等待30分钟(配合音频检测)', '相机检测', 'U盘检测','公共分区检查']

    # 创建勾选框
    test_items_vars = {item: tk.BooleanVar(value=True) for item in test_items}
    for item, var in test_items_vars.items():
        checkbutton = ttk.Checkbutton(left_frame, text=item, variable=var)
        checkbutton.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, expand=False)
        test_items_checkbuttons[item] = checkbutton  # 保存引用

    # 第四项 - 填写测试配置
    config_label = ttk.Label(right_frame, text="填写测试配置", font=bold_font)
    config_label.grid(column=0, row=0, columnspan=2, sticky=tk.W, pady=5)

    # 测试配置项的名称和提示文本
    config_items = [
        ('device_ip', '大屏IP'),
        ('android_or_win', '当前系统（android or win）'),
        ('camera_select', '相机选择'),
        ('black_check_times', '黑屏检测次数'),
        ('power_ip', '模拟器IP'),
        ('connect_wifi_name', '连接的wifi名称(不连wifi填无)'),
        ('wifi_password', 'wifi密码（无密码填无）'),
        ('serial_port', '串口端口号（只填数字）'),
        ('rms_hdmi_extend', 'HDMI Extend扬声器阈值'),
        ('rms_hdmi_in', 'HDMI Record扬声器阈值'),
        ('rms_speaker', '扬声器阈值'),
        ('rms_mic', '麦克风阈值'),
        ('record_time', '录音时长'),
        ('u_disk_name', 'U盘名称(多个以英文,分隔)'),
        ('power_sn', '智能设备端口'),
        ('power_path', '模拟器应用的安装地址'),
        ('reboot_times', '测试多少次重启模拟器'),
        ('power_process_name', '模拟器进程名称'),
        ('power_name', '智能设备的名称'),
        ('test_interval', '测试间隔（只填数字，单位S）'),
        ('tester_project_type', '测试项目'),
        ('tester', '测试人员'),
        ('device_sn', '测试机器'),
    ]

    # method_combobox.bind('<<ComboboxSelected>>', on_method_changed)
    # 为每个测试项的勾选框绑定事件
    for checkbutton_var in test_items_vars.values():
        checkbutton_var.trace('w', lambda *args: update_config_visibility())
    # 用于存储配置项输入框变量的字典
    config_vars = {}
    config_labels = {}
    config_entries = {}
    # 读取配置文件
    config_path = 'config.json'
    loaded_config = load_config(config_path, test_items)
    # 为每个配置项创建一个标签和一个输入框
    for index, (key, label_text) in enumerate(config_items):
        # 创建标签
        label = ttk.Label(right_frame, text=label_text)
        label.grid(column=0, row=index + 1, sticky=tk.W, pady=2)
        config_labels[key] = label

        # 创建输入框并将其与一个StringVar变量绑定
        entry_var = tk.StringVar()
        entry = ttk.Entry(right_frame, textvariable=entry_var)
        entry.grid(column=1, row=index + 1, sticky=(tk.W, tk.E), pady=2)
        config_entries[key] = entry
        # 将StringVar变量存储在字典中，以便后续访问
        config_vars[key] = entry_var

    # 应用配置到界面
    for key, value in loaded_config.items():
        if key == 'test_project':
            type_var.set(value)  # 设置测试项目
        if key == 'selected_method':
            method_var.set(value)  # 设置测试方法
        if key == 'stop_type':
            stop_var.set(value)  # 设置停止方式
        elif key == 'selected_test_items':
            for item, selected in value.items():
                test_items_vars[item].set(selected)  # 设置测试项
        else:
            clean_key = key.strip()
            if clean_key in config_vars:
                config_vars[clean_key].set(value)

    # 初始化界面
    update_config_visibility()
    on_type_changed()  # 确保初始测试项目的设置正确反映在界面上
    # 配置右侧Frame的列，使输入框可以随窗口大小调整
    right_frame.columnconfigure(1, weight=1)

    # 如果有更多的配置项需要垂直滚动，可以考虑添加一个滚动条

    # 设置权重，确保右侧配置部分的输入框随窗口伸缩
    for i in range(len(config_items) + 1):
        right_frame.rowconfigure(i, weight=1)

    # 可选：如果有更多的配置项需要滚动，可以添加右侧配置部分的滚动条
    # config_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL)
    # config_scrollbar.grid(column=2, row=0, sticky=(tk.N, tk.S), rowspan=len(config_items) + 1)
    # 注意：这需要你将右侧配置部分的控件放入一个Canvas或者Text widget之类的可滚动容器中

    # 第四项-创建底部按钮Frame
    bottom_frame = ttk.Frame(main_frame, padding="10 10 10 10")
    bottom_frame.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E))
    main_frame.rowconfigure(1, weight=0)

    # 创建一个用于均匀分布控件的容器Frame
    buttons_frame = ttk.Frame(bottom_frame)
    buttons_frame.pack(side=tk.LEFT, expand=False, fill=tk.X)

    # # 创建显示当前压测次数的标签
    # test_count_var.set("压测次数：0次")
    # test_count_label = ttk.Label(bottom_frame, textvariable=test_count_var)
    # test_count_label.pack(side=tk.LEFT, expand=True)
    #
    # # 创建显示当前压测失败次数的标签
    # test_fail_count_var.set("失败次数：0次")
    # test_fail_count_label = ttk.Label(bottom_frame, textvariable=test_fail_count_var)
    # test_fail_count_label.pack(side=tk.LEFT, expand=True)

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
    stop_button = ttk.Button(bottom_frame, text="结束", command=lambda: on_stop_button_clicked(logger),state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, expand=True)

    # 创建结束按钮
    open_logs = ttk.Button(bottom_frame, text="打开日志文件夹", command=on_open_log_folder_clicked)
    open_logs.pack(side=tk.LEFT, expand=True)

    # 设置主窗口的最小大小
    root.minsize(600, 400)

    # 设置main_frame的网格权重，确保它可以扩展到整个窗口
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # 开始主循环
    root.mainloop()


# 在on_start_test函数中添加一个helper函数来更新按钮状态
def update_button_states():
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
    log_text.delete("1.0",tk.END)
    log_text.configure(state="disabled")

    # 获取所有配置项的值
    configs_to_save = {k: v.get() for k, v in config_vars.items()}

    # 获取并保存测试项目
    configs_to_save['test_project'] = type_var.get()

    # 获取并保存测试方法
    configs_to_save['selected_method'] = method_var.get()

    # 获取并保存停止方式
    configs_to_save['stop_type'] = stop_var.get()

    # 获取并保存选中的测试项
    configs_to_save['selected_test_items'] = {item: var.get() for item, var in test_items_vars.items()}
    # 保存到配置文件
    save_config(configs_to_save, 'config.json')

    # 获取测试项目
    test_project = type_var.get()

    # 获取测试方法
    selected_method = method_var.get()

    # 获取停止方式
    stop_type = stop_var.get()

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

    if selected_method == "重启" and "HDMI Extend检测" in selected_test_items:
        tk.messagebox.showerror("错误", "重启下目前无法进行HDMI Extend检测项测试,请取消该项目的勾选")
        return  # 退出函数，不开始测试


    # 启动线程来执行on_start函数
    test_thread = threading.Thread(target=on_start_test,
                                   args=(test_project,selected_method,stop_type, selected_test_items, test_configs, root, logger))
    test_thread.start()
    start_button['state'] = tk.DISABLED  # 禁用开始按钮
    pause_button['state'] = tk.NORMAL  # 启用暂停按钮
    stop_button['state'] = tk.NORMAL  # 启用结束按钮


def on_start_test(test_project,selected_method, stop_type,selected_test_items, test_configs, root, logger):
    # 这里是处理测试开始逻辑的地方
    # 你可以使用selected_method, selected_test_items, test_configs变量
    test_project_type = test_project
    test_type = selected_method
    stop_type_select = stop_type
    test_select = selected_test_items
    test_Config = test_configs
    on_start(test_project_type,test_type, stop_type_select,test_select, test_Config, root, logger)


# 定义按钮点击事件的处理函数
def on_open_log_folder_clicked():
    os.startfile(log_path)


def reopen_power(power_process_name, power_path, logger):
    logger.info("杀掉模拟器进程")
    kill_process_by_name(power_process_name, logger)
    time.sleep(10)
    logger.info("重新打开模拟器")
    app1 = subprocess.Popen(power_path)
    logger.info(app1)
    time.sleep(40)


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

# 安卓设备回到桌面------黑板mega不一致
def start_test(logger,ip):
    run_command(f"adb -s {ip} shell chmod 777 /data/local/tmp/kill_app.sh")
    run_command(f"adb -s {ip} shell ./data/local/tmp/kill_app.sh")
    logger.info("已关闭所有应用")
    time.sleep(3)


# 安卓设备开始录屏
def android_record(d,logger,project):
    d.app_start("com.h3c.screencap", "com.h3c.screencap.ui.ActivityMain")
    try:
        # 等待并点击麦克风按钮
        if d(text="麦克风").exists(timeout=10):
            d(text="麦克风").click()
        else:
            logger.info("未找到麦克风按钮")
        time.sleep(5)
        # 等待并点击开始录音按钮
        if d(resourceId="com.h3c.screencap:id/tv_record").exists(timeout=20):
            d(resourceId="com.h3c.screencap:id/tv_record").click()
        else:
            logger.info("未找到录音按钮")
    except Exception as e:
        logger.info(f"遇到错误: {e}")

# 安卓设备开始录屏
def android_record_OEM(d):
    if d(resourceId="com.ifpdos.systembar:id/left_arrow_view").exists(timeout=2):
        d(resourceId="com.ifpdos.systembar:id/left_arrow_view").click()
    time.sleep(2)
    d.xpath(
        '//*[@resource-id="com.ifpdos.systembar:id/rcy_bar"]/android.widget.LinearLayout[11]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').click()
    time.sleep(2)
    d(text="录屏").click(timeout = 3)
    time.sleep(2)
    d.xpath(
        '//*[@resource-id="com.ifpdos.osrecord:id/toolbar_root_layout_recycleView"]/android.widget.RelativeLayout[1]').click()


def save_record_to_local(d):
    d.set_fastinput_ime(True)
    if d(resourceId="com.h3c.screencap:id/start_layout").exists(timeout=2):
        d(resourceId="com.h3c.screencap:id/start_layout").click()

        # 点击 "本地保存" 按钮
    if d(text="本地保存").exists(timeout=10):
        d(text="本地保存").click()
    time.sleep(5)
        # 设置文件名
    if d(resourceId="com.h3c.screencap:id/editFileName").exists(timeout=1):
        d(resourceId="com.h3c.screencap:id/editFileName").send_keys("recorded_mic_audio")

        # 点击 "保存" 按钮
    if d(text="保存").exists(timeout=1):
        d(text="保存").click()

        # 如果存在 "替换" 按钮，点击它
    if d(text="替换").exists(timeout=1):
        d(text="替换").click()
def click_set(d, x, y, selector_str=None, **kwargs):
    if selector_str:
        selector = d(**{selector_str.split('=')[0]: selector_str.split('=')[1]})
    else:
        selector = d(**kwargs)

        # 获取元素的当前位置并根据 x, y 偏移量计算点击位置
    if selector.exists:
        bounds = selector.info['bounds']
        center_x = (bounds['left'] + bounds['right']) / 2
        center_y = (bounds['top'] + bounds['bottom']) / 2
        click_x = center_x + x
        click_y = center_y + y

        d.click(click_x, click_y)


# 安卓设备结束录屏,并保存录屏文件到本地------黑板mega不一致
def android_stop_record(d,project):
    screen_mode = d.shell("wm size").output.split(":")[1].strip()
    pos_tv_time = d(resourceId="com.h3c.screencap:id/tvTime").center()
    if project == "8kmega（单安卓或双系统切换）" or project == "医科通单屏模式" or project == "edpmega（单安卓或双系统切换）":
        pos_stop = [pos_tv_time[0] + d.window_size()[0] * 0.068, pos_tv_time[1]]
    elif project == "医科通双屏模式" or project == "嘿板":
        if screen_mode == "11520x2160":
            pos_stop = [pos_tv_time[0] + d.window_size()[0] * 0.022, pos_tv_time[1]]
        elif screen_mode == "3840x2160":
            pos_stop = [pos_tv_time[0] + d.window_size()[0] * 0.068, pos_tv_time[1]]
        else:
            pos_stop = [pos_tv_time[0] + d.window_size()[0] * 0.034, pos_tv_time[1]]

    d.long_click(pos_tv_time[0], pos_tv_time[1], duration=2)
    d.click(pos_stop[0], pos_stop[1])

    time.sleep(2)
    if project == "8kmega（单安卓或双系统切换）" or project == "医科通单屏模式" or project == "edpmega（单安卓或双系统切换）":
        d.click(d.window_size()[0] * 0.5, d.window_size()[1] * 0.8)
        save_record_to_local(d)
    if project == "医科通双屏模式":
        d.click(d.window_size()[0] * 0.25, d.window_size()[1] * 0.8)
        save_record_to_local(d)
    if project == "嘿板":
        if d(resourceId="com.h3c.screencap:id/tvTime").exists(timeout=2):
            d(resourceId="com.h3c.screencap:id/tvTime").click()
        if d(resourceId="com.h3c.screencap:id/btnStop").exists(timeout=2):
            d(resourceId="com.h3c.screencap:id/btnStop").click()
        save_record_to_local(d)
    else:
        save_record_to_local(d)

def android_stop_record_OEM(d):
    d.xpath(
        '//*[@resource-id="com.ifpdos.osrecord:id/toolbar_root_layout_recycleView"]/android.widget.RelativeLayout[3]/android.widget.ImageView[1]').click()
    time.sleep(2)
    d(text="取消").click()
    time.sleep(2)
    d(text="退出").click()
    time.sleep(2)
    d.click(0.141, 0.617)
    time.sleep(2)

# 安卓设备录屏后复制录屏文件到本地,并分解录屏文件为录音文件
def copy_to_local(d,ip, logger,project):
    logger.info("从安卓设备复制录音文件到本地")
    if project == 'OEM副屏':
        movie = run_command(f'adb -s {ip} shell ls sdcard/Record').strip()
        old_file_path = f"/sdcard/Record/{movie}"
        new_file_path = f"/sdcard/Record/recorded_mic_audio.mp4"
        run_command(f'adb -s {ip} shell mv {old_file_path} {new_file_path}')
        run_command(
            f'adb -s {ip} pull sdcard/Record/recorded_mic_audio.mp4 {current_working_dir}/recorded_mic_audio.mp4')
    else:
        run_command(
            f"adb -s {ip} pull /sdcard/录屏文件/recorded_mic_audio.mp4 {current_working_dir}/recorded_mic_audio.mp4")
    cmd_command = "ffmpeg.exe -i recorded_mic_audio.mp4 -vn recorded_mic_audio.wav"
    os.chdir(current_working_dir)  # 将当前工作目录更改为指定的文件夹路径
    run_command(cmd_command)

# 复制本地的音频文件到安卓设备
def copy_to_android(device_ip, logger):
    try:
        run_command(f"adb -s {device_ip} shell  mkdir /sdcard/AAA")
    except Exception as makdir_error:
        logger.info(makdir_error)
    logger.info("复制本地的音频文件到安卓设备")
    run_command(f"adb -s {device_ip} push {current_working_dir}/test.wav /sdcard/AAA")


# 安卓设备上播放音频------黑板mega不一致
def play_audio_android(ip,project,d):
    if project == "OEM副屏":
        run_command(f'adb -s {ip} shell am start -a android.intent.action.VIEW -d file:///sdcard/AAA/test.wav -t audio/wav')
    else:
        run_command(f"adb -s {ip} shell am start com.h3c.filemanager/.ui.ActivityMain")
        time.sleep(5)
        if project == "医科通单屏模式" or project == "8kmega（单安卓或双系统切换）" or project == "edpmega（单安卓或双系统切换）":
            d.click(d.window_size()[0] * 0.5, d.window_size()[1] * 0.8)
        if project == "医科通双屏模式":
            d.click(d.window_size()[0] * 0.25, d.window_size()[1] * 0.8)
        d(text="AAA").click(timeout=2)
        d(text="test.wav").click(timeout=2)
        try:
            d(text="音视频播放器").click()
        except:
            pass




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
    wf = wave.open(record_path, 'rb')
    signal = wf.readframes(-1)
    signal = np.frombuffer(signal, dtype=np.int16)
    spectrum = np.abs(scipy.fft.fft(signal))
    # 计算频谱能量
    rms = np.sum(spectrum)
    logger.info(rms)
    return rms


# 重启安卓设备
def reboot_android(device_ip,logger,d,project):
    # run_command(f"adb -s {device_ip} shell reboot")
    start_test(logger, device_ip)

    if project == "8kmega（单安卓或双系统切换）" or project == "医科通单屏模式" or project == "edpmega（单安卓或双系统切换）" or project == "医科通双屏模式":
        # 等待并点击电源键图标
        if d(resourceId="com.h3c.launcher:id/iv_power").exists(timeout=5):
            d(resourceId="com.h3c.launcher:id/iv_power").click()
        # 等待并点击"重启"文字
        if d(text="重启").exists(timeout=5):
            d(text="重启").click()
    if project == "嘿板":
        # 等待并点击电源键图标
        if d(resourceId="com.h3c.launcher:id/iv_power_key").exists(timeout=5):
            d(resourceId="com.h3c.launcher:id/iv_power_key").click()

        # 等待并点击重启图标
        if d(resourceId="com.h3c.launcher:id/iv_reboot").exists(timeout=5):
            d(resourceId="com.h3c.launcher:id/iv_reboot").click()

        # 等待并点击"重启"文字
        if d(text="重启").exists(timeout=5):
            d(text="重启").click()

#息屏唤醒
def close_screen_android(device_ip,logger):
    logger.info("发送息屏指令")
    run_command(f"adb -s {device_ip} shell input keyevent 223")
    time.sleep(5)
    is_close = run_command(f'adb -s {device_ip} shell "dumpsys deviceidle | grep mScreenOn"').split("=")[1].strip()
    if is_close != "false":
        return False
    run_command(f"adb -s {device_ip} shell input keyevent 224")
    logger.info("发送唤醒指令")
    time.sleep(5)
    is_open = run_command(f'adb -s {device_ip} shell "dumpsys deviceidle | grep mScreenOn"').split("=")[1].strip()
    if is_open != "true":
        return False


def kill_process_by_name(process_name, logger):
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            proc.kill()
            logger.info(f"进程 {process_name} 已被终止")
            return
    logger.info(f"没有找到进程 {process_name}")


def comnon_to_power(power_ip, power_sn, power_name):
    # 获取ADB设备列表
    recheck = 0
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接，devices信息为{devices}")
    d = connect(power_ip)
    while not d(resourceId=f"com.oray.sunlogin:id/iv_power_strip_s{power_sn}").exists(timeout=5):
        if d(text="向日葵远程控制").exists(timeout=3):
            d(text="向日葵远程控制").click()
        if d(text="开机设备").exists(timeout=3):
            d(text="开机设备").click()
        if d(text=power_name).exists(timeout=3):
            d(text=power_name).click()
        if d(text="显示列表").exists(timeout=3):
            d(text="显示列表").click()
        if d(text="确定").exists(timeout=3):
            d(text="确定").click()
        if d(resourceId="com.oray.sunlogin:id/tv_offline_power_strip_tip").exists(timeout=3):
            d(resourceId="com.oray.sunlogin:id/fl_back").click()
            time.sleep(2)
            d(text=power_name).click()
        recheck += 1
        if recheck > 5:
            raise RuntimeError("命令执行失败: 尝试打开模拟器进入到电源按钮界面失败")

def comnon_to_home_on(power_ip,power_name):
    # 获取ADB设备列表
    recheck = 0
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接，devices信息为{devices}")
    d = connect(power_ip)
    # 获取设备的屏幕尺寸
    screen_height = d.info['displayHeight']
    screen_width = d.info['displayWidth']
    while not d(text="空闲").exists(timeout=5):
        if d(text="智能生活").exists(timeout=5):
            d(text="智能生活").click()
        if d(text=power_name).exists(timeout=5):
            d(text=power_name).click()
        d.swipe(screen_width / 2, screen_height * 0.8, screen_width / 2, screen_height * 0.2)
        recheck += 1
        if recheck > 5:
            raise RuntimeError(f"命令执行失败:尝试打开模拟器进入到电源按钮界面失败")

def check_and_reconnect(device_ip, power_ip, power_sn, power_path, power_process_name, power_name, logger,test_select):
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}

    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        reopen_power(power_process_name, power_path, logger)
    comnon_to_power(power_ip, power_sn, power_name)
    if android_or_win == 'android' and test_select != ['黑屏检测']:
        if f"{device_ip}:5555" not in device_status.keys() or device_status[f"{device_ip}:5555"].strip() != 'device':
            raise RuntimeError("设备未成功连接大屏ip")

def check_and_reconnect_home_on(device_ip, power_ip, power_path, power_process_name, logger,power_name,test_select):
    devices = get_adb_devices()
    logger.info(devices)
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}

    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        reopen_power(power_process_name, power_path, logger)
    comnon_to_home_on(power_ip,power_name)
    if android_or_win == 'android' and test_select != ['黑屏检测']:
        if f"{device_ip}:5555" not in device_status.keys() or device_status[f"{device_ip}:5555"].strip() != 'device':
            raise RuntimeError("设备未成功连接大屏ip")

def check_and_reconnect_except(device_ip, power_path, power_process_name, logger):
    run_command(f'adb connect {device_ip}')
    devices = get_adb_devices()
    logger.info(f"连接异常时的adb devices状态{devices}")
    reopen_power(power_process_name, power_path, logger)
    run_command(f"adb disconnect {device_ip}")
    run_command(f"adb connect {device_ip}")
    devices = get_adb_devices()
    logger.info(f"重新连接后的adb devices状态{devices}")

def check_and_reconnect_reboot(device_ip):
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if f"{device_ip}:5555" not in device_status.keys() or device_status[f"{device_ip}:5555"].strip() != 'device':
        time.sleep(5)
        raise RuntimeError("设备未成功连接大屏ip")

def check_and_reconnect_reboot_except(device_ip):
    run_command(f"adb disconnect {device_ip}")
    run_command(f'adb connect {device_ip}')

# 检查大屏的扬声器
def check_speaker(rms_single_speaker, record_time, logger,ip,project,d):
    logger.info("开始检查扬声器")
    logger.info("大屏开始播放音频")
    play_audio_android(ip,project,d)
    logger.info("本地设备开始录音")
    local_record(record_time, test_wav_speaker_path)
    time.sleep(20)
    rms_data_speaker = analysis_audio(test_wav_speaker_path, logger)
    if rms_data_speaker < rms_single_speaker:
        logger.info("扬声器无声")
        return False
    if rms_data_speaker > rms_single_speaker:
        logger.info("扬声器正常")
        return True


# 检查大屏的麦克风
def check_mic(d, rms_single_mic, ip, logger,project):
    d.shell(f'rm -rf sdcard/Record/*')
    start_test(logger, ip)
    time.sleep(2)
    logger.info("开始检查麦克风")
    if d(text = "关机").exists(timeout=20):
        d(text = "取消").click()
    logger.info("大屏开始录音")
    if project == 'OEM副屏':
        android_record_OEM(d)
    else:
        android_record(d,logger,project)
    logger.info("本地开始播放音频")
    time.sleep(2)
    play_audio_local(test_wav_path)
    logger.info("大屏结束录音")
    if project == 'OEM副屏':
        android_stop_record_OEM(d)
    else:
        android_stop_record(d, project)
    copy_to_local(d,ip, logger,project)  # 复制录音后文件到本地
    rms_data_mic = analysis_audio(test_wav_mic_path, logger)
    if rms_data_mic < rms_single_mic:
        logger.info("麦克风无声")
        return False
    if rms_data_mic > rms_single_mic:
        logger.info("麦克风正常")
        return True

# 检查相机是否连接正常
def check_camera_yiketong(d,project,logger, device_ip):
    start_test(logger, device_ip)
    d.app_start("com.h3c.camera", "com.h3c.camera.main.MainActivity")
    time.sleep(5)
    # 根据项目描述点击不同的位置
    if project == "医科通单屏模式":
        d.click(d.window_size()[0] * 0.5, d.window_size()[1] * 0.8)
    elif project == "医科通双屏模式":
        d.click(d.window_size()[0] * 0.25, d.window_size()[1] * 0.8)

    time.sleep(5)

    # 检查是否存在文本 "拍照"
    status = d(text="拍照").exists(timeout=5)
    return status

# 检查相机是否连接正常
def check_camera(d,logger,device_ip,project):
    start_test(logger, device_ip)
    if project == 'OEM副屏':
        run_command(f"adb -s {device_ip} shell am start com.dss.camera/.ui.activity.MainActivity")
    else:
        d.app_start("com.h3c.settings", "com.h3c.settings.main.ui.activity.SettingActivity")
    time.sleep(5)
    # 根据项目描述点击不同的位置
    if project in ["8kmega（单安卓或双系统切换）", "edpmega（单安卓或双系统切换）"]:
        d.click(d.window_size()[0] * 0.5, d.window_size()[1] * 0.8)

    if project == 'OEM副屏':
        if d(resourceId="com.dss.camera:id/iv_take_photo").exists(timeout=3):
            return True
        else:
            return False
    else:
        # 等待并点击“摄像头设置”
        if d(text="摄像头设置").exists(timeout=10):
            d(text="摄像头设置").click()

        time.sleep(5)

        # 检查是否存在“智能取景”文本
        status = d(text="智能取景").exists(timeout=5)
        return status


# 检查U盘是否正常识别
def check_udisk(logger,d, device_ip,u_disk_name,project):
    start_test(logger, device_ip)
    try:
        u_disk_name_list = u_disk_name.split(",")
    except:
        u_disk_name_list = u_disk_name
    if project == 'OEM副屏':
        run_command(f"adb -s {device_ip} shell am start com.seewo.easifinder/.FileBrowseMainActivity")
    else:
        d.app_start("com.h3c.filemanager", "com.h3c.filemanager.ui.ActivityMain")
    # 根据项目描述点击不同的位置
    if project in ["8kmega（单安卓或双系统切换）", "edpmega（单安卓或双系统切换）"]:
        d.click(d.window_size()[0] * 0.5, d.window_size()[1] * 0.8)

    time.sleep(5)
    for u_disk in u_disk_name_list:
        status = d(text=u_disk).exists(timeout=5)
        if not status:
            logger.info(f"名称为{u_disk}的U盘未检测到")
            send_message(f"名称为{u_disk}的U盘未检测到", logger)
            return False
    return True

#检查安卓下公共分区是否正常加载
def check_anroid_public_disk(devices_ip):
    # 构造ADB命令，以检查文件是否存在
    cmd = f"adb -s {devices_ip} shell if test -e /mnt/vendor/oem_share/ScreenShareLicense.txt; then echo True; else echo False; fi"
    # 执行ADB命令
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # 获取命令输出，并根据输出判断文件是否存在
    if 'True' in result.stdout:
        return True
    else:
        return False




def switch_power(tests, device_ip, power_ip, power_sn, power_path, reboot_times, power_process_name, power_name,
                 logger):
    # 获取ADB设备列表
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接,devices信息如下：{devices}")
    d = connect(power_ip)

    if d(text="显示列表").exists(timeout=5):
        d(text="显示列表").click()
    if d(text="确定").exists(timeout=5):
        d(text="确定").click()

    # 电源开启状态，关闭电源
    logger.info("关闭电源")
    d(resourceId="com.oray.sunlogin:id/fl_back").click()
    d(text=power_name).click()
    while d(resourceId=f"com.oray.sunlogin:id/cd_view_s{power_sn}").exists(timeout=5):
        logger.info("检测到当前电源为开启状态，关闭电源")
        time.sleep(3)
        d(resourceId=f"com.oray.sunlogin:id/iv_power_strip_s{power_sn}").click()
        if d(text="确认").exists(timeout=2):
            d(text="确认").click()
        d(resourceId="com.oray.sunlogin:id/fl_back").click()
        d(text=power_name).click()

    time.sleep(10)
    # 电源关闭状态，开启电源
    logger.info("开启电源")
    d(resourceId="com.oray.sunlogin:id/fl_back").click()
    d(text=power_name).click()
    while not d(resourceId=f"com.oray.sunlogin:id/cd_view_s{power_sn}").exists(timeout=3):
        logger.info("检测到当前电源为关闭状态，开启电源\n\n\n")
        time.sleep(3)
        d(resourceId=f"com.oray.sunlogin:id/iv_power_strip_s{power_sn}").click()
        if d(text="确认").exists(timeout=2):
            d(text="确认").click()
        d(resourceId="com.oray.sunlogin:id/fl_back").click()
        d(text=power_name).click()

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
            "text": f"测试项目：{tester_project_type}\n测试人员：{tester}\n测试机器：{device_sn}\n报错信息：{message}"
        }
    }
    push_report(webhook, message_body, logger)


def save_image(dst):
    timestamp = time.strftime("%m%d%H%M%S", time.localtime())
    filename = f"screen_fail_{timestamp}.jpg"  # 设定文件名，num为帧编号
    save_path = os.path.join(image_path, filename)  # 'path_to_big_screen_directory' 替换为大屏的文件保存路径
    cv2.imwrite(save_path, dst)


def catch_logs(ip, logger,type):
    # 切换到root用户
    run_command(f"adb -s {ip} shell setprop persist.h3c.root_state 123@qwe")
    run_command(f"adb -s {ip} root")

    # 创建目标目录
    timestamp = time.strftime("%m%d%H%M%S", time.localtime())
    target_dir = f"{current_working_dir}/logs/{timestamp}_{type}"
    zip_file_path = f"{current_working_dir}/logs/{timestamp}_{type}.zip"
    os.makedirs(target_dir, exist_ok=True)

    # 拉取日志文件的压缩包到本地
    run_command(f"adb -s {ip} pull /data/misc/logd {target_dir}")
    run_command(f"adb -s {ip} pull /data/vendor/logs {target_dir}")

    # 拉取日志文件到目标目录
    # run_command(f"adb -s {ip} pull /data/tombstones {target_dir}")
    # run_command(f"adb -s {ip} pull /data/anr {target_dir}")

    # 转存dmesg文件
    # run_command(f'adb -s {ip} shell "dmesg >/data/dmesg.txt"')
    # time.sleep(10)
    # run_command(f"adb -s {ip} pull /data/dmesg.txt {target_dir}")

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
        logger.info(f"清空日志文件夹时发生异常：{e}")

    logger.info(f"所有日志文件都已下载至 {target_dir}.")


def check_black(model, device_ip, logger,n,times):
    stop_tag = 0
    # 加载USB摄像头
    cap = cv2.VideoCapture(n, cv2.CAP_DSHOW)
    # Create output
    num = 0
    # 循环视频流
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            # print("num = ", num)
            # frame_time = cap.get(cv2.CAP_PROP_POS_MSEC)
            # print("frame_time", frame_time)
            if stop_tag > 2:
                logger.info("出现连续的多次黑屏，判断当前屏幕已黑屏，测试停止")
                return False
            # 对视频帧进行处理
            dst = cv2.resize(frame, [1920, 1080])
            results = model(dst)
            boxes = results[0].boxes
            num += 1
            if num % 10 != 0:
                continue
            if len(boxes) == 0:  # 检测不到云屏
                logger.info(f"第{stop_tag+1}次检测不到云屏\n")
                save_image(dst)
                catch_logs(device_ip, logger,"screen_fail")
                stop_tag += 1
                continue
            cls = boxes.cls[0]
            if cls == 0:
                save_image(dst)
                logger.info(f"第{stop_tag+1}次测试出现黑屏\n")
                catch_logs(device_ip, logger,"black_screen")
                stop_tag += 1
                continue
            elif cls == 1:
                save_image(dst)
                logger.info("未出现黑屏")
            real_num = int(num / 10)
            logger.info(f"第{real_num}次测试\n")
            stop_tag = 0
            if real_num > times:
                return True
        else:
            logger.info("未检测到相应的摄像头\n")
            return False
    # 释放VideoCapture对象并关闭显示窗口
    cap.release()
    cv2.destroyAllWindows()

def serial_power(serial_port,logger):
    power_off_code = bytes.fromhex("DDFF0700000031C10101F7BBCC")
    power_on_code = bytes.fromhex("DDFF0700000031C10100F6BBCC")
    power_on_res = "abab0700000031c10100f6cdcd"
    power_off_res = "abab0700000031c10101f7cdcd"
    ser = Serial(serial_port, 9600, timeout=10)  # 添加了波特率9600和超时时间1秒，这些数值根据实际情况进行调整

    if ser.isOpen():
        logger.info(f'串口已连接到{serial_port}')
    else:
        logger.info(f'串口无法连接到{serial_port}！！！')
        sys.exit()

    logger.info('发送关机码流,等待30s......')
    ser.write(power_off_code)
    res = ser.read(13).hex()
    logger.info(f"关机回复码流为{res}")
    if res != power_off_res:
        logger.info("关机回复码流错误，请检查机器状态！！！")
        return False
    time.sleep(30)

    logger.info('发送开机码流......')
    ser.write(power_on_code)
    res = ser.read(13).hex()
    logger.info(f"开机回复码流为{res}")
    if res != power_on_res:
        logger.info("开机回复码流错误，请检查机器状态！！！")
        return False

    ser.close()  # 完成后关闭串口


def match_image(template_path, screenshot_path, logger,threshold=0.8):
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

    return max_val >= threshold

def take_screenshot(device, filename,logger):
    logger.info("Taking screenshot...")
    device.screenshot(filename)
    time.sleep(3)
    if os.path.exists(filename):
        logger.info(f"Screenshot saved to {filename}")
    else:
        logger.error(f"Failed to save screenshot to {filename}")

def take_screenshot_OEM(d,ip,filepath,logger):
    # 获取当前时间
    now = datetime.now()
    # 格式化时间为 'YYYY-MM-DD'
    formatted_date = now.strftime('%Y-%m-%d').strip()
    d.shell(f'rm -rf sdcard/Notes/Mark/{formatted_date}/*')
    logger.info("Taking screenshot...")
    time.sleep(5)
    run_command(f'adb -s {ip} shell am start com.seewo.cropscreen/com.seewo.cropscreen.activity.CropActivity')
    time.sleep(3)
    if d(text="全屏").exists(timeout=10):
        d(text="全屏").click()
    if d(text="保存").exists(timeout=10):
        d(text="保存").click()
    if d(text="关闭窗口").exists(timeout=10):
        d(text="关闭窗口").click()
    if d(text="关闭").exists(timeout=10):
        d(text="关闭").click()
    time.sleep(2)
    close_hdmiin_oem(d)

    png_name = run_command(f'adb -s {ip} shell ls sdcard/Notes/Mark/{formatted_date}').strip()
    old_file_path = f"/sdcard/Notes/Mark/{formatted_date}/{png_name}"
    new_file_path = f"/sdcard/Notes/Mark/{formatted_date}/screenshot.jpg"
    run_command(f'adb -s {ip} shell mv {old_file_path} {new_file_path}')
    run_command(f'adb -s {ip} pull sdcard/Notes/Mark/{formatted_date}/screenshot.jpg {filepath}')


def check_hdmi_in_image(d,ip,project, logger):
    d.click(d.window_size()[0] * 0.5, d.window_size()[1] * 0.8)
    logger.info("开始检测图片")
    time.sleep(5)
    if project == "OEM副屏":
        take_screenshot_OEM(d,ip,os.path.join(current_working_dir,'image'), logger)
    else:
        take_screenshot(d, screenshot_path,logger)
    if match_image(f"{current_working_dir}/image/hdmi.jpg", screenshot_path,logger, threshold=0.8):
        logger.info("第一张图片检测通过")
        return True
    else:
        logger.info("第一张图片检测不通过")
        return False



def check_hdmi_in_audio(logger,record_time,rms_single_hdmi_in):
    logger.info("本地设备开始录音")
    local_record(record_time, test_wav_hdmi_in_path)
    time.sleep(10)
    rms_data_speaker = analysis_audio(test_wav_hdmi_in_path, logger)
    if rms_data_speaker < rms_single_hdmi_in:
        logger.info("HDMI IN 扬声器无声")
        return False
    if rms_data_speaker > rms_single_hdmi_in:
        logger.info("HDMI IN 扬声器正常")
        return True

def open_extend(d,logger):
    d.app_start("com.h3c.settings", "com.h3c.settings.main.ui.activity.SettingActivity")
    if d(text="声音与显示").exists(timeout=10):
        d(text="声音与显示").click()
    else:
        raise RuntimeError("未找到 '声音与显示' 选项")

        # 等待 "HDMI IN (Extend)" 出现并点击
    if d(text="HDMI IN (Extend)").exists(timeout=10):
        d(text="HDMI IN (Extend)").click()
        logger.info("已打开Extend口画面")
    else:
        raise RuntimeError("未找到 'HDMI IN (Extend)' 选项")
    logger.info("已打开Extend口画面")

def run_monkey(logger,ip):
    run_command(f"adb -s {ip} shell setprop persist.h3c.root_state 123@qwe")
    run_command(f"adb -s {ip} root")
    logger.info("开始运行monkey指令-launcher")
    run_command(f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 70 --pct-motion 30 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.launcher --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-录屏")
    run_command(f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 100 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.screencap --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-文件管理器")
    run_command(f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 100 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.filemanager --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-截屏")
    run_command(f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 70 --pct-motion 30 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.screenshot --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
    logger.info("开始运行monkey指令-批注")
    run_command(f"adb -s {ip} shell monkey  --pct-syskeys 0 --pct-touch 30 --pct-motion 70 --ignore-crashes --ignore-native-crashes --ignore-timeouts --ignore-security-exceptions -p com.h3c.commentary --throttle 1000 1000 -v -v -v 10000000 > {monkey_log_path}")
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
    run_command(f"adb -s {ip} push {kill_app_path} /data/local/tmp")

#获取已连接的wifi名称
def get_connected_wifi_name():

    result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "SSID" in line:
            wifi_name = line.split(":")[1].strip()
            return wifi_name
    return None

def open_hdmiin_oem(ip):
    run_command(f"adb -s {ip} shell am start com.cvte.tv.setting/com.cvte.tv.setting.TifPlayerActivity")

def close_hdmiin_oem(d):
    if d(resourceId="com.ifpdos.systembar:id/left_arrow_view").exists(timeout=2):
        d(resourceId="com.ifpdos.systembar:id/left_arrow_view").click()
    time.sleep(2)
    d.xpath(
        '//*[@resource-id="com.ifpdos.systembar:id/rcy_bar"]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').click()
    time.sleep(5)
    d.xpath(
        '//*[@resource-id="com.ifpdos.systembar:id/rcy_bar"]/android.widget.LinearLayout[4]').click()
    time.sleep(2)


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

def android_to_win(d,logger,device_ip):
    start_test(logger,device_ip)
    d.app_start("com.h3c.settings", "com.h3c.settings.main.ui.activity.SettingActivity")
    time.sleep(2)
    d.click(d.window_size()[0] / 2, d.window_size()[1] * 0.8)
    if d(text="切换系统").exists(timeout=5):
        d(text="切换系统").click()
    else:
        raise RuntimeError("未找到 '切换系统' 选项")

#win下检测hdmi音视频
def win_check_hdmi_in(logger,record_time,win_hdmi_record_path,rms_hdmi_win):
    check_image_tag = 0
    retry = 0
    while True:
        time.sleep(5)
        conn.sendall(b'2')  # 2表示开始检测hdmiin画面
        logger.info('已发送码2，进入检测hdmiin画面')
        response = conn.recv(1024)
        while check_image_tag == 0:
            if response.decode() == '20':
                logger.info('收到码20，hdmiin画面检测通过')
                check_image_tag = 1
            if response.decode() == '21':
                logger.info('收到码21')
                check_image_tag = 2
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break

        if check_image_tag == 2:
            return False
        if check_image_tag == 1:
            logger.info("开始录音")
            local_record(record_time, win_hdmi_record_path)
            logger.info("分析录音数据")
            rms = analysis_audio(win_hdmi_record_path, logger)
            if rms < rms_hdmi_win:
                logger.info("win-hdmiin检测扬声器无声")
                return False
            if rms > rms_hdmi_win:
                logger.info("win-hdmiin检测扬声器正常")
                conn.sendall(b'6')  # 2表示开始检测hdmiin画面
                logger.info("已发送码6，关闭hdmiin应用")
                return True

def win_check_speaker(logger,record_time,win_speaker_record_path,rms_speaker_win):
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

def check_win_public_disk(logger):
    check_public_disk_tag = 0
    retry = 0
    while True:
        conn.sendall(b'100')
        logger.info('已发送码a，进入检测win下公共分区')
        while check_public_disk_tag == 0:
            response = conn.recv(1024)
            if response.decode() == '101':
                logger.info("win-检测公共分区不通过")
                check_public_disk_tag = 2
            if response.decode() == '102':
                logger.info("win-检测公共分区通过")
                check_public_disk_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break

        if check_public_disk_tag == 1:
            return True
        if check_public_disk_tag == 2:
            return False


def check_win_camera(logger):
    check_camera_tag = 0
    retry = 0
    while True:
        conn.sendall(b'8')  # 3表示开始检测win下U盘
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


def win_to_android(logger):
    check_change_system_tag = 0
    retry = 0
    while True:
        conn.sendall(b'5')  # 3表示开始检测win下扬声器
        logger.info('已发送码5，进入切换系统')
        response = conn.recv(1024)
        while check_change_system_tag == 0:
            if response.decode() == '52':
                logger.info('已收到码52，大屏端开始切换系统')
                check_change_system_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break
        if check_change_system_tag == 1:
            return True

def win_restart(logger):
    check_win_restart_tag = 0
    retry = 0
    while True:
        conn.sendall(b'9')  # 3表示开始检测win下扬声器
        logger.info('已发送码9，准备重启win系统')
        response = conn.recv(1024)
        while check_win_restart_tag == 0:
            if response.decode() == '92':
                logger.info('已收到码92，大屏端开始重启')
                check_win_restart_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break
        if check_win_restart_tag == 1:
            return True

def win_shutdown(logger):
    check_win_shutdown_tag = 0
    retry = 0
    while True:
        conn.sendall(b'110')  # 3表示开始检测win下扬声器
        logger.info('已发送码b，准备win系统关机')
        response = conn.recv(1024)
        while check_win_shutdown_tag == 0:
            if response.decode() == '112':
                logger.info('已收到码112，大屏端开始关机')
                check_win_shutdown_tag = 1
            retry += 1
            time.sleep(2)
            if retry >= 20:
                logger.info('重试超过20次')
                break
        if check_win_shutdown_tag == 1:
            return True


def android_home_shutdown(d,logger,device_ip,project,power_ip):
    start_test(logger, device_ip)
    if project == "8kmega（单安卓或双系统切换）" or project == "医科通单屏模式" or project == "edpmega（单安卓或双系统切换）" or project == "医科通双屏模式":
        while not d(text="关机").exists(timeout=5):
            d(resourceId="com.h3c.launcher:id/iv_power").click()
            time.sleep(1)
        # 点击“关机”选项
        if d(text="关机").exists(timeout=5):
            d(text="关机").click()
        else:
            raise RuntimeError("未找到 '关机' 选项")
    if project == "嘿板":
        while not d(text="关机").exists(timeout=5):
            d(resourceId="com.h3c.launcher:id/iv_power_key").click()
            time.sleep(1)
        # 点击“关机”选项
        if d(text="关机").exists(timeout=5):
            d(text="关机").click()
        else:
            raise RuntimeError("未找到 '关机' 选项")
    if project == "OEM副屏":
        home_on(power_ip,logger)

def home_on(power_ip,logger):
    # 获取ADB设备列表
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接,devices信息如下：{devices}")

    # 获取ADB设备列表
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        raise RuntimeError(f"命令执行失败: 设备未连接,devices信息为{devices}")
    d = connect(power_ip)
    logger.info("按HOME键开机")
    if d(text="空闲").exists(timeout=5):
        d(text="空闲").click()
    time.sleep(10)
    if d(text="空闲").exists(timeout=5):
        d(text="空闲").click()



def on_start(test_project_type,test_type, stop_type_select,test_select, test_Config, root, logger):
    def check_pause_and_stop():
        while is_paused:
            time.sleep(0.1)  # 短暂睡眠，减少CPU使用
            root.after(0, update_button_text())
        # 在适当的位置添加检查 is_running 的代码
        if not is_running:
            update_button_states()  # 调用更新按钮状态的函数
            logger.info("已成功停止运行。")
            sys.exit()


    def control_devices(test_project_type,power_ip,logger,device_ip):
        global android_or_win
        if android_or_win == "android":
            d = connect(device_ip)
        if test_type == "重启":
            if android_or_win == "android":
                reboot_android(device_ip,logger,d,test_project_type)
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                time.sleep(test_interval)
            if android_or_win == "win":
                win_restart(logger)
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                time.sleep(10)
                return True


        if test_type == "息屏唤醒":
            start_test(logger,device_ip)
            if 'HDMI Record检测' in test_select:
                if test_project_type != "OEM副屏":
                    d.app_start("com.h3c.hdmi")
            time.sleep(5)
            close_screen_android(device_ip, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            time.sleep(test_interval)

        if test_type == "串口开关机":
            if serial_power(serial_port, logger) is False:
                update_button_states()  # 调用更新按钮状态的函数
                catch_logs(device_ip, logger,"serial_power_fail")
                sys.exit()
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            time.sleep(test_interval)

        if test_type == "双系统切换":
            if android_or_win == "android":
                android_to_win(d,logger,device_ip)
                android_or_win = "win"
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                time.sleep(10)
                return True
            if android_or_win == "win":
                win_to_android(logger)
                android_or_win = "android"
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                time.sleep(reboot_times)
                return True

        try:
            if test_type == "HOME键开关机":
                if android_or_win == "android":
                    android_home_shutdown(d,logger,device_ip,test_project_type,power_ip)
                    time.sleep(60)
                    home_on(power_ip, logger)
                    check_pause_and_stop()  # 检查是否有停止或暂停信号
                    time.sleep(test_interval)
                    return True
                if android_or_win == "win":
                    win_shutdown(logger)
                    time.sleep(150)
                    home_on(power_ip, logger)
                    check_pause_and_stop()  # 检查是否有停止或暂停信号
                    time.sleep(test_interval)
                    return True
        except Exception as power_e:
            logger.info(f"HOME键开关机失败,意外报错,继续下一轮,失败信息为{power_e}")
            reopen_power(power_process_name, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            comnon_to_home_on(power_ip,power_name)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            home_on(power_ip, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            time.sleep(test_interval)

        try:
            if test_type == "上下电":
                if android_or_win == "win":
                    conn.sendall(b'120')  # 120表示设置标志位
                    logger.info("已发送120码，windows端开始设置标志位")
                    time.sleep(200)
                switch_power(test_times_data, device_ip, power_ip, power_sn, power_path, reboot_times,
                             power_process_name, power_name, logger)
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                time.sleep(test_interval)

        except Exception as power_e:
            logger.info(f"上下电失败,意外报错,继续下一轮,失败信息为{power_e}")
            reopen_power(power_process_name, power_path, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            comnon_to_power(power_ip, power_sn, power_name)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            switch_power(test_times_data, device_ip, power_ip, power_sn, power_path, reboot_times,
                         power_process_name, power_name, logger)
            check_pause_and_stop()  # 检查是否有停止或暂停信号
            time.sleep(test_interval)



    try:
        rms_single_hdmi_in = int(test_Config['rms_hdmi_in'])  # 本地hdmiRecord的rms阈值---
    except:
        pass
    try:
        rms_single_hdmi_extend = int(test_Config['rms_hdmi_extend'])  # 本地hdmiRecord的rms阈值---
    except:
        pass
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
        wifi_password = test_Config['wifi_password']  # adb连接的插线板IP地址---
    except:
        pass



    try:
        power_sn = int(test_Config['power_sn'])  # 使用的插座序号---
    except:
        pass
    try:
        u_disk_name = test_Config['u_disk_name']  # U盘名称---
    except:
        pass
    try:
        power_path = test_Config['power_path']  # 模拟器打开路径---
    except:
        pass
    try:
        reboot_times = int(test_Config['reboot_times'])  # 运行多少次重启模拟器---
    except:
        pass
    try:
        power_process_name = test_Config['power_process_name']  # 模拟器进程名称---
    except:
        pass
    try:
        power_name = test_Config['power_name']  # 智能插座名称---
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
        black_check_times = int(test_Config['black_check_times'])  # 获取出现黑屏后是否要停止的选择项---
    except:
        pass

    try:
        serial_port = f"COM{int(test_Config['serial_port'])}"# 获取串口端口号---
    except:
        pass

    global is_running  # 使用 global 关键字
    global tester_project_type
    global tester
    global device_sn
    global test_count_var
    global test_fail_count_var
    global is_paused
    global android_or_win
    global run_tag
    is_running = True  # 确保每次开始时 is_running 为 True
    tester = test_Config['tester']  # 测试人员---
    device_sn = test_Config['device_sn']  # 设备序列号---
    tester_project_type = test_Config['tester_project_type']# 测试项目---
    if test_type == "双系统切换":
        android_or_win = test_Config['android_or_win']
    if test_project_type == "单win（非双系统切换）":
        android_or_win = 'win'
    test_times_data = 0
    test_fail_times_data = 0
    mic_check_tag = 0
    speaker_check_tag = 0
    if android_or_win == 'android' and test_select != ['黑屏检测']:
        run_command(f"adb connect {device_ip}")
        logger.info("已连接大屏ip")
        root_devices(device_ip)

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
                    time.sleep(20)
            logger.info(f'成功连接wifi:{connect_wifi_name}')
            if android_or_win == 'android' and test_select != ['黑屏检测']:
                run_command(f"adb -s {device_ip} shell am force-stop com.h3c.screencap")

            check_pause_and_stop()  # 检查是否有停止或暂停信号


            if android_or_win == "win":
                if test_select != ['黑屏检测']:
                    global conn
                    global response
                    host = '0.0.0.0'
                    port = 12345
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((host, port))
                    s.listen(1)
                    logger.info('等待客户端连接...')
                    conn, addr = s.accept()
                    logger.info(f'客户端 {addr} 已连接')
                    # 向客户端发送指令 111
                    conn.sendall(b'1')  # 1表示已接收到客户端的连接
                    logger.info('已发送连接码1,发送确认连接消息给客户端')
                    response = conn.recv(1024)
                    while response.decode() != "11":
                        logger.info("正在连接中")
                        time.sleep(2)
                    logger.info("连接成功")

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if android_or_win == "android":
                if '扬声器检测' in test_select or '麦克风检测' in test_select:
                    delete_file(f"{current_working_dir}/win_recorded_hdmi_in_audio.wav", logger)
                    delete_file(f"{current_working_dir}/win_speaker_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_speaker_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_hdmi_in_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_mic_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_mic_audio.mp4", logger)


            check_pause_and_stop()  # 检查是否有停止或暂停信号

            # 判断adb是否正常连接
            if android_or_win == "android":
                try:
                    if test_type == "重启" or test_type == "息屏唤醒" or test_type == "串口开关机" or test_type == "双系统切换":
                        if test_select != ['黑屏检测']:
                            check_and_reconnect_reboot(device_ip)
                except Exception as connect_e:
                    logger.info(f"设备连接失败,意外报错,继续下一轮,失败信息为{connect_e}")
                    check_and_reconnect_reboot_except(device_ip)
                    root_devices(device_ip)
                    continue

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            try:
                if test_type == "上下电":
                    check_and_reconnect(device_ip, power_ip, power_sn, power_path, power_process_name, power_name,logger,test_select)
            except Exception as connect_e:
                logger.info(f"设备连接失败,意外报错,继续下一轮,失败信息为{connect_e}")
                check_and_reconnect_except(device_ip, power_path, power_process_name, logger)
                root_devices(device_ip)
                continue
            check_pause_and_stop()  # 检查是否有停止或暂停信号

            try:
                if test_type == "HOME键开关机":
                    check_and_reconnect_home_on(device_ip, power_ip, power_path, power_process_name, logger,power_name,test_select)
            except Exception as connect_e:
                logger.info(f"设备连接失败,意外报错,继续下一轮,失败信息为{connect_e}")
                check_and_reconnect_except(device_ip, power_path, power_process_name, logger)
                root_devices(device_ip)
                continue

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if android_or_win == "android":
                d = connect(device_ip)
                if d(text = "取消").exists():
                    d(text="取消").click()

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '黑屏检测' in test_select:
                    # 检测黑屏
                    if check_black(model, device_ip, logger, camera_select, black_check_times) is False:
                        send_message(f"出现连续多次黑屏或者未检测到摄像头，停止", logger)

                        if stop_type_select == "是":
                            update_button_states()  # 调用更新按钮状态的函数
                            sys.exit()
                        else:
                            test_fail_times_data += 1
                            run_tag = 1


            check_pause_and_stop()  # 检查是否有停止或暂停信号
            if run_tag == 0:
                if 'HDMI Record检测' in test_select:
                    if android_or_win == "android":
                        # 检测hdmirecord
                        try:
                            if check_hdmi_in_image(d,device_ip,test_project_type, logger) is False:
                                send_message(f"HDMI Record检查画面不通过", logger)
                                catch_logs(device_ip, logger, "HDMI_Record_image_fail")
                                if stop_type_select == "是":
                                    update_button_states()  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1

                            check_pause_and_stop()  # 检查是否有停止或暂停信号

                            if check_hdmi_in_audio(logger,record_time,rms_single_hdmi_in) is False:
                                send_message(f"HDMI Record检查无声音", logger)
                                catch_logs(device_ip, logger,"HDMI_Record_audio_fail")
                                if stop_type_select == "是":
                                    update_button_states()  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1
                        except Exception as hdmi_record_e:
                            send_message(f"HDMI Record检测失败,失败信息为{hdmi_record_e}", logger)
                            print(hdmi_record_e)
                            catch_logs(device_ip, logger,"HDMI_Record_fail")
                            update_button_states()  # 调用更新按钮状态的函数
                            sys.exit()
                        finally:
                            delete_file(f"{current_working_dir}/win_recorded_hdmi_in_audio.wav", logger)
                            delete_file(f"{current_working_dir}/win_speaker_audio.wav", logger)
                            delete_file(f"{current_working_dir}/recorded_speaker_audio.wav", logger)
                            delete_file(f"{current_working_dir}/recorded_hdmi_in_audio.wav", logger)
                            delete_file(f"{current_working_dir}/recorded_mic_audio.wav", logger)
                            delete_file(f"{current_working_dir}/recorded_mic_audio.mp4", logger)
                    if android_or_win == "win":
                        if win_check_hdmi_in(logger,record_time,win_hdmi_record_path,rms_single_hdmi_in) is True:
                            logger.info("win下hdmiin检测通过")
                        else:
                            send_message(f"win下HDMI Record检查无声音", logger)
                            logger.info("win下hdmiin检测不通过")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if android_or_win == "android":
                if '扬声器检测' in test_select or '扬声器+monkey检测' in test_select:
                    time.sleep(5)
                    # 将音频文件复制至大屏
                    copy_to_android(device_ip, logger)
                    time.sleep(5)

                check_pause_and_stop()  # 检查是否有停止或暂停信号


                # 一键下课
                if "扬声器检测" in test_select or "麦克风检测" in test_select or "相机检测" in test_select or "U盘检测" in test_select:
                    start_test(logger, device_ip)


            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '扬声器检测' in test_select:
                    if android_or_win == "android":
                        # 扬声器检查
                        if check_speaker(rms_single_speaker, record_time, logger,device_ip,test_project_type,d) is False:
                            speaker_check_tag += 1
                            if speaker_check_tag > 1:
                                send_message(f"扬声器无声", logger)
                                catch_logs(device_ip, logger,"speaker_fail")
                                if stop_type_select == "是":
                                    update_button_states()  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1
                            else:
                                start_test(logger, device_ip)
                                if 'HDMI Record检测' in test_select:
                                    if test_project_type == "OEM副屏":
                                        open_hdmiin_oem(device_ip)
                                    else:
                                        d.app_start("com.h3c.hdmi")
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
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

                    check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '麦克风检测' in test_select:
                    if android_or_win == "android":
                        # 检查麦克风,不通过则停止运行
                        if check_mic(d, rms_single_mic, device_ip, logger,test_project_type) is False:
                            mic_check_tag += 1
                            if mic_check_tag > 1:
                                send_message(f"麦克风无声", logger)
                                catch_logs(device_ip, logger,"microphone_fail")
                                if stop_type_select == "是":
                                    update_button_states()  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1
                            else:
                                start_test(logger, device_ip)
                                if 'HDMI Record检测' in test_select:
                                    if test_project_type == "OEM副屏":
                                        open_hdmiin_oem(device_ip)
                                    else:
                                        d.app_start("com.h3c.hdmi")
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
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if android_or_win == "android":
                if '扬声器+monkey检测' in test_select or '麦克风检测+monkey检测' in test_select:
                    delete_file(f"{current_working_dir}/win_recorded_hdmi_in_audio.wav", logger)
                    delete_file(f"{current_working_dir}/win_speaker_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_speaker_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_hdmi_in_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_mic_audio.wav", logger)
                    delete_file(f"{current_working_dir}/recorded_mic_audio.mp4", logger)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if '扬声器+monkey检测' in test_select or '麦克风+monkey检测' in test_select:
                if '扬声器检测' in test_select or '麦克风检测' in test_select:
                    start_test(logger, device_ip)
                run_monkey(logger, device_ip)
                check_pause_and_stop()  # 检查是否有停止或暂停信号
                start_test(logger, device_ip)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '扬声器+monkey检测' in test_select:
                    # 扬声器检查
                    if check_speaker(rms_single_speaker, record_time, logger,device_ip,test_project_type,d) is False:
                        speaker_check_tag += 1
                        if speaker_check_tag > 1:
                            send_message(f"扬声器无声", logger)
                            catch_logs(device_ip, logger,"speaker_monkey_fail")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            start_test(logger, device_ip)
                            if 'HDMI Record检测' in test_select:
                                if test_project_type == "OEM副屏":
                                    open_hdmiin_oem(device_ip)
                                else:
                                    d.app_start("com.h3c.hdmi")
                            continue
                    else:
                        speaker_check_tag = 0

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '麦克风+monkey检测' in test_select:
                    # 检查麦克风,不通过则停止运行
                    if check_mic(d, rms_single_mic, device_ip, logger,test_project_type) is False:
                        mic_check_tag += 1
                        if mic_check_tag > 1:
                            send_message(f"麦克风无声", logger)
                            catch_logs(device_ip, logger,"microphone_monkey_fail")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        else:
                            start_test(logger,device_ip)
                            if 'HDMI Record检测' in test_select:
                                if test_project_type == "OEM副屏":
                                    open_hdmiin_oem(device_ip)
                                else:
                                    d.app_start("com.h3c.hdmi")
                            continue
                    else:
                        mic_check_tag = 0

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if '空白等待30分钟(配合音频检测)' in test_select:
                logger.info("开始等待30分钟")
                time.sleep(1800)
                logger.info("等待30分钟已完成")

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '相机检测' in test_select:
                    if android_or_win == "android":
                        # 检查相机，不通过则停止运行
                        if test_project_type =="医科通单屏模式" or test_project_type =="医科通双屏模式":
                            if check_camera_yiketong(d,test_project_type,logger, device_ip) is False:
                                logger.info("摄像头未正常加载")
                                send_message(f"摄像头未正常加载", logger)
                                catch_logs(device_ip, logger,"camera_fail")
                                if stop_type_select == "是":
                                    update_button_states()  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1
                            logger.info("摄像头正常加载")

                        else:
                            if check_camera(d,logger,device_ip,test_project_type) is False:
                                logger.info("摄像头未正常加载")
                                send_message(f"摄像头未正常加载", logger)
                                catch_logs(device_ip, logger,"camera_fail")
                                if stop_type_select == "是":
                                    update_button_states()  # 调用更新按钮状态的函数
                                    sys.exit()
                                else:
                                    test_fail_times_data += 1
                                    run_tag = 1
                            logger.info("摄像头正常加载")
                    if android_or_win == 'win':
                        if check_win_camera(logger) is True:
                            logger.info("相机正常加载")
                        else:
                            logger.info("相机未正常加载")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if 'U盘检测' in test_select:
                    if android_or_win == 'android':
                        # 检查U盘，不通过则停止运行
                        if check_udisk(logger,d, device_ip,u_disk_name,test_project_type) is False:
                            catch_logs(device_ip, logger,"u_disk_fail")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
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
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1


            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if '公共分区检查' in test_select:
                    if android_or_win == 'android':
                        # 检查U盘，不通过则停止运行
                        if check_anroid_public_disk(device_ip) is False:
                            catch_logs(device_ip, logger,"public_disk_fail")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                        logger.info("安卓公共分区正常加载")
                    if android_or_win == 'win':
                        if check_win_public_disk(logger) is True:
                            logger.info("win公共分区正常加载")
                        else:
                            logger.info("win公共分区未正常加载")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1


            check_pause_and_stop()  # 检查是否有停止或暂停信号

            if run_tag == 0:
                if 'HDMI Extend检测' in test_select:
                    # 检测hdmiExtend
                    try:
                        if test_type != "息屏唤醒":
                            try:
                                open_extend(d, logger)
                            except Exception as open_extend_error:
                                logger.info(open_extend_error)
                            check_pause_and_stop()  # 检查是否有停止或暂停信号
                        time.sleep(5)

                        if check_hdmi_in_audio(logger,record_time,rms_single_hdmi_extend) is False or check_hdmi_in_image(d,device_ip,test_project_type, logger) is False:
                            send_message(f"HDMI Extend检查无声音", logger)
                            catch_logs(device_ip, logger,"hdmi_extend_fail")
                            if stop_type_select == "是":
                                update_button_states()  # 调用更新按钮状态的函数
                                sys.exit()
                            else:
                                test_fail_times_data += 1
                                run_tag = 1
                    except Exception as hdmi_extend_e:
                        send_message(f"HDMI Extend检测失败,失败信息为{hdmi_extend_e}", logger)
                        catch_logs(device_ip, logger,"hdmi_extend_fail")
                        update_button_states()  # 调用更新按钮状态的函数
                        sys.exit()

            check_pause_and_stop()  # 检查是否有停止或暂停信号
            if run_tag == 0:
                logger.info(f"第{test_times_data + 1}次测试正常,{test_type}设备")
            else:
                logger.info(f"第{test_fail_times_data}次测试失败,{test_type}设备")
            control_devices(test_project_type,power_ip,logger,device_ip)

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            test_times_data += 1
            root.after(0, lambda: test_count_var.set(f"压测次数：{test_times_data}次"))
            root.after(0, lambda: test_fail_count_var.set(f"失败次数：{test_fail_times_data}次"))
        except Exception as e:
            logger.info(e)
            start_test(logger,device_ip)
            if 'HDMI Record检测' in test_select:
                if test_project_type == "OEM副屏":
                    open_hdmiin_oem(device_ip)
                else:
                    d.app_start("com.h3c.hdmi")
            continue
    # 确保无论测试循环如何结束，都会调用更新按钮状态的函数
    update_button_states()
    logger.info("程序已退出。")
    # send_message("程序已退出", logger)


def toggle_pause(logger):
    global is_paused
    global pause_button
    # 切换暂停状态
    is_paused = not is_paused
    update_button_pause_end()
    if is_paused:
        logger.info("已点击暂停按钮,程序暂停中,请等待")
    else:
        logger.info("已点击继续按钮,程序恢复运行")
if __name__ == '__main__':

    # 脚本名称或进程名称
    process_name = "AndroidAudioTest.exe"  # 如果打包成exe则填写exe文件名


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

    freeze_support()
    frame_main()
