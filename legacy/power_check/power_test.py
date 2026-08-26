# -*- coding: utf-8 -*-

"""
2025-4-8 修改点：
1、充电检测
"""

from logging import handlers
import tkinter.messagebox as tkMessageBox
import psutil
import subprocess
import logging
import sys
import os
import time
import wave
from datetime import datetime
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

requests.adapters.DEFAULT_RETRIES = 300
current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # 当前工作目录
log_path = os.path.join(current_working_dir, 'logs')
current_time = datetime.now()
formatted_date = current_time.strftime("%m-%d")
monkey_log_path = os.path.join(log_path, f"monkey_{formatted_date}.log")

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

global test_type_list
test_type_list = ['上下电']

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


def get_logger(log_filename, level=logging.INFO, when='W0', back_count=0, text_widget=None):
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
        'power_ip': 'emulator-5554',
        'connect_wifi_name':'setting-5G-open',
        'wifi_password':"YOUR_WIFI_PASSWORD",
        'power_sn':'0',
        'power_path': r'D:\leidian\LDPlayer9\dnplayer.exe',
        'test_interval': '80',
        'power_process_name': 'dnplayer.exe',
        'test_project': 'megabook',
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
    # 更新测试条目和配置项的可见性
    on_method_changed()

def on_method_changed(event=None):
    update_config_visibility()
# 更新配置项的显示状态
def update_config_visibility():
    if type_var.get() == '单win（非双系统切换）':
        config_labels['device_ip'].grid_remove()
        config_entries['device_ip'].grid_remove()
    else:
        config_labels['device_ip'].grid()
        config_entries['device_ip'].grid()

def on_method_changed(event=None):
    update_config_visibility()

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
    global environment_var
    global environment_combobox

    test_items_vars = {}

    # 创建主窗口
    root = tk.Tk()
    root.title('充电检测压测脚本V1.0')

    # 初始化环境变量
    environment_var = tk.StringVar(value='无')  # 设置默认值为无
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
    type_combobox['values'] = ('megabook（单安卓或双系统切换）',"单win（非双系统切换）")
    type_combobox.pack(side=tk.TOP, fill=tk.X)
    type_var.set("megabook（单安卓或双系统切换）")
    type_combobox.bind('<<ComboboxSelected>>', on_type_changed)

    # 第二项 - 选择测试方法
    method_label = ttk.Label(left_frame, text="选择测试方法", font=bold_font)
    method_label.pack(side=tk.TOP, anchor=tk.W,pady=(10, 0))

    method_var = tk.StringVar()
    method_combobox = ttk.Combobox(left_frame, textvariable=method_var, state='readonly')
    method_combobox['values'] = ('上下电')
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
    test_items = ['充电检测']

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
        ('power_ip', '模拟器IP'),
        ('connect_wifi_name', '连接的wifi名称(不连wifi填无)'),
        ('wifi_password', 'wifi密码（无密码填无）'),
        ('power_sn', '智能设备端口'),
        ('power_path', '模拟器应用的安装地址'),
        ('power_process_name', '模拟器进程名称'),
        ('power_name', '智能设备的名称'),
        ('test_interval', '测试间隔（只填数字，单位S）'),
        ('test_message', '测试项目-机器-人员')
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
    config_path = 'config_power.json'
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
        if key == 'environment':  # 检查是否有环境配置选项的保存
            environment_var.set(value)  # 设置环境配置选项
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
    save_config(configs_to_save, 'config_power.json')

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

    # 启动线程来执行on_start函数
    test_thread = threading.Thread(target=on_start_test,
                                   args=(test_project,selected_method,stop_type, selected_test_items, test_configs, root, logger))
    test_thread.start()
    start_button['state'] = tk.DISABLED  # 禁用开始按钮
    pause_button['state'] = tk.NORMAL  # 启用暂停按钮
    stop_button['state'] = tk.NORMAL  # 启用结束按钮


def on_start_test(test_project,selected_method, stop_type,selected_test_items, test_configs,root, logger):
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


def check_and_reconnect(device_ip, power_ip, power_sn, power_path, power_process_name, power_name, logger,test_select):
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}

    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        reopen_power(power_process_name, power_path, logger)
    comnon_to_power(power_ip, power_sn, power_name)
    if android_or_win == 'android':
        if f"{device_ip}:5555" not in device_status.keys() or device_status[f"{device_ip}:5555"].strip() != 'device':
            raise RuntimeError("设备未成功连接大屏ip")

def check_and_reconnect_home_on(device_ip, power_ip, power_path, power_process_name, logger,power_name,test_select):
    devices = get_adb_devices()
    logger.info(devices)
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}

    if power_ip not in device_status.keys() or device_status.get(power_ip) != 'device':
        reopen_power(power_process_name, power_path, logger)
    if android_or_win == 'android':
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

def check_and_reconnect_reboot_except(device_ip,logger):
    run_command(f"adb disconnect {device_ip}")
    run_command(f'adb connect {device_ip}')
    logger.info('已重新断开再连接adb')


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
            "text": f"测试项目-机器-人员：{message}\n报错信息：{message}"
        }
    }
    push_report(webhook, message_body, logger)

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
    run_command(f"adb -s {ip} pull /data/tombstones {target_dir}")
    run_command(f"adb -s {ip} pull /data/anr {target_dir}")

    #转存dmesg文件
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
        logger.info(f"清空日志文件夹时发生异常：{e}")

    logger.info(f"所有日志文件都已下载至 {target_dir}.")

def power_check_android(ip):
    # 执行 adb 命令来获取电池状态
    result = subprocess.run(['adb', f"{ip}",'shell', 'dumpsys', 'battery'], capture_output=True, text=True)
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

