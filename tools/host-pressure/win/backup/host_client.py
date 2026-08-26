# -*- coding: utf-8 -*-

"""
2025-1-3:
1、增加界面
2、新增开机自启动
3、脚本名称及版本号修改为：win压测脚本-CLIENT端-V1.1（需以管理员权限启动）
2024-10-31:新增检查项，检测是否出现两分钟后重启的现象
"""

import socket
import time
import os
import logging
from logging import handlers
import sys
import subprocess
import pywifi
from pywifi import const
import win32com.client
import shutil
import glob
import tkinter as tk
from tkinter import ttk
from tkinter import font
import tkinter.messagebox as tkMessageBox
import threading
from datetime import datetime
import json
from multiprocessing import freeze_support



current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # 当前工作目录
exe_path = os.path.join(current_working_dir,'audiotest_client.exe')
log_path = os.path.join(current_working_dir, 'logs')
test_wav_path = os.path.join(current_working_dir, 'test.wav')
test_wav_Save_path = os.path.join(current_working_dir, 'recorded_audio.wav')
hdmi_8k_mega_image = os.path.join(os.path.join(current_working_dir, '8k_mega_image'), '8k_mega.jpg')
hdmi_edp_mega_image = os.path.join(os.path.join(current_working_dir, 'edp_mega_image'), 'edp_mega.jpg')
test_image = os.path.join(os.path.join(current_working_dir, 'test_image'), 'test.jpg')
setting_path = r'C:\Program Files (x86)\H3C.Magic\MagicSetting\H3C.Entry.exe'
hdmi_in_path = r'C:\Program Files (x86)\H3C.Magic\MagicHdmiRecord\H3C.Entry.exe'
mega_x1 = 2277  # 切换系统按钮横坐标
mega_y1 = 3357  # 切换系统按钮纵坐标
mega_x2 = 4023  # 确定按钮横坐标
mega_y2 = 2245  # 确定按钮纵坐标
edp_mega_x1 = 1172  # 切换系统按钮横坐标
edp_mega_y1 = 1695  # 切换系统按钮纵坐标
edp_mega_x2 = 2020  # 确定按钮横坐标
edp_mega_y2 = 1140  # 确定按钮纵坐标
is_running = True

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


def get_logger(log_filename, level=logging.INFO, when='W0', back_count=0, text_widget=None):
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
        'connect_wifi_name':'setting-5G-open',
        'wifi_password':"YOUR_WIFI_PASSWORD",
        'connect_timeout':'300',
        'rms_mic': '100000000000',
        'record_time': '10',
        'u_disk_name':'',
        'camera_name': '',
        'boot_delay': '30',
        'sim_check': '0.8',
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


    if not test_items_vars['HDMI Record检测'].get() and not test_items_vars['HDMI Extend检测'].get():
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
    root.title('win压测脚本-CLIENT端-V1.1（需以管理员权限启动）')

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
    type_combobox['values'] = ('8K','edp')
    type_combobox.pack(side=tk.TOP, fill=tk.X)
    type_var.set("8K")

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
    test_items = ['HDMI Record检测', 'HDMI Extend检测', '麦克风检测', '相机检测', 'U盘检测']

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
        ('connect_wifi_name', '连接的wifi名称(不连wifi填无)'),
        ('wifi_password', 'wifi密码（无密码填无）'),
        ('connect_timeout', '连接超时'),
        ('rms_mic', '麦克风阈值'),
        ('record_time', '录音时长'),
        ('u_disk_name', 'U盘名称(多个以英文,分隔)'),
        ('camera_name', '相机名称'),
        ('boot_delay', '程序启动延时'),
        ('sim_check', '相似度阈值'),
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
    config_path = 'config_client.json'
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

    # 创建开始按钮
    start_button = ttk.Button(bottom_frame, text="开始",
                              command=lambda: on_start_button_clicked(config_vars, logger))
    start_button.pack(side=tk.LEFT, expand=True)

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

    root.after(0, lambda: on_start_button_clicked(config_vars, logger))

    # 开始主循环
    root.mainloop()

# 在on_start_test函数中添加一个helper函数来更新按钮状态
def update_button_states():
    start_button['state'] = tk.NORMAL  # 启用开始按钮
    stop_button['state'] = tk.DISABLED  # 禁用结束按钮


def task_exists(scheduler, task_name):
    """检查任务是否已经存在"""
    try:
        root_folder = scheduler.GetFolder("\\")
        task = root_folder.GetTask(task_name)
        return task is not None
    except Exception as e:
        return False

def create_task_xml(executable_path, working_directory, logger,script_args=None, delay_seconds=30):
    task_name = 'win_client_task'
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

        # Debug 打印日志查看XML内容是否正确
        print(task_xml)

        # 通过任务计划程序注册任务
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        # 检查任务是否已存在
        if task_exists(scheduler, task_name):
            logger.info(f'任务 "{task_name}" 已存在，取消创建')
            return

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
    task_name = 'win_client_task'
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


