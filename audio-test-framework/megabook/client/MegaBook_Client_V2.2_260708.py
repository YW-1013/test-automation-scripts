# -*- coding: utf-8 -*-

"""
2026-7-8 修改点：
1、新增"快速切换系统"函数 win_to_android_fast：配合服务端"快速切换"方式，收到新增码6后走 H3C SystemControl 的
   WebSocket IPC 直接下发切换命令(免 pyautogui 逐像素点击控制中心，原理同 switch_to_android.py)，回 ACK 码62。
   任一前置条件不满足(缺 websocket-client/服务未运行/端口不可连/连接失败/服务返回失败)时自动回退为原点击切换 win_to_android。
   注意：需 pip install websocket-client；IPC 端口默认候选 48372/27101，如本机不同可改 H3C_IPC_PORTS。

2026-6-24 修改点：
1、启动时检测管理员权限：非管理员运行时弹出UAC提权弹窗，以管理员身份重启自身(powercfg/任务计划/模拟键鼠等均需管理员权限)

2026-6-22 修改点：
1、修复双系统"休眠切换"模式下，客户端 win_to_android 死循环被休眠冻结后又恢复执行，导致系统从Win恢复后又被反复点击控制中心切回安卓、与服务端失配卡死的问题；增加休眠恢复检测：单轮点击耗时异常(>30秒)即判定本次切换任务已过期并停止点击

2026-6-10 修改点：
1、驱动检查改为通用模式，不再依赖预设设备列表，只检查是否存在异常状态码的设备
2、修改版本号为MegaBook_Client_V2.0_260610

2025-7-28 修改点：
1、增加报错信息详细解释，except中增加
2025-7-23 修改点：
1、把版本号等需要修改的地方都放在代码开头，防止后续遗漏
2、新增关闭当前设备的自动更新
3、新增设置无操作睡眠和息屏的时间
4、修改相机检测新方式
4、修改版本号为MegaBook_Client_V1.6_250723

2025-7-17:
1、修改win+x快捷键时，开启大写键盘
2、修改相机检测时同时检测前后相机及外接摄像头拍摄的画面

2025-7-10:
1、修改程序点不到控制中心，采用轮询坐标点击
2、修改检查设备管理器的驱动，只检查较重要的几项
3、修改版本号：MegaBook_Client_V1.5_250710
2025-7-8:
1、修改程序运行时就设置英文输入法
2025-4-23:
3、脚本名称及版本号修改为：win压测脚本-CLIENT端-V1.2（需以管理员权限启动）
2025-1-3:
1、增加界面
2、新增开机自启动
3、脚本名称及版本号修改为：win压测脚本-CLIENT端-V1.1（需以管理员权限启动）
2024-10-31:新增检查项，检测是否出现两分钟后重启的现象
"""

import socket
import time
import pyaudio
import wave
import os
import shutil
import logging
from logging import handlers
import numpy as np
import sys
import subprocess
import pywifi
from pywifi import const
import pyautogui
import win32com.client
from PIL import Image
import wmi
from pygrabber.dshow_graph import FilterGraph
import tkinter as tk
from tkinter import ttk
from tkinter import font
import tkinter.messagebox as tkMessageBox
import threading
from datetime import datetime, timedelta
import json
from multiprocessing import freeze_support
import pygetwindow as gw
import psutil
import ctypes
import winreg
import traceback

def get_path():
    try:
        base_path = sys._MEIPASS  # pyinstaller打包后的路径
    except AttributeError:
        base_path = os.path.abspath(".")  # 当前工作目录的路径

    return base_path  # 返回实际路径
current_working_dir = get_path()
file_path = os.path.dirname(os.path.realpath(sys.argv[0]))
#名称修改处
exe_path = os.path.join(file_path,'MegaBook_Client_V2.2_260708.exe')
root_title = 'MMegaBook_Client_V2.2_260708（需以管理员权限启动）'

log_path = os.path.join(file_path, 'logs')
test_wav_path = os.path.join(current_working_dir, 'test.wav')
test_wav_Save_path = os.path.join(file_path, 'recorded_audio.wav')
screen_tools = os.path.join(current_working_dir,'PowerTool.exe')
is_running = True

global test_items_checkbuttons
test_items_checkbuttons = {}
global task_name
task_name = 'win_client_task_megabook'

STATUS_CODES = {
            0: "正常",
            1: "配置错误",
            2: "未分配资源",
            3: "筛选器驱动加载失败",
            4: "驱动加载失败",
            5: "注册表损坏",
            6: "需要重启",
            7: "部分配置失败",
            8: "未签名驱动",
            9: "未知设备",
            10: "需要重新启动",
            11: "配置冲突",
            12: "需要进一步配置",
            13: "硬件不存在",
            14: "驱动加载失败",
            15: "启动失败",
            16: "已禁用",
            17: "系统故障",
            18: "未找到驱动",
            19: "被策略禁用",
            20: "设备不存在",
            21: "需要重新扫描",
            22: "驱动程序未安装",
            23: "需要验证配置",
            24: "需要重新安装驱动",
            25: "部分配置信息丢失",
            26: "需要驱动程序安装",
            27: "未知配置问题",
            28: "设备被阻止",
            29: "遗留设备",
            30: "驱动兼容性问题",
            31: "需要用户干预"
        }



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
    # 创建一个日志器。提供了应用程序接口
    logger = logging.getLogger(log_prefix)
    # 设置日志输出的最低等级,低于当前等级则会被忽略
    logger.setLevel(level)
    # 创建日志输出路径
    dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
    log_path = os.path.join(dirname, "logs")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # 创建处理器：ch为控制台处理器，fh为按日期切换的文件处理器
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # 输出到文件：每天自动切换为 audio_test_MM-DD.log，跨天后自动新建
    fh = DailyDateFileHandler(log_path, log_prefix, encoding='utf-8')
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
        'host_ip': '192.168.1.100',
        'connect_wifi_name':'无',
        'wifi_password':"无",
        'connect_timeout':'60',
        'rms_mic': '100000000000',
        'time_set_sleep':'300',
        'time_set_screen': '300',
        'record_time': '13',
        'u_disk_name':'',
        'camera_name': '',
        'boot_delay': '30',
        'sim_check': '0.8',
        'light_threshold': '10',
        'bt_name': '',
        'auto_start_type': '是',
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

