# -*- coding: utf-8 -*-

"""
双系统切换 DEMO（仅 Windows→安卓 切换 + 开机自启动）
========================================================
功能：
  1. 启动时检测管理员权限，非管理员则弹 UAC 以管理员身份重启自身（模拟键鼠需要管理员权限）。
  2. 支持注册/删除"开机自启动"任务计划（登录后延时自动拉起本程序）。
  3. 核心逻辑：程序被开机自启动拉起 == 当前已从安卓切换到 Windows，
     于是自动执行 Windows→安卓 切换（点击控制中心）。
     win_to_android() 在系统被切到安卓（进程冻结）后、下次回到 Win 时返回，
     外层循环再次切回安卓，形成自维持的双系统切换循环。

说明：本 demo 由正式客户端 MegaBook_Client 裁剪而来，仅保留双系统切换相关代码，
      其余（音频/相机/U盘/光感/蓝牙/socket/服务端通信等）全部删除。
"""

import os
import sys
import time
import json
import logging
import threading
import traceback
import ctypes
from datetime import datetime
from multiprocessing import freeze_support

import pyautogui
import win32com.client
import tkinter as tk
from tkinter import ttk
from tkinter import font
import tkinter.messagebox as tkMessageBox


# ── 名称/路径（统一修改处）────────────────────────────────────────────
file_path = os.path.dirname(os.path.realpath(sys.argv[0]))
exe_path = os.path.join(file_path, 'MegaBook_Switch_Demo.exe')
root_title = 'MegaBook_Switch_Demo（双系统切换demo，需以管理员权限启动）'
task_name = 'win_switch_demo_megabook'
log_path = os.path.join(file_path, 'logs')
config_path = os.path.join(file_path, 'config_switch_demo.json')

# 控制中心点击坐标序列（必须与实机分辨率匹配；与正式客户端 win_to_android 一致）
SWITCH_START_X = 2440          # 第一步点击的起始 X（每轮 -30 微调，<2280 时回到起点）
SWITCH_MIN_X = 2280
# 从安卓切回Win后系统处于休眠/锁屏，需先点"登录"进入桌面，再点控制中心切回安卓
SWITCH_LOGIN_XY = (1440, 982)  # 登录按钮坐标

is_running = True