def on_start_button_clicked(config_vars,logger):
    # 重置全局变量
    global is_running
    is_running = True
    log_text.configure(state="normal")
    log_text.delete("1.0",tk.END)
    log_text.configure(state="disabled")

    # 获取所有配置项的值
    configs_to_save = {k: v.get() for k, v in config_vars.items()}

    # 获取并保存测试项目
    configs_to_save['test_project'] = type_var.get()

    # 获取并保存停止方式
    configs_to_save['auto_start_type'] = auto_start_var.get()

    # 获取并保存选中的测试项
    configs_to_save['selected_test_items'] = {item: var.get() for item, var in test_items_vars.items()}
    # 保存到配置文件
    save_config(configs_to_save, 'config_client.json')

    # 获取测试项目
    test_project = type_var.get()

    # 获取停止方式
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
                                   args=(test_project, auto_start_type,test_Config, logger))
    test_thread.start()
    start_button['state'] = tk.DISABLED  # 禁用开始按钮
    stop_button['state'] = tk.NORMAL  # 启用结束按钮


def on_start_test(test_project,auto_start_type ,test_Config, logger):
    # 这里是处理测试开始逻辑的地方
    # 你可以使用selected_method, selected_test_items, test_Config变量
    test_project_type = test_project
    on_start(test_project_type, auto_start_type,test_Config, logger)


# 定义按钮点击事件的处理函数
def on_open_log_folder_clicked():
    os.startfile(log_path)


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


def proc_exist(process_name):
    is_exist = False
    wmi = win32com.client.GetObject('winmgmts:')
    processCodeCov = wmi.ExecQuery('select * from Win32_Process where name=\"%s\"' % process_name)
    if len(processCodeCov) > 0:
        is_exist = True
    return is_exist

def host_test(logger):
    while True:
        conn.sendall(b'3000')  # 3表示开始检测win下热点
        logger.info('已发送码3000，进入检测win下热点')
        response = conn.recv(1024)
        if response.decode() == '3001':
            logger.info('已收到码3001，热点检测通过')
            return True
        if response.decode() == '3002':
            logger.info('已收到码3001，热点检测不通过')
            return False
        else:
            logger.info('未成功通信，热点连接失败')
            return False

def clean_old_mei_directories(logger,exclude_dir=None):
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


def on_start(test_project, auto_start_type,test_Config, logger):
    def check_pause_and_stop():
        # 在适当的位置添加检查 is_running 的代码
        if not is_running:
            update_button_states()  # 调用更新按钮状态的函数
            logger.info("已成功停止运行。")
            sys.exit()
    connect_wifi_name = test_Config['connect_wifi_name']
    wifi_password = test_Config['wifi_password']
    connect_timeout = int(test_Config['connect_timeout'])
    boot_delay = int(test_Config['boot_delay'])

    for i in range(boot_delay):
        time.sleep(1)
        logger.info(f"等待前置延时中，{boot_delay-i}s")
        check_pause_and_stop()


    # 删除缓存文件，避免内存不足
    current_mei_dir = os.path.dirname(sys.executable)
    clean_old_mei_directories(logger,exclude_dir=current_mei_dir)

    check_pause_and_stop()

    # 添加开机自启动任务
    if auto_start_type == '是':
        create_task_xml(exe_path, current_working_dir, logger,script_args=None, delay_seconds=30)

    if auto_start_type == '否':
        delete_task(logger)

    check_pause_and_stop()

    retry = 0
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
                retry += 1
        if retry >= 20:
            logger.info("连接大屏热点失败")
            update_button_states()  # 调用更新按钮状态的函数
            sys.exit()


        global conn
        global response
        host = '0.0.0.0'
        port = 60002
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(1)
            s.settimeout(3000)  # 设置超时时间为30秒
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

        a = 0
        while True:
            conn.sendall(b'3000')  # 3表示开始检测win下热点
            logger.info('已发送码3000，进入检测win下热点')
            response = conn.recv(1024)
            if response.decode() == '3001':
                logger.info('已收到码3001，热点检测通过')
                os.system('shutdown /r /t 1')
            else:
                logger.info('未成功通信，热点连接失败,重试')
                a += 1
                time.sleep(5)
            if a >= 5:
                logger.info('未成功通信，热点连接失败')




# 定义结束按钮的事件函数
def on_stop_button_clicked(logger):
    # 使用 global 关键字声明修改全局变量
    global is_running
    is_running = False
    logger.info("测试结束按钮已被点击,程序即将停止运行,请等待")

if __name__ == '__main__':
    freeze_support()
    frame_main()