def power_check_win(want_status):
    while True:
        conn.sendall(b'120')  # 3表示开始检测win下扬声器
        logger.info('已发送码120，进入检测win下充电')
        response = conn.recv(1024)
        if response.decode() == '121':
            logger.info("win-检测未在充电")
            status = False
            break
        if response.decode() == '122':
            logger.info("win-检测正在充电")
            status = True
            break
    if want_status == status:
        return True
    else:
        return False

def root_devices(ip):
    # 切换到root用户
    run_command(f"adb -s {ip} shell setprop persist.h3c.root_state 123@qwe")
    run_command(f"adb -s {ip} root")

#获取已连接的wifi名称
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



def on_start(test_project_type,test_type, stop_type_select,test_select, test_Config, root, logger):
    global check_pause_and_stop
    def check_pause_and_stop():
        while is_paused:
            time.sleep(0.1)  # 短暂睡眠，减少CPU使用
            root.after(0, update_button_text())
        # 在适当的位置添加检查 is_running 的代码
        if not is_running:
            update_button_states()  # 调用更新按钮状态的函数
            logger.info("已成功停止运行。")
            sys.exit()

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
        power_path = test_Config['power_path']  # 模拟器打开路径---
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
        test_interval = int(test_Config['test_interval'])  # 测试间隔---
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
    test_message = test_Config['test_message']  # 测试项目信息
    if test_project_type == "单win（非双系统切换）":
        android_or_win = 'win'
    if test_project_type == 'megabook（单安卓或双系统切换）':
        android_or_win = 'android'
    test_times_data = 0
    test_fail_times_data = 0

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

            check_pause_and_stop()  # 检查是否有停止或暂停信号


            if android_or_win == "win":
                global conn
                global response
                host = '0.0.0.0'
                port = 12345
                while True:
                    try:
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
                            response = conn.recv(1024)
                            while response.decode() != "11":
                                logger.info("正在连接中")
                                time.sleep(2)
                            logger.info("连接成功")
                            break
                    except socket.timeout:
                        # 捕获到超时异常
                        logger.info("等待连接超时，重新开始监听")
                    except Exception as e:
                        logger.error(f"发生错误: {e}")
                        continue

            check_pause_and_stop()  # 检查是否有停止或暂停信号

            # 判断adb是否正常连接
            if android_or_win == "android":
                run_command(f'adb connect {device_ip}')
                time.sleep(5)
                try:
                    check_and_reconnect_reboot(device_ip)
                except Exception as connect_e:
                    logger.info(f"设备连接失败,意外报错,继续下一轮,失败信息为{connect_e}")
                    check_and_reconnect_reboot_except(device_ip,logger)
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

            comnon_to_power(power_ip, power_sn, power_name)
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
                time.sleep(5)

            time.sleep(test_interval)
            if android_or_win == "win":
                if power_check_win(False) is True:
                    logger.info("检测win当前未在充电，与预期状态一致")
                if power_check_win(False) is False:
                    logger.info("检测win当前正在充电，与预期状态不一致")
                    if stop_type_select == "是":
                        update_button_states()  # 调用更新按钮状态的函数
                        sys.exit()
                    else:
                        test_fail_times_data += 1
                        run_tag = 1
            if android_or_win == "android":
                if power_check_android(device_ip) is False:
                    logger.info("检测安卓当前未在充电，与预期状态一致")
                if power_check_android(device_ip) is True:
                    logger.info("检测安卓当前正在充电，与预期状态不一致")
                    catch_logs(device_ip, logger, "power_check_fail")
                    if stop_type_select == "是":
                        update_button_states()  # 调用更新按钮状态的函数
                        sys.exit()
                    else:
                        test_fail_times_data += 1
                        run_tag = 1


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
                time.sleep(5)
            time.sleep(test_interval)
            if android_or_win == "win":
                if power_check_win(False) is False:
                    logger.info("检测win当前未在充电，与预期状态一致")
                if power_check_win(False) is True:
                    logger.info("检测win当前正在充电，与预期状态不一致")
                    if stop_type_select == "是":
                        update_button_states()  # 调用更新按钮状态的函数
                        sys.exit()
                    else:
                        test_fail_times_data += 1
                        run_tag = 1
            if android_or_win == "android":
                if power_check_android(device_ip) is True:
                    logger.info("检测安卓当前未在充电，与预期状态一致")
                if power_check_android(device_ip) is False:
                    logger.info("检测安卓当前正在充电，与预期状态不一致")
                    catch_logs(device_ip, logger, "power_check_fail")
                    if stop_type_select == "是":
                        update_button_states()  # 调用更新按钮状态的函数
                        sys.exit()
                    else:
                        test_fail_times_data += 1
                        run_tag = 1



            if run_tag == 0:
                logger.info(f"第{test_times_data + 1}次测试正常")
            else:
                logger.info(f"第{test_fail_times_data}次测试失败")
            time.sleep(test_interval)
            check_pause_and_stop()  # 检查是否有停止或暂停信号

            test_times_data += 1
            root.after(0, lambda: test_count_var.set(f"压测次数：{test_times_data}次"))
            root.after(0, lambda: test_fail_count_var.set(f"失败次数：{test_fail_times_data}次"))
        except Exception as e:
            logger.info(e)
            run_command(f"adb disconnect {device_ip}")
            time.sleep(10)
            run_command(f"adb connect {device_ip}")
            d = connect(device_ip)
            time.sleep(5)
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
    process_name = "PowerTest.exe"  # 如果打包成exe则填写exe文件名


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