# 更新配置项的显示状态
def update_config_visibility():
    # 确保使用全局变量
    global type_var
    global auto_start_var
    global test_items_vars
    global config_labels
    global config_entries
    global config_items


    if not test_items_vars['相机检测'].get():
        config_labels['sim_check'].grid_remove()
        config_entries['sim_check'].grid_remove()
    else:
        config_labels['sim_check'].grid()
        config_entries['sim_check'].grid()


    if not test_items_vars['麦克风检测'].get():
        config_labels['rms_mic'].grid_remove()
        config_entries['rms_mic'].grid_remove()
        config_labels['record_time'].grid_remove()
        config_entries['record_time'].grid_remove()
    else:
        config_labels['rms_mic'].grid()
        config_entries['rms_mic'].grid()
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

    if not test_items_vars['相机检测'].get():
        config_labels['camera_name'].grid_remove()
        config_entries['camera_name'].grid_remove()
    else:
        config_labels['camera_name'].grid()
        config_entries['camera_name'].grid()


def frame_main():
    # 确保使用全局变量
    global stop_var
    global type_var
    global test_items_vars
    global config_labels
    global config_entries
    global config_items
    global start_button
    global stop_button
    global pause_button
    global log_text
    global method_combobox
    global stop_combobox
    global auto_start_var


    # 创建主窗口
    root = tk.Tk()
    root.title(root_title)

    def on_closing():
        logging.shutdown()  # 清理日志系统
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

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
    type_combobox['values'] = ('megabook')
    type_combobox.pack(side=tk.TOP, fill=tk.X)
    type_var.set("megabook")

    # 第二项 - 选择是否创建开机自启动任务
    auto_start_label = ttk.Label(left_frame, text="开启自启动", font=bold_font)
    auto_start_label.pack(side=tk.TOP, anchor=tk.W,pady=(10, 0))

    auto_start_var = tk.StringVar()
    auto_start_combobox = ttk.Combobox(left_frame, textvariable=auto_start_var, state='readonly')
    auto_start_combobox['values'] = ('是', '否')
    auto_start_combobox.pack(side=tk.TOP, fill=tk.X)
    auto_start_var.set("是")

    # 第四项 - 选择测试项
    test_items_label = ttk.Label(left_frame, text="选择测试项", font=bold_font)
    test_items_label.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))

    # 填充测试项到列表框中，并默认全选这些项
    test_items = ['麦克风检测', '相机检测', 'U盘检测', '蓝牙检测']

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
        ('host_ip', '笔记本IP'),
        ('connect_wifi_name', '连接的wifi名称(不连wifi填无)'),
        ('wifi_password', 'wifi密码（无密码填无）'),
        ('connect_timeout', '连接超时'),
        ('rms_mic', '麦克风阈值'),
        ('time_set_screen', '无操作息屏时间（单位分钟，从不填0）'),
        ('time_set_sleep', '无操作睡眠时间（单位分钟，从不填0）'),
        ('record_time', '录音时长'),
        ('u_disk_name', 'U盘名称(多个以英文,分隔)'),
        ('camera_name', '相机名称'),
        ('boot_delay', '程序启动延时'),
        ('sim_check', '相似度阈值(0~1)'),
        ('light_threshold', '光感阈值(低于此值判失败,单位lux)'),
        ('bt_name', '蓝牙名称(多个以英文,分隔)'),
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
    config_path = os.path.join(file_path, 'config_client_megabook.json')
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
        if key == 'auto_start_type':
            auto_start_var.set(value)  # 设置停止方式
        elif key == 'selected_test_items':
            for item, selected in value.items():
                test_items_vars[item].set(selected)  # 设置测试项
        else:
            clean_key = key.strip()
            if clean_key in config_vars:
                config_vars[clean_key].set(value)

    # 初始化界面
    update_config_visibility()
    # 配置右侧Frame的列，使输入框可以随窗口大小调整
    right_frame.columnconfigure(1, weight=1)

    # 如果有更多的配置项需要垂直滚动，可以考虑添加一个滚动条

    # 设置权重，确保右侧配置部分的输入框随窗口伸缩
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


    # 创建删除开机自启动按钮
    open_logs = ttk.Button(bottom_frame, text="生成相机对比图", command=lambda: template_image(logger))
    open_logs.pack(side=tk.LEFT, expand=True)


    # 创建删除开机自启动按钮
    open_logs = ttk.Button(bottom_frame, text="恢复系统更新", command=lambda: resume_windows_updates(logger))
    open_logs.pack(side=tk.LEFT, expand=True)

    # 创建删除开机自启动按钮
    open_logs = ttk.Button(bottom_frame, text="禁用开机自启动", command=lambda: delete_task(logger))
    open_logs.pack(side=tk.LEFT, expand=True)

    # 创建开始按钮
    start_button = ttk.Button(bottom_frame, text="开始",
                              command=lambda: on_start_button_clicked(config_vars, logger))
    start_button.pack(side=tk.LEFT, expand=True)

    # 创建结束按钮
    stop_button = ttk.Button(bottom_frame, text="结束", command=lambda: on_stop_button_clicked(logger),state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, expand=True)

    # 创建打开日志文件夹按钮
    open_logs = ttk.Button(bottom_frame, text="打开日志文件夹", command=on_open_log_folder_clicked)
    open_logs.pack(side=tk.LEFT, expand=True)

    # 设置主窗口的最小大小
    root.minsize(600, 400)

    # 设置main_frame的网格权重，确保它可以扩展到整个窗口
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    root.after(0, lambda: on_start_button_clicked(config_vars, logger))

    # 开始主循环
    root.mainloop()

# 在on_start_test函数中添加一个helper函数来更新按钮状态
def update_button_states(logger):
    resume_windows_updates(logger)
    time.sleep(5)
    start_button['state'] = tk.NORMAL  # 启用开始按钮
    stop_button['state'] = tk.DISABLED  # 禁用结束按钮