# ── 日志（按日期切换文件名 switch_demo_MM-DD.log）──────────────────────
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
            self.text.yview(tk.END)

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
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fh = DailyDateFileHandler(log_path, log_prefix, encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    if text_widget:
        th = TextHandler(text_widget)
        th.setLevel(level)
        th.setFormatter(formatter)
        logger.addHandler(th)
    return logger


# ── 配置持久化 ─────────────────────────────────────────────────────────
def load_config():
    default_config = {
        'boot_delay': '30',        # 进入Win后等待系统稳定再切换的延时（秒）
        'auto_start_type': '是',    # 是否注册开机自启动
    }
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return default_config


def save_config(config):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


# ── 开机自启动任务计划 ─────────────────────────────────────────────────
def create_task_xml(executable_path, working_directory, logger, delay_seconds=30):
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
          <Arguments></Arguments>
          <WorkingDirectory>{working_directory}</WorkingDirectory>
        </Exec>
      </Actions>
    </Task>"""
    try:
        user_name = os.getlogin()
        task_xml = TASK_XML_TEMPLATE.format(
            delay_seconds=delay_seconds,
            command=executable_path,
            working_directory=working_directory,
            user_id=user_name
        )
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        task_definition = scheduler.NewTask(0)
        task_definition.XmlText = task_xml
        root_folder.RegisterTaskDefinition(
            task_name, task_definition, 6, user_name, None, 3)
        logger.info(f'{task_name} 开机自启动任务已创建（延时 {delay_seconds}s）')
    except Exception as e:
        logger.info(f"任务创建失败，原因：{e}")


def delete_task(logger):
    try:
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        try:
            root_folder.GetTask(task_name)
        except Exception:
            logger.info(f'{task_name} 任务不存在')
            return
        root_folder.DeleteTask(task_name, 0)
        logger.info(f'{task_name} 任务已删除，不再自动执行')
    except Exception as e:
        logger.info(f"删除任务失败，原因：{e}")


# ── 核心：Windows → 安卓 切换 ──────────────────────────────────────────
def win_to_android(logger):
    """点击控制中心把系统从 Windows 切换到安卓。
    点击成功后系统切到安卓、本进程被冻结；下次系统回到 Win 时进程恢复，
    通过"单轮耗时 >30 秒"判定曾被冻结（即已切到安卓又回到Win），结束本次切换并返回。"""
    pyautogui.FAILSAFE = False
    x = SWITCH_START_X
    times = 1
    while is_running:
        iter_start = time.time()
        logger.info(f"第{times}次尝试切换系统（Windows→安卓）")
        resumed = False
        # 先点"登录"进入桌面（切回Win时为休眠/锁屏），再逐步点击控制中心切换到安卓；每步后检测本轮累计耗时
        for click_x, click_y, wait in [(SWITCH_LOGIN_XY[0], SWITCH_LOGIN_XY[1], 2), (x, 1750, 1), (2597, 1530, 1), (1546, 1010, 2)]:
            if not is_running:
                return
            pyautogui.click(click_x, click_y)
            time.sleep(wait)
            # 休眠恢复检测：正常一轮约4秒，若本轮后累计耗时远超(>30秒)，
            # 说明进程曾被冻结——即系统已切到安卓后又切回Win，本次切换任务已过期，立即停止。
            if time.time() - iter_start > 30:
                resumed = True
                break
        if resumed:
            logger.info("检测到曾被冻结后恢复（已从安卓回到Windows），本次切换结束")
            break
        x -= 30
        times += 1
        if x < SWITCH_MIN_X:
            x = SWITCH_START_X


def run_switch_loop(boot_delay, logger):
    """主循环：进入Win后等待稳定 → 切到安卓 → win_to_android返回(说明又回到Win) → 再切。"""
    def wait_stable(label):
        for i in range(boot_delay):
            if not is_running:
                return False
            logger.info(f"{label}，剩余 {boot_delay - i}s")
            time.sleep(1)
        return True

    logger.info("程序已启动：判定当前已从安卓切换到 Windows，准备自动切回安卓")
    if not wait_stable("进入Windows后等待系统稳定"):
        return
    while is_running:
        logger.info("开始执行 Windows→安卓 切换")
        win_to_android(logger)
        if not is_running:
            break
        logger.info("已从安卓恢复到 Windows，准备再次切回安卓")
        if not wait_stable("再次切换前等待系统稳定"):
            return


# ── GUI ────────────────────────────────────────────────────────────────
def frame_main():
    global start_button, stop_button, auto_start_var, log_text

    root = tk.Tk()
    root.title(root_title)

    def on_closing():
        logging.shutdown()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    bold_font = font.Font(family='Helvetica', size=10, weight='bold')

    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 左侧配置区
    left_frame = ttk.LabelFrame(main_frame, text="配置", padding="10 10 10 10")
    left_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(left_frame, text="开启自启动", font=bold_font).pack(side=tk.TOP, anchor=tk.W)
    auto_start_var = tk.StringVar()
    auto_start_combobox = ttk.Combobox(left_frame, textvariable=auto_start_var, state='readonly')
    auto_start_combobox['values'] = ('是', '否')
    auto_start_combobox.pack(side=tk.TOP, fill=tk.X)
    auto_start_var.set("是")

    ttk.Label(left_frame, text="进入Win后切换延时(秒)", font=bold_font).pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))
    boot_delay_var = tk.StringVar(value='30')
    boot_delay_entry = ttk.Entry(left_frame, textvariable=boot_delay_var)
    boot_delay_entry.pack(side=tk.TOP, fill=tk.X)

    # 右侧日志区
    log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10 10 10 10")
    log_frame.grid(column=1, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)
    log_text = tk.Text(log_frame, wrap='word', state='disabled', height=18, width=60)
    log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    logger = get_logger('switch_demo', text_widget=log_text)

    # 应用已保存配置
    loaded = load_config()
    auto_start_var.set(loaded.get('auto_start_type', '是'))
    boot_delay_var.set(loaded.get('boot_delay', '30'))

    # 底部按钮
    bottom_frame = ttk.Frame(main_frame, padding="10 10 10 10")
    bottom_frame.grid(column=0, row=1, columnspan=2, sticky=(tk.W, tk.E))

    def do_start():
        global is_running
        is_running = True
        log_text.configure(state="normal")
        log_text.delete("1.0", tk.END)
        log_text.configure(state="disabled")

        try:
            boot_delay = int(boot_delay_var.get())
        except ValueError:
            tkMessageBox.showerror("错误", "切换延时请填写整数（秒）")
            return

        auto_start_type = auto_start_var.get()
        save_config({'boot_delay': str(boot_delay), 'auto_start_type': auto_start_type})

        # 注册/删除开机自启动
        if auto_start_type == '是':
            create_task_xml(exe_path, file_path, logger, delay_seconds=30)
        else:
            delete_task(logger)

        threading.Thread(target=run_switch_loop, args=(boot_delay, logger), daemon=True).start()
        start_button['state'] = tk.DISABLED
        stop_button['state'] = tk.NORMAL

    def do_stop():
        global is_running
        is_running = False
        logger.info("结束按钮已点击，程序即将停止切换，请等待")
        start_button['state'] = tk.NORMAL
        stop_button['state'] = tk.DISABLED

    start_button = ttk.Button(bottom_frame, text="开始", command=do_start)
    start_button.pack(side=tk.LEFT, expand=True)
    stop_button = ttk.Button(bottom_frame, text="结束", command=do_stop, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, expand=True)
    ttk.Button(bottom_frame, text="禁用开机自启动", command=lambda: delete_task(logger)).pack(side=tk.LEFT, expand=True)
    ttk.Button(bottom_frame, text="打开日志文件夹", command=lambda: os.startfile(log_path)).pack(side=tk.LEFT, expand=True)

    root.minsize(700, 420)

    # 开机自启动拉起后自动开始切换
    root.after(0, do_start)
    root.mainloop()


# ── 管理员权限 ─────────────────────────────────────────────────────────
def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def restart_as_admin():
    exe = sys.executable
    if getattr(sys, 'frozen', False):
        import subprocess
        params = subprocess.list2cmdline(sys.argv[1:])
    else:
        import subprocess
        params = subprocess.list2cmdline([os.path.abspath(sys.argv[0])] + sys.argv[1:])
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
        return ret > 32
    except Exception:
        return False


if __name__ == '__main__':
    freeze_support()
    # 本程序需管理员权限（模拟键鼠/任务计划）。非管理员则弹UAC以管理员身份重启自身。
    if not is_admin():
        if restart_as_admin():
            sys.exit(0)
        else:
            try:
                tkMessageBox.showerror("权限不足", "本程序需要管理员权限运行。\n请右键选择“以管理员身份运行”，或在UAC弹窗中点击“是”。")
            except Exception:
                pass
            sys.exit(1)
    frame_main()
