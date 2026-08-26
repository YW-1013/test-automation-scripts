# -*- coding: utf-8 -*-
"""
安卓锁屏密码解锁测试脚本 (PyQt6 UI)
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
from datetime import datetime
from locale import getpreferredencoding
from uiautomator2 import connect

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QTextEdit, QGroupBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor


# ══════════════════════════════════════════════════════════════
#  全局状态
# ══════════════════════════════════════════════════════════════
is_running = False
is_paused  = False
logger     = None


# ══════════════════════════════════════════════════════════════
#  日志 Handler（线程安全：通过 Qt 信号传到主线程）
# ══════════════════════════════════════════════════════════════
class _LogSignalEmitter(QObject):
    new_line = pyqtSignal(str)


class QtTextHandler(logging.Handler):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self._edit   = text_edit
        self._sig    = _LogSignalEmitter()
        self._sig.new_line.connect(self._append)

    def emit(self, record):
        self._sig.new_line.emit(self.format(record))

    def _append(self, msg: str):
        self._edit.append(msg)
        self._edit.moveCursor(QTextCursor.MoveOperation.End)


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


def get_logger(text_edit=None):
    lg = logging.getLogger('lockscreen_test')
    if lg.handlers:
        return lg
    lg.setLevel(logging.INFO)
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    ch = logging.StreamHandler(); ch.setFormatter(fmt); lg.addHandler(ch)
    fh = DailyDateFileHandler(os.path.join(script_dir, 'logs'), 'lockscreen_test')
    fh.setFormatter(fmt); lg.addHandler(fh)
    if text_edit:
        th = QtTextHandler(text_edit); th.setFormatter(fmt); lg.addHandler(th)
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
    for entry in get_adb_devices():
        if '\t' in entry:
            addr, status = entry.split('\t', 1)
            if device_ip in addr and status.strip() == 'device':
                return True
    return False


def adb(device_ip, *args):
    return run_cmd(['adb', '-s', f'{device_ip}:5555'] + list(args))


def get_screen_size(device_ip):
    output = adb(device_ip, 'shell', 'wm', 'size')
    try:
        part = output.strip().split(':')[-1].strip()
        w, h = map(int, part.split('x'))
        return w, h
    except Exception:
        return 2560, 1600


# ══════════════════════════════════════════════════════════════
#  拇指机器人
# ══════════════════════════════════════════════════════════════
def kill_process(name):
    try:
        subprocess.run(['taskkill', '/F', '/IM', name],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError:
        pass


def reopen_emulator(emu_ip, emu_process, emu_path, lg):
    lg.info("重启模拟器...")
    kill_process(emu_process)
    time.sleep(10)
    subprocess.Popen(emu_path)
    for _ in range(30):
        try:
            d = connect(emu_ip)
            if d(text="智能生活").exists() or d(text="向日葵远程控制").exists():
                lg.info("模拟器已就绪")
                return
        except Exception:
            pass
        time.sleep(5)
    lg.warning("模拟器重启后仍未就绪")


def ensure_emulator_ready(emu_ip, emu_process, emu_path, btn_name, lg):
    devices = get_adb_devices()
    status  = {e.split('\t')[0]: e.split('\t')[1] for e in devices if '\t' in e}
    if emu_ip not in status or status[emu_ip].strip() != 'device':
        run_cmd('adb disconnect')
        reopen_emulator(emu_ip, emu_process, emu_path, lg)

    while True:
        try:
            d = connect(emu_ip)
            h = d.info['displayHeight']
            w = d.info['displayWidth']
            if not d(text="智能生活").exists(timeout=5):
                d.app_stop_all()
                time.sleep(10)
                continue
            d(text="智能生活").click()
            for _ in range(6):
                if d(text=btn_name).exists(timeout=3):
                    break
                d.swipe(w/2, h*0.8, w/2, h*0.2)
                time.sleep(2)
            if d(text="空闲").exists(timeout=3) and d(text=btn_name).exists(timeout=3):
                return
        except Exception:
            lg.info(f"模拟器操作异常，重启\n{traceback.format_exc()}")
            reopen_emulator(emu_ip, emu_process, emu_path, lg)


def press_robot(emu_ip, emu_process, emu_path, btn_name, lg):
    ensure_emulator_ready(emu_ip, emu_process, emu_path, btn_name, lg)
    d = connect(emu_ip)
    lg.info("拇指机器人按键一次")
    if d(text="空闲").exists(timeout=5):
        d(text="空闲").click()


# ══════════════════════════════════════════════════════════════
#  解锁核心逻辑
# ══════════════════════════════════════════════════════════════
def wait_adb_with_wakeup(device_ip, emu_ip, emu_process, emu_path, btn_name,
                         lg, max_wait=120, press_interval=15):
    deadline   = time.time() + max_wait
    last_press = 0.0
    while time.time() < deadline:
        if not is_running:
            return False
        if is_device_online(device_ip):
            lg.info("设备 ADB 已连接（锁屏界面）")
            return True
        now = time.time()
        if now - last_press >= press_interval:
            lg.info("设备未响应（息屏中），按拇指机器人唤醒...")
            try:
                press_robot(emu_ip, emu_process, emu_path, btn_name, lg)
            except Exception:
                lg.warning(f"按键异常：{traceback.format_exc()}")
            last_press = now
        time.sleep(1)
    lg.warning(f"等待 ADB 连接超时（{max_wait}s）")
    return False


def swipe_to_show_pin(device_ip, lg):
    w, h = get_screen_size(device_ip)
    cx = w // 2
    adb(device_ip, 'shell', 'input', 'swipe',
        str(cx), str(int(h * 0.75)), str(cx), str(int(h * 0.25)), '300')
    lg.info("已上滑锁屏界面，等待 PIN 键盘出现")
    time.sleep(1.5)


def input_pin(device_ip, password, use_text_click, lg):
    lg.info(f"开始输入密码（方式：{'按文本' if use_text_click else 'adb input text'}）")
    if use_text_click:
        try:
            d = connect(device_ip)
            for digit in password:
                btn = d(text=digit)
                if btn.exists(timeout=3):
                    btn.click()
                    lg.info(f"  已点击数字 {digit}")
                    time.sleep(0.35)
                else:
                    lg.warning(f"未找到数字按键 '{digit}'，切换为 adb input text")
                    adb(device_ip, 'shell', 'input', 'text', password)
                    time.sleep(0.5)
                    break
        except Exception:
            lg.warning(f"uiautomator2 点击异常：{traceback.format_exc()}")
            adb(device_ip, 'shell', 'input', 'text', password)
            time.sleep(0.5)
    else:
        adb(device_ip, 'shell', 'input', 'text', password)
        time.sleep(0.5)
    adb(device_ip, 'shell', 'input', 'keyevent', '66')
    lg.info("已发送回车确认")
    time.sleep(2)


def check_unlocked(device_ip, lg):
    kw = run_cmd(f'adb -s {device_ip}:5555 shell "dumpsys window | grep -E mDreamingLockscreen"')
    if 'mDreamingLockscreen=false' in kw:
        lg.info("检查通过：keyguard 已关闭")
        return True
    act = run_cmd(f'adb -s {device_ip}:5555 shell "dumpsys activity activities | grep mResumedActivity"')
    if any(kw in act.lower() for kw in ['launcher', 'home', 'nexuslauncher']):
        lg.info("检查通过：Launcher 在前台")
        return True
    try:
        d = connect(device_ip)
        has_pin_pad  = d(resourceId='com.android.systemui:id/pinEntry').exists(timeout=2)
        has_keyguard = d(description='Keyguard').exists(timeout=1)
        if not has_pin_pad and not has_keyguard:
            lg.info("检查通过：锁屏元素不存在")
            return True
    except Exception:
        pass
    lg.info("判断：仍在锁屏界面，解锁失败")
    return False


def lock_screen_now(device_ip, lg):
    adb(device_ip, 'shell', 'input', 'keyevent', '26')
    lg.info("已发送电源键，屏幕即将息屏锁定")
    time.sleep(3)


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
    'max_wait':       '120',
    'press_interval': '15',
    'use_text_click': True,
}

def load_cfg():
    try:
        with open(CFG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULTS)

def save_cfg(data):
    with open(CFG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════
#  测试线程（QThread）
# ══════════════════════════════════════════════════════════════
class TestWorker(QObject):
    finished   = pyqtSignal()
    stat_update = pyqtSignal(int, int, int, int, int)   # i, total, pass, fail, skip

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

    def run(self):
        global is_running, is_paused
        cfg            = self.cfg
        device_ip      = cfg['device_ip']
        emu_ip         = cfg['emu_ip']
        emu_process    = cfg['emu_process']
        emu_path       = cfg['emu_path']
        btn_name       = cfg['btn_name']
        password       = cfg['password']
        test_count     = int(cfg['test_count'])
        max_wait       = int(cfg['max_wait'])
        press_interval = int(cfg['press_interval'])
        use_text_click = cfg['use_text_click']

        pass_cnt = fail_cnt = skip_cnt = 0
        run_cmd(f'adb connect {device_ip}')
        time.sleep(2)

        for i in range(1, test_count + 1):
            if not is_running:
                logger.info("测试已手动停止")
                break
            while is_paused:
                time.sleep(0.2)

            logger.info(f"{'='*10} 第 {i}/{test_count} 次测试 {'='*10}")
            self.stat_update.emit(i, test_count, pass_cnt, fail_cnt, skip_cnt)

            if is_device_online(device_ip):
                lock_screen_now(device_ip, logger)
            else:
                logger.info("设备已离线（已处于息屏状态），跳过锁屏步骤")

            connected = wait_adb_with_wakeup(
                device_ip, emu_ip, emu_process, emu_path, btn_name,
                logger, max_wait=max_wait, press_interval=press_interval
            )
            if not connected:
                logger.warning(f"第 {i} 次：ADB 等待超时，跳过本次")
                skip_cnt += 1
                continue

            time.sleep(1)
            swipe_to_show_pin(device_ip, logger)
            input_pin(device_ip, password, use_text_click, logger)

            if check_unlocked(device_ip, logger):
                pass_cnt += 1
                logger.info(f"第 {i} 次：解锁成功  [通过:{pass_cnt} 失败:{fail_cnt} 跳过:{skip_cnt}]")
            else:
                fail_cnt += 1
                logger.warning(f"第 {i} 次：解锁失败  [通过:{pass_cnt} 失败:{fail_cnt} 跳过:{skip_cnt}]")

            self.stat_update.emit(i, test_count, pass_cnt, fail_cnt, skip_cnt)
            time.sleep(1)

        total_done = pass_cnt + fail_cnt
        rate = f"{pass_cnt / total_done * 100:.1f}%" if total_done > 0 else "N/A"
        logger.info(f"测试结束 — 共执行 {total_done} 次，通过 {pass_cnt}，失败 {fail_cnt}，"
                    f"跳过 {skip_cnt}，通过率 {rate}")
        is_running = False
        self.finished.emit()


# ══════════════════════════════════════════════════════════════
#  主窗口
# ══════════════════════════════════════════════════════════════
STYLE = """
QMainWindow, QWidget#central {
    background-color: #F5F6FA;
}
QGroupBox {
    font-family: 微软雅黑;
    font-size: 13px;
    font-weight: bold;
    color: #2C3E50;
    border: 1px solid #D5D8DC;
    border-radius: 8px;
    margin-top: 10px;
    background-color: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2980B9;
}
QLabel#field_label {
    font-family: 微软雅黑;
    font-size: 11px;
    color: #555;
}
QLineEdit {
    font-family: Consolas;
    font-size: 11px;
    border: 1px solid #BDC3C7;
    border-radius: 5px;
    padding: 4px 8px;
    background: #FDFEFE;
    color: #2C3E50;
}
QLineEdit:focus {
    border: 1.5px solid #2980B9;
    background: #EBF5FB;
}
QCheckBox {
    font-family: 微软雅黑;
    font-size: 11px;
    color: #444;
    spacing: 6px;
}
QPushButton {
    font-family: 微软雅黑;
    font-size: 12px;
    font-weight: bold;
    border-radius: 6px;
    padding: 7px 20px;
    color: white;
}
QPushButton#btn_start {
    background-color: #2980B9;
    border: none;
}
QPushButton#btn_start:hover   { background-color: #3498DB; }
QPushButton#btn_start:pressed { background-color: #1F618D; }
QPushButton#btn_start:disabled { background-color: #AEB6BF; }
QPushButton#btn_stop {
    background-color: #C0392B;
    border: none;
}
QPushButton#btn_stop:hover    { background-color: #E74C3C; }
QPushButton#btn_stop:pressed  { background-color: #922B21; }
QPushButton#btn_stop:disabled { background-color: #AEB6BF; }
QPushButton#btn_pause {
    background-color: #D4A017;
    border: none;
}
QPushButton#btn_pause:hover   { background-color: #F1C40F; color: #2C3E50; }
QPushButton#btn_pause:pressed { background-color: #B7770D; }
QPushButton#btn_pause:disabled { background-color: #AEB6BF; }
QLabel#stat_label {
    font-family: 微软雅黑;
    font-size: 12px;
    font-weight: bold;
    color: #1F4E79;
    padding: 2px 0;
}
QTextEdit#log_view {
    font-family: Consolas;
    font-size: 9pt;
    background-color: #1E1E2E;
    color: #CDD6F4;
    border: none;
    border-radius: 6px;
    padding: 6px;
}
QScrollBar:vertical {
    width: 8px;
    background: #2A2A3E;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #585B70;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("安卓锁屏解锁测试")
        self.resize(800, 880)
        self._thread = None
        self._worker = None
        self._cfg    = load_cfg()
        self._build_ui()

    def _build_ui(self):
        central = QWidget(objectName="central")
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(8)

        # ── 配置区 ──
        cfg_box = QGroupBox("配置")
        cfg_grid = QGridLayout(cfg_box)
        cfg_grid.setContentsMargins(14, 18, 14, 14)
        cfg_grid.setHorizontalSpacing(12)
        cfg_grid.setVerticalSpacing(6)

        fields = [
            ('device_ip',      '被测设备 IP'),
            ('emu_ip',         '模拟器 ADB ID'),
            ('emu_process',    '模拟器进程名'),
            ('emu_path',       '模拟器路径'),
            ('btn_name',       '拇指机器人按键名'),
            ('password',       '锁屏密码'),
            ('test_count',     '测试次数'),
            ('max_wait',       '唤醒超时(秒)'),
            ('press_interval', '按键间隔(秒)'),
        ]
        self._entries = {}
        for row, (key, label) in enumerate(fields):
            lbl = QLabel(label, objectName="field_label")
            lbl.setFixedWidth(160)
            cfg_grid.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignVCenter)
            entry = QLineEdit(str(self._cfg.get(key, DEFAULTS.get(key, ''))))
            self._entries[key] = entry
            cfg_grid.addWidget(entry, row, 1)

        self._chk = QCheckBox("按数字文本点击（推荐；取消则用 adb input text）")
        self._chk.setChecked(bool(self._cfg.get('use_text_click', True)))
        cfg_grid.addWidget(self._chk, len(fields), 0, 1, 2)
        cfg_grid.setColumnStretch(1, 1)
        root_layout.addWidget(cfg_box)

        # ── 结果统计条 ──
        self._stat_lbl = QLabel("尚未开始", objectName="stat_label")
        root_layout.addWidget(self._stat_lbl)

        # ── 按钮区 ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self._btn_start = QPushButton("开始测试", objectName="btn_start")
        self._btn_stop  = QPushButton("停止",     objectName="btn_stop")
        self._btn_pause = QPushButton("暂停",     objectName="btn_pause")
        self._btn_stop.setEnabled(False)
        self._btn_pause.setEnabled(False)
        self._btn_start.setFixedSize(120, 38)
        self._btn_stop.setFixedSize(90,  38)
        self._btn_pause.setFixedSize(90,  38)
        self._btn_start.clicked.connect(self._on_start)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_pause.clicked.connect(self._on_pause)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_stop)
        btn_row.addWidget(self._btn_pause)
        btn_row.addStretch()
        root_layout.addLayout(btn_row)

        # ── 日志区 ──
        log_box = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_box)
        log_layout.setContentsMargins(8, 16, 8, 8)
        self._log_view = QTextEdit(objectName="log_view")
        self._log_view.setReadOnly(True)
        log_layout.addWidget(self._log_view)
        root_layout.addWidget(log_box, stretch=1)

        # 初始化 logger
        global logger
        logging.getLogger('lockscreen_test').handlers.clear()
        logger = get_logger(self._log_view)

    # ── 按钮回调 ──
    def _on_start(self):
        global is_running, is_paused, logger
        is_running = True
        is_paused  = False
        cfg = {k: e.text() for k, e in self._entries.items()}
        cfg['use_text_click'] = self._chk.isChecked()
        save_cfg(cfg)

        logging.getLogger('lockscreen_test').handlers.clear()
        logger = get_logger(self._log_view)

        self._btn_start.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._btn_pause.setEnabled(True)

        self._thread = QThread()
        self._worker = TestWorker(cfg)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_test_finished)
        self._worker.stat_update.connect(self._update_stat)
        self._thread.start()

    def _on_stop(self):
        global is_running
        is_running = False
        if logger:
            logger.info("正在停止，等待当前步骤完成...")
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._btn_pause.setEnabled(False)

    def _on_pause(self):
        global is_paused
        is_paused = not is_paused
        self._btn_pause.setText("继续" if is_paused else "暂停")
        if logger:
            logger.info("已暂停" if is_paused else "已继续")

    def _on_test_finished(self):
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._btn_pause.setEnabled(False)
        if self._thread:
            self._thread.quit()
            self._thread.wait()

    def _update_stat(self, i, total, p, f, s):
        done = p + f
        rate = f"{p / done * 100:.1f}%" if done > 0 else "-"
        self._stat_lbl.setText(
            f"进度  {i} / {total}    通过  {p}    失败  {f}    跳过  {s}    通过率  {rate}"
        )


# ══════════════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