def create_task_xml(executable_path, working_directory, logger,script_args=None, delay_seconds=30):
    TASK_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-16"?>
    <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <Triggers>
        <LogonTrigger>
          <Enabled>true</Enabled>
          <Delay>PT{delay_seconds}S</Delay>
        </LogonTrigger>
      </Triggers>
      <Principals>
        <Principal id="Author">
          <UserId>{user_id}</UserId>
          <LogonType>InteractiveToken</LogonType>
          <RunLevel>HighestAvailable</RunLevel>
        </Principal>
      </Principals>
      <Settings>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
        <StartWhenAvailable>true</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
        <IdleSettings>
          <StopOnIdleEnd>false</StopOnIdleEnd>
          <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <RunOnlyIfIdle>false</RunOnlyIfIdle>
        <WakeToRun>false</WakeToRun>
        <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
        <Priority>7</Priority>
        <AllowHardTerminate>false</AllowHardTerminate>
      </Settings>
      <Actions Context="Author">
        <Exec>
          <Command>{command}</Command>
          <Arguments>{arguments}</Arguments>
          <WorkingDirectory>{working_directory}</WorkingDirectory>
        </Exec>
      </Actions>
    </Task>"""

    try:
        # 获取当前登录用户名称
        user_name = os.getlogin()

        # 生成任务XML
        task_xml = TASK_XML_TEMPLATE.format(
            delay_seconds=delay_seconds,
            command=executable_path,
            arguments=script_args if script_args else "",
            working_directory=working_directory,
            user_id=user_name
        )


        # 通过任务计划程序注册任务
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        task_definition = scheduler.NewTask(0)
        task_definition.XmlText = task_xml

        # 使用当前登录用户的凭证
        root_folder.RegisterTaskDefinition(
            task_name,
            task_definition,
            6,  # 6 表示，如果任务已存在则更新
            user_name,
            None,
            3  # 3 表示使用当前登录用户的凭证
        )
        logger.info(f'{task_name}任务成功创建')

    except Exception as e:
        print(f"任务创建失败，失败原因为： {e}")


def delete_task(logger):

    try:
        # Connect to the Task Scheduler service
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()

        # Get the root folder
        root_folder = scheduler.GetFolder('\\')

        # Check if the task exists
        task_exists = False
        try:
            root_folder.GetTask(task_name)
            task_exists = True
        except Exception:
            task_exists = False

        if not task_exists:
            logger.info(f'{task_name}任务不存在')
            return

        # Delete the task
        root_folder.DeleteTask(task_name, 0)
        logger.info(f'{task_name}任务不再自动执行')

    except Exception as e:
        logger.info(f"删除任务失败，原因为: {e}")


def on_start_button_clicked(config_vars, logger):
    # 重置全局变量
    global is_running
    is_running = True
    log_text.configure(state="normal")
    log_text.delete("1.0",tk.END)
    log_text.configure(state="disabled")

    # 获取所有配置项的值
    configs_to_save = {k: v.get() for k, v in config_vars.items()}


    # 获取并保存停止方式
    configs_to_save['auto_start_type'] = auto_start_var.get()

    # 获取并保存选中的测试项
    configs_to_save['selected_test_items'] = {item: var.get() for item, var in test_items_vars.items()}
    # 保存到配置文件
    save_config(configs_to_save, 'config_client_megabook.json')

    # 获取停止方式
    selected_test_items = {item: var.get() for item, var in test_items_vars.items()}

    # 获取测试项目
    auto_start_type = auto_start_var.get()

    # 获取测试配置
    test_Config = {key: var.get() for key, var in config_vars.items()}
    missing_configs = [key for key, value in test_Config.items() if
                       value == '' and config_entries[key].winfo_viewable()]
    if missing_configs:
        # 弹出提示框，告知用户哪些配置项未填写
        missing_configs_str = ", ".join(missing_configs)
        tk.messagebox.showerror("错误", f"以下测试配置项未填写，请填写后再开始测试：{missing_configs_str}")
        return  # 退出函数，不开始测试

    # 启动线程来执行on_start函数
    test_thread = threading.Thread(target=on_start_test,
                                   args=(selected_test_items, auto_start_type,test_Config, logger))
    test_thread.start()
    start_button['state'] = tk.DISABLED  # 禁用开始按钮
    stop_button['state'] = tk.NORMAL  # 启用结束按钮


def on_start_test(selected_test_items,auto_start_type ,test_Config, logger):
    # 这里是处理测试开始逻辑的地方
    # 你可以使用selected_method, selected_test_items, test_Config变量
    test_items = selected_test_items
    on_start(test_items, auto_start_type,test_Config, logger)


# 定义按钮点击事件的处理函数
def on_open_log_folder_clicked():
    os.startfile(log_path)

#判断键盘大写键是否按下
def is_caps_lock_on():
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL) & 0xffff != 0


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
        print(f"获取WiFi名称出错: {e}")
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


#驱动检查
def get_all_devices():
    """获取所有设备及其状态码"""
    c = wmi.WMI()
    devices = {}

    # 获取正常设备
    for item in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
        if item.Description:
            devices[item.Description] = 0

    # 获取异常设备
    for error_code in STATUS_CODES:
        if error_code == 0: continue
        for item in c.Win32_PnPEntity(ConfigManagerErrorCode=error_code):
            if item.Description:
                devices[item.Description] = error_code
    return devices


def check_abnormal_devices():
    """检查并返回所有存在异常状态码的设备列表（通用，不依赖特定设备名称）"""
    all_devices = get_all_devices()
    abnormal = []
    for desc, status_code in all_devices.items():
        if status_code != 0:
            reason = STATUS_CODES.get(status_code, "未知状态码")
            abnormal.append((desc, "异常", reason))
    return abnormal

def check_all_driver(logger):
    # 获取所有存在异常状态码的设备，不依赖预设设备列表
    abnormal_devices = check_abnormal_devices()

    if abnormal_devices:
        log_content = f"设备异常 {len(abnormal_devices)} 个\n"
        log_content += "\n".join(
            [f"异常设备名称：{d[0]}；异常原因：{d[2]}"
             for d in abnormal_devices]
        )
        logger.info(log_content)
        return False
    else:
        logger.info("所有设备状态正常")
        return True


#win+x操作，模拟人为操作
def winx_operation(logger,operation):
    try:
        if is_caps_lock_on() is False:
            pyautogui.press('CapsLock')
        logger.info('已开启大写')
        time.sleep(3)
        # 触发 Win+X 组合键
        pyautogui.keyDown('win')
        pyautogui.press('x')
        pyautogui.keyUp('win')
        time.sleep(1)  # 等待菜单弹出

        # 按下 U 键展开电源菜单
        pyautogui.press('U')
        time.sleep(1)  # 等待子菜单展开

        # 按下 S 键选择睡眠
        pyautogui.press(operation)

    except Exception as e:
        logger.info(f"操作失败: {e}")



# ================== 快速切换系统(H3C SystemControl IPC，免点击控制中心) ==================
# 原理与同目录 switch_to_android.py 完全一致：不再用 pyautogui 逐像素点击控制中心，
# 而是复用 H3C 应用控制中心的 WebSocket IPC，直接给 SystemControlService 下发
# "SwitchSystemToAndroid" 事件触发切换(与UI按钮同一条链路)。成功后系统重启进入安卓。
# 依赖：pip install websocket-client
H3C_WS_PATH = "H3C_APPS_Channel"
# 本机 ServiceHost 监听的 IPC 端口候选(不同机器/版本可能不同：这台样机实测48372，反编译源码默认27101)
H3C_IPC_PORTS = (48372, 27101)
H3C_APP_CLIENT_NAME = "SystemControl"           # 本客户端登记名
H3C_SERVICE_CLIENT_NAME = "SystemControlService"  # 目标：执行切换的服务
H3C_T_APPLY_CLIENT_CONNECTING = 0
H3C_T_CLIENT_COMMUNICATION = 6
H3C_EVENT_SWITCH_TO_ANDROID = "SwitchSystemToAndroid"
H3C_EVENT_SWITCH_RESULT = "SystemSwitchResult"
H3C_SWITCH_TIMEOUT = 5.0                          # 源码：等待5000ms
H3C_RESULT_MEANING = {0: "失败(response data 0)", -1: "失败：无安卓启动项"}


def _h3c_server_frame(msg_type, inner):
    """ChannelServerMessage: {"Type":int,"MessageData":"<inner json字符串>"}(双重编码)"""
    return json.dumps({"Type": msg_type, "MessageData": json.dumps(inner, ensure_ascii=False)},
                      ensure_ascii=False)


def _h3c_connect_frame():
    return _h3c_server_frame(H3C_T_APPLY_CLIENT_CONNECTING, {"Client": H3C_APP_CLIENT_NAME, "Message": None})


def _h3c_switch_frame():
    import uuid
    inner = {
        "TargetClient": H3C_SERVICE_CLIENT_NAME,
        "SourceClient": H3C_APP_CLIENT_NAME,
        "Data": "",
        "Event": {
            "EventName": H3C_EVENT_SWITCH_TO_ANDROID,
            "EventId": str(uuid.uuid4()),
            "NeedCallBack": True,
            "IsCallBack": False,
            "BackingResponse": None,
        },
        "Message": None,
    }
    return _h3c_server_frame(H3C_T_CLIENT_COMMUNICATION, inner)


def _h3c_parse_incoming(raw):
    """解析服务端帧；若为 SystemSwitchResult 返回 int 结果，否则 None。"""
    try:
        outer = json.loads(raw)
        inner = json.loads(outer.get("MessageData") or "{}")
    except Exception:
        return None
    if (inner.get("Event") or {}).get("EventName") != H3C_EVENT_SWITCH_RESULT:
        return None
    try:
        return int(str(inner.get("Data")).strip())
    except Exception:
        return None


def _h3c_port_open(port, timeout=2.0):
    """依次探测 IPv6/IPv4 回环该端口是否可连接(服务端可能仅监听IPv6回环)。"""
    for fam, host in ((socket.AF_INET6, "::1"), (socket.AF_INET, "127.0.0.1")):
        try:
            with socket.socket(fam, socket.SOCK_STREAM) as sk:
                sk.settimeout(timeout)
                if sk.connect_ex((host, port)) == 0:
                    return True
        except OSError:
            continue
    return False


def _h3c_service_running(name="SystemControlService"):
    try:
        out = subprocess.run(["sc", "query", name], capture_output=True, text=True, timeout=10,
                             creationflags=subprocess.CREATE_NO_WINDOW).stdout
        return "RUNNING" in out.upper()
    except Exception:
        return False


def win_to_android_fast(logger):
    """快速切换系统：通过 H3C SystemControl 的 WebSocket IPC 直接下发切换命令，
    免去 pyautogui 逐像素点击控制中心。成功后系统会重启进入安卓。
    任一前置条件不满足(缺依赖/服务未运行/端口不可连/连接失败/服务明确返回失败)时，
    自动回退为原来的点击切换 win_to_android，保证压测不中断。"""
    try:
        from websocket import create_connection
    except ImportError:
        logger.info("[快速切换] 缺少依赖 websocket-client(pip install websocket-client)，本轮回退为点击切换")
        win_to_android(logger)
        return False

    if not _h3c_service_running():
        logger.info("[快速切换] 未检测到 SystemControlService 运行，回退为点击切换")
        win_to_android(logger)
        return False

    port = next((p for p in H3C_IPC_PORTS if _h3c_port_open(p)), None)
    if port is None:
        logger.info(f"[快速切换] IPC端口{H3C_IPC_PORTS}均不可连接，回退为点击切换")
        win_to_android(logger)
        return False

    ws = None
    for host in ("localhost", "[::1]", "127.0.0.1"):
        try:
            ws = create_connection(f"ws://{host}:{port}/{H3C_WS_PATH}", timeout=H3C_SWITCH_TIMEOUT + 2)
            logger.info(f"[快速切换] 已连接 ws://{host}:{port}/{H3C_WS_PATH}")
            break
        except Exception:
            ws = None
    if ws is None:
        logger.info("[快速切换] WebSocket 连接失败，回退为点击切换")
        win_to_android(logger)
        return False

    try:
        ws.send(_h3c_connect_frame())          # 1) 登记本客户端名 SystemControl
        time.sleep(0.2)
        ws.send(_h3c_switch_frame())           # 2) 下发 SwitchSystemToAndroid
        logger.info(f"[快速切换] 已下发 {H3C_EVENT_SWITCH_TO_ANDROID}，等待结果(≤{int(H3C_SWITCH_TIMEOUT)}s)…")
        deadline = time.time() + H3C_SWITCH_TIMEOUT
        while time.time() < deadline:
            ws.settimeout(max(0.2, deadline - time.time()))
            try:
                raw = ws.recv()
            except Exception:
                break
            if not raw:
                continue
            res = _h3c_parse_incoming(raw if isinstance(raw, str) else raw.decode("utf-8", "ignore"))
            if res is None:
                continue
            if res in H3C_RESULT_MEANING:
                logger.info(f"[快速切换] 失败：{H3C_RESULT_MEANING[res]}，回退为点击切换")
                win_to_android(logger)
                return False
            logger.info(f"[快速切换] 服务已受理(result={res})，系统即将重启进入安卓")
            return True
        # 已发出切换命令但5s内没收到结果：服务可能已开始切换/重启，视为已受理，不再回退点击(避免重复切换)
        logger.info("[快速切换] 5s内未收到结果(服务可能已开始切换/重启)，视为已受理")
        return True
    finally:
        try:
            ws.close()
        except Exception:
            pass


def win_to_android(logger):
    pyautogui.FAILSAFE = False
    x = 2440
    times = 1
    while True:
        iter_start = time.time()
        logger.info(f"第{times}次尝试切换系统")
        resumed = False
        # 逐步点击控制中心切换到安卓；每步后检测本轮累计耗时
        for click_x, click_y, wait in [(x, 1750, 1), (2597, 1530, 1), (1546, 1010, 2)]:
            pyautogui.click(click_x, click_y)
            time.sleep(wait)
            # 休眠恢复检测：正常一轮约4秒，若本轮某步后累计耗时远超(>30秒)，
            # 说明进程曾被休眠冻结——即系统已切到安卓后又切回Win，本次切换任务已过期。
            # 必须立即停止，否则恢复后会继续点击控制中心，又把系统切回安卓，
            # 导致与服务端(此时认为已在Win)失配、压测卡死。
            if time.time() - iter_start > 30:
                resumed = True
                break
        if resumed:
            logger.info("检测到休眠冻结后恢复，本次切换任务已过期，停止点击控制中心")
            break
        x -= 30
        times += 1
        if x < 2280:
            x = 2440

def compare_images(img1, img2):
    # 打开图片并转化为numpy数组
    i1 = np.array(Image.open(img1))
    i2 = np.array(Image.open(img2))

    # 计算两张图片的差异
    difference = np.sum((i1 - i2) ** 2)

    # 计算相似度
    similarity = 100 - (difference / float(i1.size))

    return similarity


# 获取当前设备上的USB存储设备，磁盘类的U盘无法识别
def get_current_usb_names(logger):
    c = wmi.WMI()
    usb_names = []
    for disk in c.Win32_LogicalDisk(DriveType=2):
        usb_names.append(disk.VolumeName)
    logger.info('U盘列表如下')
    logger.info(usb_names)
    return usb_names

def compare_usb_names(config_usb_names, current_usb_names,logger):
    missing_usb_names = [usb for usb in config_usb_names if usb not in current_usb_names]
    if missing_usb_names:
        logger.info(f'缺少U盘: {missing_usb_names}')
        return False
    else:
        logger.info('所有U盘都检测到了')
        return True

#获取当前设备上的相机列表
def get_camera_list(logger):
    camera_list = []
    graph = FilterGraph()
    camera_name_lists = graph.get_input_devices()
    for camera_name in camera_name_lists:
        camera_list.append(camera_name)
    logger.info('相机列表如下')
    logger.info(camera_list)
    return camera_list

def compare_camera_names(config_camera_names, current_camera_names,logger):
    missing_camera_names = [usb for usb in config_camera_names if usb not in current_camera_names]
    if missing_camera_names:
        logger.info(f'缺少相机: {missing_camera_names}')
        return False
    else:
        logger.info('所有相机都检测到了')
        return True


def clean_old_mei_directories(logger, exclude_dir=None):
    temp_dir = os.environ.get("TEMP")
    mei_dirs = []

    # 手动实现 "_MEI*" 目录匹配
    for entry in os.listdir(temp_dir):
        entry_path = os.path.join(temp_dir, entry)
        if entry.startswith("_MEI") and os.path.isdir(entry_path):
            mei_dirs.append(entry_path)

    current_time = time.time()

    for dir_path in mei_dirs:
        if dir_path == exclude_dir:
            continue

        dir_time = os.path.getmtime(dir_path)
        if current_time - dir_time <= 3600:
            continue

        try:
            for root, dirs, files in os.walk(dir_path, topdown=False):
                # 删除文件
                for file in files:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, 0o666)
                    os.remove(file_path)
                    logger.debug(f"Deleted file: {file_path}")
                # 删除子目录
                for dir_name in dirs:
                    sub_dir = os.path.join(root, dir_name)
                    os.rmdir(sub_dir)
                    logger.debug(f"Deleted dir: {sub_dir}")
            # 删除最外层目录
            os.rmdir(dir_path)
            logger.info(f"成功删除目录: {dir_path}")
        except Exception as e:
            logger.error(f"删除 {dir_path} 报错: {str(e)}")


def template_image(logger):
    if not os.path.exists(os.path.join(file_path,'megabook_image')):
        os.makedirs(os.path.join(file_path,'megabook_image'))

    subprocess.Popen('start microsoft.windows.camera:', shell=True)
    time.sleep(5)  # 等待应用启动
    for i in range(len(get_camera_list(logger))):
        pyautogui.click(2788, 110)
        time.sleep(5)
        im = pyautogui.screenshot()
        # 保存图片
        im.save(os.path.join(os.path.join(file_path,'megabook_image'), f"template_captured_{i}.jpg"))
        time.sleep(5)
    pyautogui.hotkey('alt', 'f4')


def check_megabook_camera(sim_check,camera_config_list,logger):
    retry_times = 0
    camera_status = False
    while True:
        similarity_image_path_name = datetime.now().strftime("%Y%m%d%H%M%S")
        logger.info(similarity_image_path_name)
        camera_path_name = f"camera_{similarity_image_path_name}"
        logger.info(camera_path_name)
        camera_path_name_full = os.path.join(os.path.join(file_path,'megabook_image'),
                                                  camera_path_name)
        logger.info(camera_path_name_full)
        os.makedirs(camera_path_name_full)
        time.sleep(5)
        if camera_status is False:
            status_list = []
            subprocess.Popen('start microsoft.windows.camera:', shell=True)
            time.sleep(5)  # 等待应用启动
            for i in range(len(camera_config_list)):
                pyautogui.click(2788, 110)
                time.sleep(5)
                im = pyautogui.screenshot()
                # 保存图片
                im.save(os.path.join(os.path.join(camera_path_name_full, f"captured_{i}.jpg")))
                time.sleep(5)
            pyautogui.hotkey('alt', 'f4')
            for sim_i in range(len(camera_config_list)):
                captured_path = os.path.join(camera_path_name_full, f"captured_{sim_i}.jpg")
                check_tag_partial = False
                for sim_j in range(len(camera_config_list)):
                    template_path = os.path.join(file_path, 'megabook_image', f"template_captured_{sim_j}.jpg")
                    similarity = compare_images(captured_path, template_path)
                    logger.info(f"{camera_config_list[sim_i]}与template_captured_{sim_j}相似度为{similarity}%")
                    if similarity >= sim_check*100:
                        check_tag_partial = True
                status_list.append(check_tag_partial)
            camera_status = all(status_list)
            time.sleep(5)
            retry_times += 1
            if retry_times > 20:
                return camera_status
        else:
            shutil.rmtree(camera_path_name_full)  # 清除整个目录
            logger.info(camera_path_name_full)
            logger.info("删除截图文件夹成功")
            return camera_status


def check_light_sensor(logger, threshold=None):
    """通过 PowerShell WinRT 读取环境光传感器数值，返回 (ok: bool, lux: float|None)。
    传感器不存在、无法读取或输出无法解析均视为失败。
    若传入 threshold 且读数低于该阈值(lux)，同样判定为失败。"""
    ps = (
        '[Windows.Devices.Sensors.LightSensor,'
        'Windows.Devices.Sensors,ContentType=WindowsRuntime] | Out-Null; '
        '$s = [Windows.Devices.Sensors.LightSensor]::GetDefault(); '
        'if ($s) { $r = $s.GetCurrentReading(); '
        'if ($r) { $r.IlluminanceInLux } else { "NO_READING" } } '
        'else { "NO_SENSOR" }'
    )
    try:
        result = subprocess.run(
            ['powershell', '-NonInteractive', '-Command', ps],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        out = result.stdout.strip()
        if not out or out == 'NO_SENSOR':
            logger.info('[光感] 未找到传感器（NO_SENSOR 或无输出）')
            return False, None
        if out == 'NO_READING':
            logger.info('[光感] 传感器存在但 GetCurrentReading() 返回 null')
            return False, None
        try:
            lux = float(out)
            logger.info(f'[光感] 读数：{lux:.2f} lux')
            if threshold is not None and lux < threshold:
                logger.info(f'[光感] 读数 {lux:.2f} lux 低于阈值 {threshold:.2f} lux，判定为失败')
                return False, lux
            return True, lux
        except ValueError:
            logger.warning(f'[光感] 返回值无法解析：{out!r}')
            return False, None
    except Exception as e:
        logger.info(f'[光感] 检测异常：{e}')
        return False, None


def check_bluetooth(bt_names_str, logger):
    """Windows侧蓝牙检测，两道检测：
      ①蓝牙开关(无线电)是否打开 —— 用 WinRT Radio API 读取蓝牙无线电状态；
      ②打开后再查指定蓝牙设备是否已连接 —— 用 Get-PnpDevice 按 BTHENUM/BTHHFENUM/BTHLE
        枚举，FriendlyName 与设备管理器一致，状态为 OK 视为已连接。
    bt_names_str 为英文逗号分隔的设备名；为空则只校验开关。整体通过返回 True。"""
    # ① 蓝牙开关（无线电状态）
    radio_ps = (
        "$ErrorActionPreference='Stop';"
        "Add-Type -AssemblyName System.Runtime.WindowsRuntime | Out-Null;"
        "$asTaskGeneric=([System.WindowsRuntimeSystemExtensions].GetMethods()|"
        "Where-Object{$_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and "
        "$_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'})[0];"
        "function Await($op,$t){$m=$asTaskGeneric.MakeGenericMethod($t);"
        "$task=$m.Invoke($null,@($op));$task.Wait(-1)|Out-Null;$task.Result};"
        "[Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime]|Out-Null;"
        "[Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime]|Out-Null;"
        "$null=Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus]);"
        "$radios=Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) "
        "([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]]);"
        "$bt=$radios|Where-Object{$_.Kind -eq 'Bluetooth'};"
        "if(-not $bt){'NO_RADIO'}else{($bt|ForEach-Object{$_.State.ToString()}) -join ','}"
    )
    try:
        r = subprocess.run(['powershell', '-NonInteractive', '-Command', radio_ps],
                           capture_output=True, text=True, timeout=30,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        state = (r.stdout or '').strip()
    except Exception as e:
        logger.info(f"[蓝牙] 开关检测异常：{e}")
        return False
    logger.info(f"[蓝牙] 无线电状态：{state!r}")
    if not state or state == 'NO_RADIO':
        logger.info("[蓝牙] 未找到蓝牙适配器，检测不通过")
        return False
    if 'On' not in state:
        logger.info("[蓝牙] 蓝牙开关未打开，检测不通过")
        return False
    logger.info("[蓝牙] 蓝牙开关：已打开")

    # ② 指定蓝牙设备是否已连接
    names = [n.strip() for n in str(bt_names_str).split(',') if n.strip()]
    if not names:
        logger.info("[蓝牙] 未配置蓝牙名称，仅校验开关，判定通过")
        return True
    pnp_ps = (
        "Get-PnpDevice | Where-Object {"
        " $_.InstanceId -like 'BTHENUM*' -or"
        " $_.InstanceId -like 'BTHHFENUM*' -or"
        " $_.InstanceId -like 'BTHLE*'"
        " } | Select-Object FriendlyName,Status | ConvertTo-Json -Compress"
    )
    try:
        r2 = subprocess.run(['powershell', '-NonInteractive', '-Command', pnp_ps],
                            capture_output=True, text=True, timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
        out = (r2.stdout or '').strip()
    except Exception as e:
        logger.info(f"[蓝牙] 设备检测异常：{e}")
        return False
    devices = []
    if out and out.lower() != 'null':
        try:
            parsed = json.loads(out)
            devices = [parsed] if isinstance(parsed, dict) else (parsed or [])
        except Exception:
            devices = []
    ok_names = [d.get('FriendlyName') for d in devices
                if d.get('FriendlyName') and d.get('Status') == 'OK']
    logger.info(f"[蓝牙] 已连接(状态OK)蓝牙设备：{ok_names if ok_names else '无'}")
    missing = [n for n in names if not any(n in d for d in ok_names)]
    if missing:
        logger.info(f"[蓝牙] 未连接的目标设备：{missing}，检测不通过")
        return False
    logger.info("[蓝牙] 所有目标蓝牙设备均已连接，检测通过")
    return True


def power_check_win():
    battery = psutil.sensors_battery()
    if battery is None:
        print("无法检测到电池，请确保这是一个平板或笔记本电脑，并且系统支持电池状态检测。")
        return

    # 判断是否在充电
    if battery.power_plugged:
        print("平板正在充电。")
        return True
    else:
        print("平板未在充电。")
        return False

def check_screen_on(logger):
    if not os.path.exists(screen_tools):
        logger.info(f"错误：未找到可执行文件 {screen_tools}")
        return None
    # 执行命令并捕获输出
    result = subprocess.run(
        [screen_tools, "IsMonitorOn"],
        capture_output=True,
        text=True,
        check=True
    )

    # 返回执行结果（包含返回值、标准输出和错误输出）
    return result.stdout.strip()


def pause_windows_updates(days=7):
    """
    暂停Windows自动更新（最多35天）
    原理：修改注册表PauseUpdatesExpiryTime时间戳
    """
    try:
        expiry_time = int((datetime.now() + timedelta(days=days)).timestamp() * 1e7) + 116444736000000000
        key_path = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"

        # 以管理员权限写入注册表
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "PauseUpdatesExpiryTime", 0, winreg.REG_QWORD, expiry_time)
            winreg.SetValueEx(key, "PauseFeatureUpdatesEndTime", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "PauseQualityUpdatesEndTime", 0, winreg.REG_DWORD, 0)
            print(f"已成功暂停更新至 {datetime.now() + timedelta(days=days)}")

        # 重启更新服务
        subprocess.run("net stop wuauserv", shell=True)
        subprocess.run("net start wuauserv", shell=True)

    except Exception as e:
        print("操作失败，请以管理员权限运行脚本！错误详情：", str(e))


def resume_windows_updates(logger):
    """
    立即恢复Windows自动更新
    """
    try:
        key_path = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"

        # 删除相关注册表项
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
            try:
                winreg.DeleteValue(key, "PauseUpdatesExpiryTime")
                winreg.DeleteValue(key, "PauseFeatureUpdatesEndTime")
                winreg.DeleteValue(key, "PauseQualityUpdatesEndTime")
            except FileNotFoundError:
                pass  # 如果键值不存在则忽略

            # 重置更新检查标记
            winreg.SetValueEx(key, "FlightSettingsMaxPauseDays", 0, winreg.REG_DWORD, 0)

        logger.info("已恢复Windows自动更新")

        # 重启更新服务
        subprocess.run("net stop wuauserv", shell=True)
        subprocess.run("net start wuauserv", shell=True)

    except Exception as e:
        print("恢复失败，请以管理员权限运行脚本！错误详情：", str(e))




def on_start(test_items, auto_start_type,test_Config, logger):
    test_items = [key for key, value in test_items.items() if value]
    def check_pause_and_stop():
        # 在适当的位置添加检查 is_running 的代码
        if not is_running:
            update_button_states(logger)  # 调用更新按钮状态的函数
            logger.info("已成功停止运行。")
            sys.exit()
    host_ip = test_Config['host_ip']
    connect_wifi_name = test_Config['connect_wifi_name']
    wifi_password = test_Config['wifi_password']
    connect_timeout = int(test_Config['connect_timeout'])
    boot_delay = int(test_Config['boot_delay'])
    try:
        rms_mic = int(test_Config['rms_mic'])
    except:
        pass

    try:
        time_set_sleep = int(test_Config['time_set_sleep'])
    except:
        pass
    try:
        time_set_screen = int(test_Config['time_set_screen'])
    except:
        pass
    try:
        record_time = int(test_Config['record_time'])
    except:
        pass
    try:
        u_disk_names = test_Config['u_disk_name'].strip()
        u_disk_name = u_disk_names.split(",") if u_disk_names else []
    except:
        pass

    try:
        camera_names = test_Config['camera_name'].strip()
        camera_name = camera_names.split(",") if camera_names else []
    except:
        pass
    try:
        sim_check = float(test_Config['sim_check'])
    except:
        pass
    light_threshold = None
    try:
        light_threshold = float(test_Config['light_threshold'])
    except:
        pass
    try:
        bt_name = test_Config['bt_name']  # 蓝牙名称（英文逗号分隔）
    except:
        bt_name = ''


    for i in range(boot_delay):
        time.sleep(1)
        logger.info(f"等待前置延时中，{boot_delay-i}s")
        check_pause_and_stop()

    #暂停windows系统更新
    # pause_windows_updates(days=7)

    port = 12345

    # 删除缓存文件，避免内存不足
    current_mei_dir = os.path.dirname(sys.executable)
    clean_old_mei_directories(logger,exclude_dir=current_mei_dir)

    check_pause_and_stop()

    # 添加开机自启动任务
    if auto_start_type == '是':
        create_task_xml(exe_path, file_path, logger,script_args=None, delay_seconds=30)

    if auto_start_type == '否':
        delete_task(logger)


    check_pause_and_stop()

    os.system(f"powercfg /change monitor-timeout-ac {time_set_screen}")
    os.system(f"powercfg /change monitor-timeout-dc {time_set_screen}")
    os.system(f"powercfg /change standby-timeout-ac {time_set_sleep}")
    os.system(f"powercfg /change standby-timeout-dc {time_set_sleep}")

    check_pause_and_stop()

    while is_running:
        # 连接wifi
        if connect_wifi_name == "无":
            logger.info("设置不连接wifi")
            check_pause_and_stop()
        else:
            logger.info(f"当前连接wifi为{get_connected_wifi_name()},需要连接的wifi为{connect_wifi_name}")
            while get_connected_wifi_name() != connect_wifi_name:
                # 连接到特定的WiFi网络
                if wifi_password == "无":
                    connect_to_wifi(connect_wifi_name)
                else:
                    connect_to_wifi(connect_wifi_name, wifi_password)
                logger.info(f'尝试连接wifi:{connect_wifi_name}...')
                time.sleep(20)
                logger.info(f"已连接上wifi:{connect_wifi_name}")
                check_pause_and_stop()
            time.sleep(10)
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(connect_timeout)  # 设置超时时间为 300 秒（5 分钟）

        try:
            # 连接到服务器
            logger.info('尝试连接到服务器...')
            s.connect((host_ip, port))
            logger.info('已连接到服务器')

            while is_running:
                try:
                    data = s.recv(1024)
                    if not data:
                        raise socket.timeout  # 如果没有收到数据，假设超时
                except socket.timeout:
                    logger.info('接收数据超时，重新连接...')
                    s.close()
                    break
                except Exception as e:
                    logger.info(f'接收数据失败: {e}')
                    break


                if data.decode() == '1':
                    logger.info('已收到服务端连接码1')
                    s.sendall(b'11')
                    continue

                check_pause_and_stop()

                if data.decode() == '14':
                    logger.info("已收到码14，开始检查驱动")
                    if check_all_driver(logger) is True:
                        s.sendall(b'141')
                    if check_all_driver(logger) is False:
                        s.sendall(b'140')
                    continue

                check_pause_and_stop()

                if data.decode() == '3':
                    logger.info("已收到码3，开始检查扬声器")
                    s.sendall(b'32')
                    time.sleep(2)
                    logger.info("已发送码32，开始播放音频")
                    play_audio(test_wav_path)
                    time.sleep(2)
                    continue

                check_pause_and_stop()

                if data.decode() == '4':
                    logger.info("收到码4，开始检查麦克风")
                    s.sendall(b'42')
                    logger.info("开始录音，录制指定时间")
                    record_audio(record_time, test_wav_Save_path)
                    logger.info("分析录音数据，检查录音数据是否正常")
                    with wave.open(test_wav_Save_path, 'rb') as wf:
                        signal = wf.readframes(-1)
                        arr = np.frombuffer(signal, dtype=np.int16)
                        spectrum = np.abs(np.fft.fft(arr))
                        rms = np.sum(spectrum)
                    logger.info(rms)
                    if rms < rms_mic:
                        s.sendall(b'40')  # 30表示音频数据不达标，麦克风无声
                        logger.info("麦克风无声，已发送码40")
                        continue
                    if rms > rms_mic:
                        s.sendall(b'41')  # 21表示音频数据达标，麦克风有声音
                        logger.info("麦克风正常，已发送码41")
                        continue

                check_pause_and_stop()

                if data.decode() == '5':
                    logger.info("收到码5，开始切换系统")
                    s.sendall(b'52')
                    logger.info("开始切系统")
                    win_to_android(logger)
                    continue

                check_pause_and_stop()

                if data.decode() == '6':
                    logger.info("收到码6，开始快速切换系统(IPC)")
                    s.sendall(b'62')
                    logger.info("开始快速切系统")
                    win_to_android_fast(logger)
                    continue


                check_pause_and_stop()

                if data.decode() == '7':
                    logger.info("收到码7，开始检测U盘")
                    if compare_usb_names(u_disk_name, get_current_usb_names(logger),logger) is True:
                        s.sendall(b'70')
                        logger.info("U盘检测通过，已发送码70")
                        continue
                    if compare_usb_names(u_disk_name, get_current_usb_names(logger),logger) is False:
                        s.sendall(b'71')
                        logger.info("U盘检测不通过，已发送码71")
                        continue

                check_pause_and_stop()

                if data.decode() == '15':
                    logger.info("收到码15，开始检测息屏状态")
                    if check_screen_on(logger) == "False":
                        s.sendall(b'150')
                        logger.info("息屏检测通过，已发送码150")
                        continue
                    else:
                        s.sendall(b'151')
                        logger.info("息屏检测不通过，已发送码151")
                        continue

                check_pause_and_stop()

                if data.decode() == '16':
                    logger.info("收到码16，开始检测唤醒状态")
                    if check_screen_on(logger) == "True":
                        s.sendall(b'160')
                        logger.info("唤醒状态检测通过，已发送码160")
                        continue
                    else:
                        s.sendall(b'161')
                        logger.info("唤醒状态检测不通过，已发送码161")
                        continue


                check_pause_and_stop()

                if data.decode() == '8':
                    logger.info("收到码8，开始检测相机")
                    if compare_camera_names(camera_name, get_camera_list(logger),logger) is True:
                        if check_megabook_camera(sim_check,camera_name,logger) is True:
                            s.sendall(b'80')
                            logger.info("相机检测通过，已发送码80")
                            continue
                        else:
                            s.sendall(b'81')
                            logger.info("相机检测不通过，已发送码81")
                            continue
                    else:
                        s.sendall(b'81')
                        logger.info("相机检测不通过，已发送码81")
                        continue

                check_pause_and_stop()

                if data.decode() == '9':
                    logger.info("收到码9，开始重启系统")
                    s.sendall(b'92')
                    logger.info("开始重启系统")
                    winx_operation(logger,"R")
                    continue

                check_pause_and_stop()

                if data.decode() == '110':
                    logger.info("收到码110，开始关机")
                    s.sendall(b'112')
                    logger.info("开始关机")
                    winx_operation(logger,"U")
                    continue

                check_pause_and_stop()

                if data.decode() == '130':
                    logger.info("收到码130，开始进入睡眠")
                    s.sendall(b'132')
                    logger.info("开始睡眠")
                    winx_operation(logger,"S")
                    continue

                check_pause_and_stop()

                if data.decode() == '170':
                    logger.info("收到码170，开始进入休眠")
                    s.sendall(b'172')
                    logger.info("开始休眠")
                    winx_operation(logger,"H")
                    continue

                check_pause_and_stop()

                if data.decode() == '180':
                    logger.info("收到码180，开始设置无操作息屏和睡眠时间")
                    s.sendall(b'182')
                    logger.info("设置完成")
                    os.system(f"powercfg /change monitor-timeout-ac {time_set_screen}")
                    os.system(f"powercfg /change monitor-timeout-dc {time_set_screen}")
                    os.system(f"powercfg /change standby-timeout-ac {time_set_sleep}")
                    os.system(f"powercfg /change standby-timeout-dc {time_set_sleep}")
                    continue

                check_pause_and_stop()

                if data.decode() == '120':
                    logger.info("收到码120，开始检测充电")
                    if power_check_win() is False:
                        s.sendall(b'121')
                        logger.info("未在充电")
                    if power_check_win() is True:
                        s.sendall(b'122')
                        logger.info("正在充电")
                    continue

                check_pause_and_stop()

                if data.decode() == '200':
                    logger.info("收到码200，开始检测光感传感器")
                    ok, lux = check_light_sensor(logger, light_threshold)
                    if ok:
                        s.sendall(b'202')
                        logger.info(f"光感检测通过，已发送码202（lux={lux:.2f}，阈值={light_threshold}）")
                    else:
                        s.sendall(b'201')
                        lux_str = f"{lux:.2f}" if lux is not None else "无读数"
                        logger.info(f"光感检测不通过，已发送码201（lux={lux_str}，阈值={light_threshold}）")
                    continue

                check_pause_and_stop()

                if data.decode() == '210':
                    logger.info("收到码210，开始检测蓝牙（开关+已连接设备）")
                    if check_bluetooth(bt_name, logger) is True:
                        s.sendall(b'212')
                        logger.info("蓝牙检测通过，已发送码212")
                    else:
                        s.sendall(b'211')
                        logger.info("蓝牙检测不通过，已发送码211")
                    continue

        except Exception as e:
            error_msg = traceback.format_exc()
            logger.info(f"连接失败{error_msg}")
        finally:
            s.close()

        time.sleep(10)  # 在重新尝试连接之前等待一段时间
        check_pause_and_stop()

# 定义结束按钮的事件函数
def on_stop_button_clicked(logger):
    # 使用 global 关键字声明修改全局变量
    global s
    global is_running
    is_running = False
    logger.info("测试结束按钮已被点击,程序即将停止运行,请等待")
    update_button_states(logger)  # 调用更新按钮状态的函数

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
    # 本程序需管理员权限运行(powercfg/任务计划/模拟键鼠等)。非管理员则弹UAC以管理员身份重启自身。
    if not is_admin():
        if restart_as_admin():
            sys.exit(0)  # 已拉起管理员实例，退出当前非管理员实例
        else:
            try:
                tkMessageBox.showerror("权限不足", "本程序需要管理员权限运行。\n请右键选择“以管理员身份运行”，或在UAC弹窗中点击“是”。")
            except Exception:
                pass
            sys.exit(1)
    frame_main()




