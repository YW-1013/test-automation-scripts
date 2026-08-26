# -*- coding: utf-8 -*-
"""
安卓锁屏密码解锁测试脚本
测试流程：
  1. 通过 adb 锁定屏幕（模拟息屏场景）
  2. 息屏后 ADB 断连 → 按拇指机器人唤醒设备
  3. 屏幕亮起 / ADB 重连 → 上滑解锁界面 → 按数字输入密码
  4. 验证是否成功进入系统桌面
  5. 统计通过率
"""

import subprocess
import logging
import sys
import os
import time
import threading
import json
import traceback
import shutil
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from locale import getpreferredencoding
from uiautomator2 import connect

# ── u2.jar 打包兼容处理 ───────────────────────────────────────────────
# PyInstaller 单文件模式下，资源解压到 _MEIPASS 临时目录；
# 系统维护任务可能清理旧临时目录，导致 jar 丢失。
# 首次运行时将 jar 备份到 exe 同目录，之后若 _MEIPASS 目录被清理则自动从备份恢复。
_exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
_U2JAR_STABLE = os.path.join(_exe_dir, '_u2jar_backup', 'u2.jar')

if hasattr(sys, '_MEIPASS'):
    _u2jar_src = os.path.join(sys._MEIPASS, 'uiautomator2', 'assets', 'u2.jar')
    if os.path.exists(_u2jar_src) and not os.path.exists(_U2JAR_STABLE):
        os.makedirs(os.path.dirname(_U2JAR_STABLE), exist_ok=True)
        shutil.copy2(_u2jar_src, _U2JAR_STABLE)


def _restore_u2jar_if_needed():
    if not hasattr(sys, '_MEIPASS'):
        return
    meipass_jar = os.path.join(sys._MEIPASS, 'uiautomator2', 'assets', 'u2.jar')
    if os.path.exists(meipass_jar):
        return
    if not os.path.exists(_U2JAR_STABLE):
        return
    os.makedirs(os.path.dirname(meipass_jar), exist_ok=True)
    shutil.copy2(_U2JAR_STABLE, meipass_jar)


def safe_u2_connect(ip):
    """打包环境下先确保 u2.jar 存在，再执行 connect。"""
    _restore_u2jar_if_needed()
    return connect(ip)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ══════════════════════════════════════════════════════════════
#  全局状态
# ══════════════════════════════════════════════════════════════
is_running = False
is_paused  = False
logger     = None
log_text   = None

# tkinter 控件引用（在 build_ui 里赋值）
start_button = stop_button = pause_button = None
result_var   = None


# ══════════════════════════════════════════════════════════════
#  日志
# ══════════════════════════════════════════════════════════════
class TextHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        def _append():
            self.widget.configure(state='normal')
            self.widget.insert(tk.END, msg + '\n')
            self.widget.configure(state='disabled')
            self.widget.see(tk.END)
        self.widget.after(0, _append)


class DailyDateFileHandler(logging.FileHandler):
    def __init__(self, log_dir, prefix, encoding='utf-8'):
        self.log_dir = log_dir
        self.prefix  = prefix
        self._cur    = datetime.now().strftime('%m-%d')
        os.makedirs(log_dir, exist_ok=True)
        super().__init__(os.path.join(log_dir, f'{prefix}_{self._cur}.log'), 'a', encoding)

    def emit(self, record):
        today = datetime.now().strftime('%m-%d')
        if today != self._cur:
            self._cur = today
            if self.stream:
                self.stream.flush(); self.stream.close(); self.stream = None
            self.baseFilename = os.path.abspath(
                os.path.join(self.log_dir, f'{self.prefix}_{today}.log'))
            self.stream = self._open()
        super().emit(record)


def get_logger(text_widget=None):
    lg = logging.getLogger('lockscreen_test')
    if lg.handlers:          # 防止重复添加
        return lg
    lg.setLevel(logging.INFO)
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    ch = logging.StreamHandler(); ch.setFormatter(fmt); lg.addHandler(ch)
    fh = DailyDateFileHandler(os.path.join(script_dir, 'logs'), 'lockscreen_test')
    fh.setFormatter(fmt); lg.addHandler(fh)
    if text_widget:
        th = TextHandler(text_widget); th.setFormatter(fmt); lg.addHandler(th)
    return lg


# ══════════════════════════════════════════════════════════════
#  ADB 工具
# ══════════════════════════════════════════════════════════════
def run_cmd(cmd):
    proc = subprocess.Popen(
        cmd, bufsize=10000,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    out, _ = proc.communicate()
    try: proc.kill()
    except OSError: pass
    return out.decode(getpreferredencoding(), errors='ignore')


def get_adb_devices():
    output = run_cmd('adb devices')
    return [l.strip() for l in output.strip().split('\n')[1:] if l.strip()]


def is_device_online(device_ip):
    """检查设备 ADB 是否处于 device（在线）状态"""
    for entry in get_adb_devices():
        if '\t' in entry:
            addr, status = entry.split('\t', 1)
            if device_ip in addr and status.strip() == 'device':
                return True
    return False


def adb(device_ip, *args):
    """对 device_ip 执行 adb 命令，自动加 -s"""
    return run_cmd(['adb', '-s', f'{device_ip}:5555'] + list(args))


def get_screen_size(device_ip):
    """返回 (width, height)，默认 2560x1600"""
    output = adb(device_ip, 'shell', 'wm', 'size')
    try:
        part = output.strip().split(':')[-1].strip()
        w, h = map(int, part.split('x'))
        return w, h
    except Exception:
        return 2560, 1600


# ══════════════════════════════════════════════════════════════
#  拇指机器人（对齐主脚本 home_on / common_to_home_on 逻辑）
# ══════════════════════════════════════════════════════════════
def kill_process(name):
    try:
        subprocess.run(['taskkill', '/F', '/IM', name],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError:
        pass


def _reopen_emulator(emu_ip, emu_process, emu_path, logger):
    """杀掉模拟器进程并重新启动，等待智能生活桌面出现"""
    logger.info("杀掉模拟器进程")
    kill_process(emu_process)
    time.sleep(10)
    logger.info("重新打开模拟器")
    subprocess.Popen(emu_path)
    for _ in range(30):
        try:
            d = safe_u2_connect(emu_ip)
            if d(text="智能生活").exists() or d(text="向日葵远程控制").exists():
                logger.info("模拟器已就绪")
                return
        except Exception:
            logger.info("还未连接模拟器")
        time.sleep(5)
    logger.warning("模拟器重启后仍未就绪")


def _ensure_emulator_connected(emu_ip, emu_process, emu_path, logger):
    """确保模拟器 ADB 处于 device 状态，否则重启"""
    devices = get_adb_devices()
    status  = {e.split('\t')[0]: e.split('\t')[1] for e in devices if '\t' in e}
    while emu_ip not in status or status[emu_ip].strip() != 'device':
        run_cmd('adb disconnect')
        _reopen_emulator(emu_ip, emu_process, emu_path, logger)
        devices = get_adb_devices()
        status  = {e.split('\t')[0]: e.split('\t')[1] for e in devices if '\t' in e}


def _navigate_to_device_panel(emu_ip, btn_name, logger):
    """
    对齐 common_to_home_on：
    循环直到 "空闲" 和 btn_name 同时可见：
      1. 若 "智能生活" 不可见 → stop_all_apps + 等待15s
      2. 点击 "智能生活"
      3. 滑动寻找 btn_name（最多5次）
      4. 点击 btn_name 进入设备控制页
      5. 等待20秒让控制页加载
    """
    d = safe_u2_connect(emu_ip)
    h = d.info['displayHeight']
    w = d.info['displayWidth']

    while (d(text="空闲").exists(timeout=5) is False
           or d(text=btn_name).exists(timeout=5) is False):

        # 确保 智能生活 在前台
        while d(text="智能生活").exists(timeout=5) is False:
            logger.info("智能生活未找到，关闭所有应用等待桌面就绪")
            d.app_stop_all()
            time.sleep(15)

        logger.info("点击智能生活")
        d(text="智能生活").click()

        # 滑动寻找设备按键
        recheck = 0
        while d(text=btn_name).exists(timeout=5) is False:
            d.swipe(w / 2, h * 0.8, w / 2, h * 0.2)
            time.sleep(2)
            recheck += 1
            if recheck > 5:
                break

        logger.info(f"点击设备 {btn_name}")
        d(text=btn_name).click()
        logger.info("等待设备控制页加载（20s）")
        time.sleep(20)


def press_robot(emu_ip, emu_process, emu_path, btn_name, logger):
    """
    对齐 home_on：
    1. 确保模拟器 ADB 在线
    2. 导航到设备控制页（_navigate_to_device_panel）
    3. 点击 "空闲" 触发按键
    """
    _ensure_emulator_connected(emu_ip, emu_process, emu_path, logger)
    try:
        _navigate_to_device_panel(emu_ip, btn_name, logger)
    except Exception:
        logger.info(f"导航异常，重启模拟器后重试\n{traceback.format_exc()}")
        _reopen_emulator(emu_ip, emu_process, emu_path, logger)
        _ensure_emulator_connected(emu_ip, emu_process, emu_path, logger)
        _navigate_to_device_panel(emu_ip, btn_name, logger)

    d = safe_u2_connect(emu_ip)
    logger.info("拇指机器人按键一次")
    if d(text="空闲").exists(timeout=5):
        d(text="空闲").click()


# ══════════════════════════════════════════════════════════════
#  解锁核心逻辑
# ══════════════════════════════════════════════════════════════
def wait_adb_with_wakeup(device_ip, emu_ip, emu_process, emu_path, btn_name,
                         logger, max_attempts=20):
    """
    最多按 max_attempts 次拇指机器人。
    每次按键后立即密集重连：每 0.5 秒调一次 adb connect + 状态检测，
    连续 16 次（约 8 秒）覆盖完整的屏幕唤醒窗口。
    返回 True = ADB 已连接，False = 全部次数耗尽仍未连接
    """
    # 先主动连一次，有可能本来就在线
    run_cmd(f'adb connect {device_ip}:5555')
    time.sleep(0.5)
    if is_device_online(device_ip):
        logger.info("设备 ADB 已连接（无需唤醒）")
        return True

    for press_num in range(1, max_attempts + 1):
        if not is_running:
            return False

        logger.info(f"按拇指机器人唤醒（第 {press_num}/{max_attempts} 次）...")
        try:
            press_robot(emu_ip, emu_process, emu_path, btn_name, logger)
        except Exception:
            logger.warning(f"按键异常：{traceback.format_exc()}")

        # 按键后立即密集检测（16 次 × 0.5 s ≈ 8 s，覆盖唤醒窗口）
        logger.info("已按键，立即尝试 ADB 连接...")
        for quick in range(1, 17):
            if not is_running:
                return False
            run_cmd(f'adb connect {device_ip}:5555')
            if is_device_online(device_ip):
                logger.info(f"ADB 已连接（第 {press_num} 次唤醒后第 {quick} 次检测）")
                return True
            time.sleep(0.5)

        logger.info(f"第 {press_num} 次唤醒后 8s 内未连接，继续重试")

    logger.warning(f"ADB 连接失败，已按键 {max_attempts} 次")
    return False


def swipe_to_show_pin(device_ip, logger):
    """
    锁屏界面可能先显示时钟页，需要上滑才出现 PIN 输入框。
    执行一次上滑手势。
    """
    w, h = get_screen_size(device_ip)
    cx = w // 2
    adb(device_ip, 'shell', 'input', 'swipe',
        str(cx), str(int(h * 0.75)), str(cx), str(int(h * 0.25)), '300')
    logger.info("已上滑锁屏界面，等待 PIN 键盘出现")
    time.sleep(1.5)


def input_pin(device_ip, password, use_text_click, logger):
    """
    输入 PIN 密码。
    use_text_click=True  → uiautomator2 找数字文本按钮点击（推荐）
    use_text_click=False → adb input text 直接发送（备用，部分系统有效）
    """
    logger.info(f"开始输入密码（方式：{'按文本' if use_text_click else 'adb input text'}）")
    if use_text_click:
        try:
            d = safe_u2_connect(device_ip)
            for digit in password:
                btn = d(text=digit)
                if btn.exists(timeout=3):
                    btn.click()
                    logger.info(f"  已点击数字 {digit}")
                    time.sleep(0.35)
                else:
                    # 数字按键找不到，回退 adb input text
                    logger.warning(f"未找到数字按键 '{digit}'，切换为 adb input text")
                    adb(device_ip, 'shell', 'input', 'text', password)
                    time.sleep(0.5)
                    break
        except Exception:
            logger.warning(f"uiautomator2 点击异常：{traceback.format_exc()}")
            adb(device_ip, 'shell', 'input', 'text', password)
            time.sleep(0.5)
    else:
        adb(device_ip, 'shell', 'input', 'text', password)
        time.sleep(0.5)

    # 发送回车确认
    adb(device_ip, 'shell', 'input', 'keyevent', '66')
    logger.info("已发送回车确认")
    time.sleep(2)


def check_unlocked(device_ip, logger):
    """
    判断是否已离开锁屏进入桌面。
    多种方法互补，任意一种命中即判为成功。
    """
    # 方法1：keyguard 状态
    kw = run_cmd(f'adb -s {device_ip}:5555 shell "dumpsys window | grep -E mDreamingLockscreen"')
    if 'mDreamingLockscreen=false' in kw:
        logger.info("检查通过：keyguard 已关闭")
        return True

    # 方法2：前台 Activity 是否为 Launcher
    act = run_cmd(f'adb -s {device_ip}:5555 shell "dumpsys activity activities | grep mResumedActivity"')
    if any(kw in act.lower() for kw in ['launcher', 'home', 'nexuslauncher']):
        logger.info("检查通过：Launcher 在前台")
        return True

    # 方法3：uiautomator2 检查锁屏元素是否消失
    try:
        d = safe_u2_connect(device_ip)
        # 锁屏下通常能找到 PIN 键盘或 keyguard 相关元素
        has_pin_pad  = d(resourceId='com.android.systemui:id/pinEntry').exists(timeout=2)
        has_keyguard = d(description='Keyguard').exists(timeout=1)
        if not has_pin_pad and not has_keyguard:
            logger.info("检查通过：锁屏元素不存在")
            return True
    except Exception:
        pass

    logger.info("判断：仍在锁屏界面，解锁失败")
    return False


def lock_screen_now(device_ip, logger):
    """通过电源键事件锁定屏幕（息屏）"""
    adb(device_ip, 'shell', 'input', 'keyevent', '26')
    logger.info("已发送电源键，屏幕即将息屏锁定")
    time.sleep(3)   # 等待息屏和 ADB 断连


# ══════════════════════════════════════════════════════════════
#  主测试循环
# ══════════════════════════════════════════════════════════════
def run_test(cfg):
    global is_running, is_paused

    device_ip      = cfg['device_ip']
    emu_ip         = cfg['emu_ip']
    emu_process    = cfg['emu_process']
    emu_path       = cfg['emu_path']
    btn_name       = cfg['btn_name']
    password       = cfg['password']
    test_count     = int(cfg['test_count'])
    max_attempts   = int(cfg['max_attempts'])
    use_text_click = cfg['use_text_click']

    pass_cnt = fail_cnt = 0
    MAX_UNLOCK_RETRY = 10

    for i in range(1, test_count + 1):
        if not is_running:
            logger.info("测试已手动停止")
            break
        while is_paused:
            time.sleep(0.2)

        logger.info(f"{'='*10} 第 {i}/{test_count} 次测试 {'='*10}")
        _update_result(i, test_count, pass_cnt, fail_cnt)

        # ── 步骤1：先按一次拇指机器人（处理设备可能已处于锁屏/息屏状态）──
        logger.info("步骤1：按拇指机器人唤醒屏幕...")
        try:
            press_robot(emu_ip, emu_process, emu_path, btn_name, logger)
        except Exception:
            logger.warning(f"按键异常：{traceback.format_exc()}")

        # ── 步骤2：连接 ADB，最多 max_attempts 次，连不上算失败 ──
        connected = wait_adb_with_wakeup(
            device_ip, emu_ip, emu_process, emu_path, btn_name,
            logger, max_attempts=max_attempts
        )
        if not connected:
            fail_cnt += 1
            logger.warning(f"第 {i} 次：❌ ADB {max_attempts} 次均未连接，判为失败"
                           f"  [通过:{pass_cnt} 失败:{fail_cnt}]")
            _update_result(i, test_count, pass_cnt, fail_cnt)
            continue

        # ── 步骤3：锁定屏幕 ──
        lock_screen_now(device_ip, logger)

        # ── 步骤4：锁屏后立即按一次拇指机器人唤醒 ──
        logger.info("步骤4：锁屏后立即按拇指机器人唤醒屏幕...")
        try:
            press_robot(emu_ip, emu_process, emu_path, btn_name, logger)
        except Exception:
            logger.warning(f"按键异常：{traceback.format_exc()}")

        # ── 步骤5：等待 ADB 重连，最多 max_attempts 次 ──
        connected = wait_adb_with_wakeup(
            device_ip, emu_ip, emu_process, emu_path, btn_name,
            logger, max_attempts=max_attempts
        )
        if not connected:
            fail_cnt += 1
            logger.warning(f"第 {i} 次：❌ 锁屏后 ADB {max_attempts} 次均未连接，判为失败"
                           f"  [通过:{pass_cnt} 失败:{fail_cnt}]")
            _update_result(i, test_count, pass_cnt, fail_cnt)
            continue

        # ── 步骤6-7：尝试解锁，失败则重试，最多 MAX_UNLOCK_RETRY 次 ──
        unlocked = False
        for attempt in range(1, MAX_UNLOCK_RETRY + 1):
            if not is_running:
                break
            # 如果重试期间屏幕再次熄灭，先重新唤醒
            if not is_device_online(device_ip):
                logger.info(f"  第 {attempt} 次解锁前设备已离线，重新唤醒...")
                reconnected = wait_adb_with_wakeup(
                    device_ip, emu_ip, emu_process, emu_path, btn_name,
                    logger, max_attempts=max_attempts
                )
                if not reconnected:
                    logger.warning("  重新唤醒失败，放弃本轮剩余重试")
                    break
            time.sleep(0.5)
            swipe_to_show_pin(device_ip, logger)
            input_pin(device_ip, password, use_text_click, logger)
            if check_unlocked(device_ip, logger):
                unlocked = True
                break
            logger.warning(f"  第 {attempt}/{MAX_UNLOCK_RETRY} 次解锁尝试失败，继续重试...")
            time.sleep(1)

        if unlocked:
            pass_cnt += 1
            logger.info(f"第 {i} 次：✅ 解锁成功  [通过:{pass_cnt} 失败:{fail_cnt}]")
        else:
            fail_cnt += 1
            logger.warning(f"第 {i} 次：❌ 解锁失败（重试 {MAX_UNLOCK_RETRY} 次均未成功）"
                           f"  [通过:{pass_cnt} 失败:{fail_cnt}]")

        _update_result(i, test_count, pass_cnt, fail_cnt)
        time.sleep(1)

    total_done = pass_cnt + fail_cnt
    rate = f"{pass_cnt / total_done * 100:.1f}%" if total_done > 0 else "N/A"
    logger.info(f"测试结束 — 共执行 {total_done} 次，通过 {pass_cnt}，失败 {fail_cnt}，通过率 {rate}")
    is_running = False
    if start_button:
        start_button.after(0, lambda: start_button.configure(state="normal"))
    if stop_button:
        stop_button.after(0, lambda: stop_button.configure(state="disabled"))
    if pause_button:
        pause_button.after(0, lambda: pause_button.configure(state="disabled"))


def _update_result(i, total, p, f):
    if result_var:
        done = p + f
        rate = f"{p / done * 100:.1f}%" if done > 0 else "-"
        result_var.set(f"进度 {i}/{total}   通过 {p}   失败 {f}   通过率 {rate}")


# ══════════════════════════════════════════════════════════════
#  配置存取
# ══════════════════════════════════════════════════════════════
CFG_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config_lockscreen.json')

DEFAULTS = {
    'device_ip':      '192.168.1.100',
    'emu_ip':         'emulator-5554',
    'emu_process':    'dnplayer.exe',
    'emu_path':       r'C:\leidian\LDPlayer9\dnplayer.exe',
    'btn_name':       'MegaBook键盘',
    'password':       '123456',
    'test_count':     '50',
    'max_attempts':   '20',
    'use_text_click': True,
}

def load_cfg():
    try:
        with open(CFG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 补充缺失的 key
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULTS)

def save_cfg(data):
    with open(CFG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════
#  UI
# ══════════════════════════════════════════════════════════════
def build_ui():
    global logger, log_text, start_button, stop_button, pause_button, result_var

    root = ctk.CTk()
    root.title("安卓锁屏解锁测试")
    root.geometry("780x860")
    root.resizable(True, True)

    cfg = load_cfg()

    # ── 顶部：配置区 ──
    frm_cfg = ctk.CTkFrame(root, corner_radius=10)
    frm_cfg.pack(fill=tk.X, padx=14, pady=(14, 4))

    ctk.CTkLabel(frm_cfg, text="配置",
                 font=ctk.CTkFont(family='微软雅黑', size=13, weight='bold'),
                 anchor='w').grid(row=0, column=0, columnspan=2,
                                  sticky=tk.W, padx=12, pady=(10, 4))

    fields = [
        ('device_ip',      '被测设备 IP'),
        ('emu_ip',         '模拟器 ADB ID'),
        ('emu_process',    '模拟器进程名'),
        ('emu_path',       '模拟器路径'),
        ('btn_name',       '拇指机器人按键名'),
        ('password',       '锁屏密码'),
        ('test_count',     '测试次数'),
        ('max_attempts',   'ADB连接尝试次数(次)'),
    ]
    vars_ = {}
    lbl_font = ctk.CTkFont(family='微软雅黑', size=11)
    for row_idx, (key, label) in enumerate(fields, start=1):
        ctk.CTkLabel(frm_cfg, text=label, font=lbl_font, anchor='w', width=160).grid(
            row=row_idx, column=0, sticky=tk.W, pady=4, padx=(12, 6))
        v = tk.StringVar(value=str(cfg.get(key, DEFAULTS.get(key, ''))))
        vars_[key] = v
        ctk.CTkEntry(frm_cfg, textvariable=v, width=400,
                     font=ctk.CTkFont(family='Consolas', size=11)).grid(
            row=row_idx, column=1, sticky=tk.EW, pady=4, padx=(0, 12))

    use_text_var = tk.BooleanVar(value=bool(cfg.get('use_text_click', True)))
    vars_['use_text_click'] = use_text_var
    ctk.CTkCheckBox(frm_cfg,
                    text="按数字文本点击（推荐；取消则用 adb input text）",
                    font=ctk.CTkFont(family='微软雅黑', size=11),
                    variable=use_text_var).grid(
        row=len(fields) + 1, column=0, columnspan=2,
        sticky=tk.W, pady=(6, 12), padx=12)
    frm_cfg.columnconfigure(1, weight=1)

    # ── 结果统计条 ──
    result_var = tk.StringVar(value="尚未开始")
    frm_stat = ctk.CTkFrame(root, fg_color="transparent")
    frm_stat.pack(fill=tk.X, padx=14, pady=2)
    ctk.CTkLabel(frm_stat, textvariable=result_var,
                 font=ctk.CTkFont(family='微软雅黑', size=12, weight='bold'),
                 text_color=("#1F4E79", "#5BC0F8"),
                 anchor='w').pack(side=tk.LEFT, pady=4)

    # ── 按钮区 ──
    frm_btn = ctk.CTkFrame(root, fg_color="transparent")
    frm_btn.pack(fill=tk.X, padx=14, pady=(2, 6))

    def on_start():
        global is_running, is_paused, logger
        is_running = True
        is_paused  = False
        c = {k: (v.get() if isinstance(v, tk.StringVar) else v.get())
             for k, v in vars_.items()}
        c['use_text_click'] = bool(use_text_var.get())
        save_cfg(c)
        logging.getLogger('lockscreen_test').handlers.clear()
        logger = get_logger(log_text)
        start_button.configure(state="disabled")
        stop_button.configure(state="normal")
        pause_button.configure(state="normal")
        threading.Thread(target=run_test, args=(c,), daemon=True).start()

    def on_stop():
        global is_running
        is_running = False
        if logger:
            logger.info("正在停止，等待当前步骤完成...")
        start_button.configure(state="normal")
        stop_button.configure(state="disabled")
        pause_button.configure(state="disabled")

    def on_pause():
        global is_paused
        is_paused = not is_paused
        pause_button.configure(text="继续" if is_paused else "暂停")
        if logger:
            logger.info("已暂停" if is_paused else "已继续")

    btn_font = ctk.CTkFont(family='微软雅黑', size=12, weight='bold')
    start_button = ctk.CTkButton(frm_btn, text="开始测试", command=on_start,
                                  width=120, height=36, font=btn_font)
    stop_button  = ctk.CTkButton(frm_btn, text="停止", command=on_stop,
                                  width=88, height=36, font=btn_font,
                                  state="disabled",
                                  fg_color="#C0392B", hover_color="#E74C3C")
    pause_button = ctk.CTkButton(frm_btn, text="暂停", command=on_pause,
                                  width=88, height=36, font=btn_font,
                                  state="disabled",
                                  fg_color="#B7770D", hover_color="#D4A017")
    start_button.pack(side=tk.LEFT, padx=(0, 8))
    stop_button.pack(side=tk.LEFT, padx=(0, 8))
    pause_button.pack(side=tk.LEFT)

    # ── 日志区 ──
    frm_log = ctk.CTkFrame(root, corner_radius=10)
    frm_log.pack(fill=tk.BOTH, expand=True, padx=14, pady=(4, 14))
    ctk.CTkLabel(frm_log, text="运行日志",
                 font=ctk.CTkFont(family='微软雅黑', size=12, weight='bold'),
                 anchor='w').pack(fill=tk.X, padx=12, pady=(8, 2))
    log_text = ctk.CTkTextbox(frm_log,
                               font=ctk.CTkFont(family='Consolas', size=9),
                               state='disabled', wrap='word')
    log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 10))

    logger = get_logger()
    root.mainloop()


if __name__ == '__main__':
    build_ui()
