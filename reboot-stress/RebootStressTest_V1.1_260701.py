# -*- coding: utf-8 -*-
"""
2026-6-16：
1、新增光感传感器检测（check_light_sensor），通过 PowerShell WinRT 读取 ALS 数值，
   ≤10 lux 判为异常（覆盖自动亮度读数归零 bug），新增配置项"光感检测（是/否）"
2、传感器不存在（NO_SENSOR）、无法读取（NO_READING）及输出无法解析均视为异常（不再跳过）
3、配置区 UI 改版：充电检测/异常时停止/光感检测改为下拉选项框（CTkOptionMenu）；
   U盘卷标/外接显示器/蓝牙设备改为多选下拉弹窗，打开时自动刷新当前设备列表，支持复选框多选
2026-6-12：
1、修复蓝牙检测：改为 PowerShell Get-PnpDevice 按 InstanceId 前缀（BTHENUM/BTHHFENUM/BTHLE）
   枚举蓝牙设备，FriendlyName 与设备管理器一致，可识别已配对的 HID/音频等外设
2、新增充电状态检测（check_charging），配置项"充电检测（跳过/充电中/未充电）"
3、新增异常停止选项（stop_on_error），检测失败时可选择停止压测不再重启
4、事件日志改为仅记录不计入失败结果（EventID 10111/10120 等为正常开机行为）
2026-6-10：
1、初始版本
检测项：
  1.  驱动异常检测（WMI ConfigManagerErrorCode != 0）
  2.  系统事件日志 Critical 级别事件检测（仅记录，不计失败）
  3.  关键系统服务运行状态检测
  4.  充电状态检测（可选）
  5.  光感传感器检测（可选，输入光感阈值 lux，0=跳过，低于阈值为异常）
  6.  外接 U 盘识别检测（按卷标名称）
  7.  外接显示器识别检测（按设备名称）
  8.  蓝牙设备识别检测（按设备名称）
"""
import os
import sys
import time
import json
import subprocess
import threading
import logging
import traceback
import ctypes
import psutil
import wmi
import pythoncom
import win32com.client
import tkinter as tk
import tkinter.messagebox
from datetime import datetime
from multiprocessing import freeze_support
import customtkinter as ctk

# ── 版本号（统一修改处）──────────────────────────────────────────
VERSION       = 'RebootStressTest_V1.1_260701'
EXE_NAME      = f'{VERSION}.exe'
TASK_NAME     = 'RebootStressTest_AutoStart'
STATE_FILE    = 'reboot_test_state.json'
# ─────────────────────────────────────────────────────────────────

# 需要检测的关键服务（Windows 服务名）
REQUIRED_SERVICES = [
    'AudioSrv',   # Windows Audio
    'Power',      # Power
    'Themes',     # Themes
]

WMI_ERROR_CODES = {
    1:  '配置错误',           2:  '未分配资源',         3:  '筛选器驱动加载失败',
    4:  '驱动加载失败',       5:  '注册表损坏',         6:  '需要重启',
    7:  '部分配置失败',       8:  '未签名驱动',         9:  '未知设备',
    10: '需要重新启动',       11: '配置冲突',           12: '需要进一步配置',
    13: '硬件不存在',         14: '驱动加载失败',       16: '已禁用',
    18: '未找到驱动',         22: '驱动程序未安装',     24: '需要重新安装驱动',
    28: '设备被阻止',         31: '需要用户干预',
}

file_path  = os.path.dirname(os.path.realpath(sys.argv[0]))
log_path   = os.path.join(file_path, 'logs')
state_path = os.path.join(file_path, STATE_FILE)
exe_path   = os.path.join(file_path, EXE_NAME)




is_running   = True
root         = None
logger       = None
start_button = None
stop_button  = None
count_var    = None
fail_var     = None
status_var   = None


# ── 日志 ─────────────────────────────────────────────────────────

class TextHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        # CTkTextbox 将底层 tk.Text 暴露在 _textbox 属性；tk.Text 则直接使用自身
        self._inner = getattr(widget, '_textbox', widget)

    def emit(self, record):
        msg = self.format(record)
        def _append():
            self.widget.configure(state='normal')
            self.widget.insert('end', msg + '\n')
            self.widget.configure(state='disabled')
            self._inner.see('end')
        self.widget.after(0, _append)


def get_logger(text_widget=None):
    os.makedirs(log_path, exist_ok=True)
    _logger = logging.getLogger('reboot_stress')
    _logger.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    date_str = datetime.now().strftime('%m-%d')
    fh = logging.FileHandler(
        os.path.join(log_path, f'reboot_stress_{date_str}.log'), encoding='utf-8'
    )
    fh.setFormatter(fmt)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    _logger.addHandler(fh)
    _logger.addHandler(ch)
    if text_widget:
        th = TextHandler(text_widget)
        th.setFormatter(fmt)
        _logger.addHandler(th)
    return _logger


# ── 状态持久化（跨重启）────────────────────────────────────────────

def load_state():
    default = {
        'test_count': 0, 'fail_count': 0,
        'is_test_running': False, 'failures': [], 'config': {}
    }
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_state(state):
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ── 任务计划（开机自启动）─────────────────────────────────────────

_TASK_XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT{delay}S</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{user}</UserId>
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
      <Command>{cmd}</Command>
      <Arguments></Arguments>
      <WorkingDirectory>{wd}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""


def create_startup_task(delay_seconds):
    try:
        user   = os.getlogin()
        xml    = _TASK_XML.format(delay=delay_seconds, user=user, cmd=exe_path, wd=file_path)
        svc    = win32com.client.Dispatch('Schedule.Service')
        svc.Connect()
        folder = svc.GetFolder('\\')
        task   = svc.NewTask(0)
        task.XmlText = xml
        folder.RegisterTaskDefinition(TASK_NAME, task, 6, user, None, 3)
        logger.info(f'开机自启动任务已注册：{TASK_NAME}（延时 {delay_seconds}s）')
    except Exception:
        logger.error(f'注册任务失败：{traceback.format_exc()}')


def delete_startup_task():
    try:
        svc    = win32com.client.Dispatch('Schedule.Service')
        svc.Connect()
        folder = svc.GetFolder('\\')
        try:
            folder.GetTask(TASK_NAME)
            folder.DeleteTask(TASK_NAME, 0)
            logger.info(f'开机自启动任务已删除：{TASK_NAME}')
        except Exception:
            pass
    except Exception:
        logger.error(f'删除任务失败：{traceback.format_exc()}')


# ── 检测函数 ──────────────────────────────────────────────────────

def check_drivers():
    """检测1：驱动异常（WMI ConfigManagerErrorCode != 0）"""
    try:
        c = wmi.WMI()
        abnormal = []
        for code, reason in WMI_ERROR_CODES.items():
            for dev in c.Win32_PnPEntity(ConfigManagerErrorCode=code):
                if dev.Description:
                    abnormal.append(f'{dev.Description}（{reason}）')
        if abnormal:
            logger.info(f'[驱动] ✗ 异常设备 {len(abnormal)} 个：{"；".join(abnormal)}')
            return False, abnormal
        logger.info('[驱动] ✓ 全部正常')
        return True, []
    except Exception:
        logger.error(f'[驱动] 执行异常：{traceback.format_exc()}')
        return False, ['驱动检测执行异常']


def check_event_log():
    """事件日志仅记录，不计入检测结果。"""
    try:
        boot_dt = datetime.fromtimestamp(psutil.boot_time())
        minutes = max(1, int((datetime.now() - boot_dt).total_seconds() / 60) + 2)
        ps_cmd = (
            f'$t=(Get-Date).AddMinutes(-{minutes});'
            f'Get-WinEvent -FilterHashtable @{{LogName="System";Level=1;StartTime=$t}}'
            f' -ErrorAction SilentlyContinue'
            f' | Select-Object -First 20 TimeCreated,Id,ProviderName'
            f' | ConvertTo-Json -Compress'
        )
        result = subprocess.run(
            ['powershell', '-NonInteractive', '-Command', ps_cmd],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        out = result.stdout.strip()
        if not out or out.lower() in ('null', ''):
            logger.info('[事件日志] 无 Critical 级别事件')
        else:
            events = json.loads(out)
            if isinstance(events, dict):
                events = [events]
            for e in events:
                logger.info(f'[事件日志] 仅记录 EventID={e.get("Id","?")} '
                            f'来源={e.get("ProviderName","?")} '
                            f'时间={e.get("TimeCreated","?")}')
    except Exception:
        logger.warning(f'[事件日志] 查询异常：{traceback.format_exc()}')
    return True, []  # 永远不计为失败


def check_services():
    """检测3：关键系统服务是否处于运行状态"""
    try:
        stopped = []
        for svc_name in REQUIRED_SERVICES:
            try:
                status = psutil.win_service_get(svc_name).status()
                if status != 'running':
                    stopped.append(f'{svc_name}（{status}）')
            except Exception:
                stopped.append(f'{svc_name}（未找到）')
        if stopped:
            logger.info(f'[服务] ✗ 异常：{"；".join(stopped)}')
            return False, stopped
        logger.info('[服务] ✓ 全部运行中')
        return True, []
    except Exception:
        logger.error(f'[服务] 执行异常：{traceback.format_exc()}')
        return False, ['服务检测执行异常']


def check_usb_drives(u_disk_names_str):
    """检测7：外接 U 盘识别。u_disk_names_str 为逗号分隔的卷标，空字符串则跳过。
    通过 WMI Win32_LogicalDisk（DriveType=2，可移动磁盘）匹配卷标名称。"""
    names = [n.strip() for n in u_disk_names_str.split(',') if n.strip()]
    if not names:
        logger.info('[U盘] 未配置，跳过')
        return True, []
    try:
        c       = wmi.WMI()
        present = {disk.VolumeName for disk in c.Win32_LogicalDisk(DriveType=2) if disk.VolumeName}
        logger.info(f'[U盘] 当前识别到：{list(present) if present else "无"}')
        missing = [n for n in names if n not in present]
        if missing:
            logger.info(f'[U盘] ✗ 未识别：{"；".join(missing)}')
            return False, [f'U盘未识别：{n}' for n in missing]
        logger.info('[U盘] ✓ 全部识别')
        return True, []
    except Exception:
        logger.error(f'[U盘] 执行异常：{traceback.format_exc()}')
        return False, ['U盘检测执行异常']


def check_external_monitor(monitor_names_str):
    """检测5：外接显示器识别。monitor_names_str 为逗号分隔的设备名称，空字符串则跳过。
    通过 PowerShell Get-PnpDevice 获取已识别的显示器名称列表，做子串匹配。"""
    names = [n.strip() for n in monitor_names_str.split(',') if n.strip()]
    if not names:
        logger.info('[显示器] 未配置，跳过')
        return True, []
    try:
        ps_cmd = (
            'Get-PnpDevice -Class Monitor -Status OK'
            ' -ErrorAction SilentlyContinue'
            ' | Select-Object -ExpandProperty FriendlyName'
            ' | ConvertTo-Json -Compress'
        )
        result = subprocess.run(
            ['powershell', '-NonInteractive', '-Command', ps_cmd],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        out = result.stdout.strip()
        if not out or out.lower() == 'null':
            current = []
        else:
            parsed  = json.loads(out)
            current = [parsed] if isinstance(parsed, str) else (parsed or [])
        logger.info(f'[显示器] 当前识别：{current if current else "无"}')
        missing = [n for n in names if not any(n in c for c in current)]
        if missing:
            logger.info(f'[显示器] ✗ 未识别：{"；".join(missing)}')
            return False, [f'显示器未识别：{n}' for n in missing]
        logger.info('[显示器] ✓ 全部识别')
        return True, []
    except Exception:
        logger.error(f'[显示器] 执行异常：{traceback.format_exc()}')
        return False, ['显示器检测执行异常']


def check_bluetooth(bt_names_str):
    """检测6：蓝牙设备识别。bt_names_str 为逗号分隔的设备名称，空字符串则跳过。
    通过 PowerShell Get-PnpDevice 按 InstanceId 前缀（BTHENUM/BTHHFENUM/BTHLE）
    枚举所有蓝牙设备，FriendlyName 与设备管理器完全一致。"""
    names = [n.strip() for n in bt_names_str.split(',') if n.strip()]
    if not names:
        logger.info('[蓝牙] 未配置，跳过')
        return True, []
    try:
        ps_cmd = (
            'Get-PnpDevice'
            ' | Where-Object {'
            '   $_.InstanceId -like "BTHENUM*" -or'
            '   $_.InstanceId -like "BTHHFENUM*" -or'
            '   $_.InstanceId -like "BTHLE*"'
            ' }'
            ' | Select-Object FriendlyName,Status'
            ' | ConvertTo-Json -Compress'
        )
        result = subprocess.run(
            ['powershell', '-NonInteractive', '-Command', ps_cmd],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        out = result.stdout.strip()
        if not out or out.lower() == 'null':
            devices = []
        else:
            parsed = json.loads(out)
            devices = [parsed] if isinstance(parsed, dict) else (parsed or [])

        ok_names = [
            d['FriendlyName'] for d in devices
            if d.get('FriendlyName') and d.get('Status') == 'OK'
        ]
        all_names = [d['FriendlyName'] for d in devices if d.get('FriendlyName')]
        logger.info(f'[蓝牙] 检测到蓝牙设备（状态OK）：{ok_names if ok_names else "无"}')

        try:
            svc_status = psutil.win_service_get('bthserv').status()
        except Exception:
            svc_status = '未找到'
        logger.info(f'[蓝牙] 服务状态：{svc_status}')

        issues = []
        for n in names:
            matched_ok  = [d for d in ok_names  if n in d]
            matched_all = [d for d in all_names if n in d]
            if matched_ok:
                logger.info(f'[蓝牙] {n} -> 识别正常：{matched_ok[0]}')
            elif matched_all:
                issues.append(f'蓝牙设备存在但状态异常：{matched_all[0]}')
            else:
                issues.append(f'蓝牙设备未识别：{n}')
        if svc_status != 'running':
            issues.append(f'蓝牙服务（bthserv）状态异常：{svc_status}')
        if issues:
            logger.info(f'[蓝牙] ✗ {"；".join(issues)}')
            return False, issues
        logger.info('[蓝牙] ✓ 正常')
        return True, []
    except Exception:
        logger.error(f'[蓝牙] 执行异常：{traceback.format_exc()}')
        return False, ['蓝牙检测执行异常']


def check_charging(charging_mode):
    """充电状态检测。charging_mode: '跳过'或空 跳过；'充电中' 验证正在充电；'未充电' 验证未充电"""
    if not charging_mode or charging_mode == '跳过':
        logger.info('[充电] 未配置，跳过')
        return True, []
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            logger.info('[充电] 未检测到电池（跳过）')
            return True, []
        pct     = bat.percent
        plugged = bat.power_plugged
        state_str = '充电中' if plugged else '未充电'
        logger.info(f'[充电] 当前状态：{state_str}，电量：{pct:.1f}%')
        if charging_mode == '充电中' and not plugged:
            return False, [f'期望充电中，但当前未充电（电量 {pct:.1f}%）']
        if charging_mode == '未充电' and plugged:
            return False, [f'期望未充电，但当前正在充电（电量 {pct:.1f}%）']
        logger.info('[充电] ✓ 正常')
        return True, []
    except Exception:
        logger.error(f'[充电] 执行异常：{traceback.format_exc()}')
        return False, ['充电检测执行异常']


def check_light_sensor(threshold):
    """光感传感器检测。threshold 为光感阈值（lux）：
    填 0（或未配置）跳过检测；否则读取当前 ALS 数值，低于阈值视为异常。
    通过 PowerShell WinRT 读取 ALS 数值。"""
    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        threshold = 0
    if threshold <= 0:
        logger.info('[光感] 未启用（阈值为0），跳过')
        return True, []
    try:
        ps = (
            '[Windows.Devices.Sensors.LightSensor,'
            'Windows.Devices.Sensors,ContentType=WindowsRuntime] | Out-Null; '
            '$s = [Windows.Devices.Sensors.LightSensor]::GetDefault(); '
            'if ($s) { $r = $s.GetCurrentReading(); '
            'if ($r) { $r.IlluminanceInLux } else { "NO_READING" } } '
            'else { "NO_SENSOR" }'
        )
        result = subprocess.run(
            ['powershell', '-NonInteractive', '-Command', ps],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        out = result.stdout.strip()
        if out == 'NO_SENSOR' or not out:
            logger.info('[光感] ✗ 未找到传感器')
            return False, ['光感传感器未找到（系统无法识别 ALS 设备）']
        if out == 'NO_READING':
            logger.info('[光感] ✗ 传感器存在但 GetCurrentReading() 返回 null')
            return False, ['光感传感器无法读取数值（GetCurrentReading 返回 null）']
        try:
            lux = float(out)
        except ValueError:
            logger.warning(f'[光感] ✗ 返回值无法解析：{out!r}')
            return False, [f'光感读数解析失败（返回值：{out!r}）']
        logger.info(f'[光感] 当前光感值：{lux:.2f} lux（阈值 {threshold:g} lux）')
        if lux < threshold:
            logger.info(f'[光感] ✗ 光感值低于阈值')
            return False, [f'光感值低于阈值：{lux:.2f} lux < {threshold:g} lux（传感器可能故障或读数归零）']
        logger.info('[光感] ✓ 正常')
        return True, []
    except Exception:
        logger.error(f'[光感] 执行异常：{traceback.format_exc()}')
        return False, ['光感检测执行异常']


def run_all_checks(config):
    all_pass   = True
    fail_items = []
    for name, fn, args in [
        ('驱动',    check_drivers,          ()),
        ('事件日志', check_event_log,        ()),   # 仅记录，不失败
        ('服务',    check_services,         ()),
        ('充电',    check_charging,         (config.get('charging_mode', '跳过'),)),
        ('光感',    check_light_sensor,     (config.get('light_sensor_threshold', 0),)),
        ('U盘',     check_usb_drives,       (config['u_disk_names'],)),
        ('显示器',  check_external_monitor, (config['monitor_names'],)),
        ('蓝牙',    check_bluetooth,        (config['bt_names'],)),
    ]:
        ok, issues = fn(*args)
        if not ok:
            all_pass = False
            fail_items.extend([f'[{name}] {i}' for i in issues])
    return all_pass, fail_items


# ── 设备枚举（供 UI 多选下拉使用）──────────────────────────────────

def enumerate_usb_drives():
    ps = (
        'Get-Disk | Where-Object {$_.BusType -eq "USB"} | '
        'Get-Partition | Get-Volume | '
        'Where-Object {$_.FileSystemLabel} | '
        'Select-Object -ExpandProperty FileSystemLabel | ConvertTo-Json -Compress'
    )
    try:
        r = subprocess.run(['powershell', '-NonInteractive', '-Command', ps],
                           capture_output=True, text=True, timeout=10,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        out = r.stdout.strip()
        if not out or out.lower() == 'null':
            return []
        parsed = json.loads(out)
        return [parsed] if isinstance(parsed, str) else (parsed or [])
    except Exception:
        return []


def enumerate_monitors():
    ps = (
        'Get-PnpDevice | Where-Object {'
        '  $_.Class -eq "Monitor" -and $_.Status -eq "OK"'
        '} | Select-Object -ExpandProperty FriendlyName | ConvertTo-Json -Compress'
    )
    try:
        r = subprocess.run(['powershell', '-NonInteractive', '-Command', ps],
                           capture_output=True, text=True, timeout=10,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        out = r.stdout.strip()
        if not out or out.lower() == 'null':
            return []
        parsed = json.loads(out)
        return [parsed] if isinstance(parsed, str) else (parsed or [])
    except Exception:
        return []


def enumerate_bluetooth_devices():
    ps = (
        'Get-PnpDevice | Where-Object {'
        '  ($_.InstanceId -like "BTHENUM*" -or '
        '   $_.InstanceId -like "BTHHFENUM*" -or '
        '   $_.InstanceId -like "BTHLE*") -and '
        '  $_.Status -eq "OK"'
        '} | Select-Object -ExpandProperty FriendlyName | ConvertTo-Json -Compress'
    )
    try:
        r = subprocess.run(['powershell', '-NonInteractive', '-Command', ps],
                           capture_output=True, text=True, timeout=10,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        out = r.stdout.strip()
        if not out or out.lower() == 'null':
            return []
        parsed = json.loads(out)
        return [parsed] if isinstance(parsed, str) else (parsed or [])
    except Exception:
        return []


# ── 测试主流程 ────────────────────────────────────────────────────

def run_test(config, update_ui):
    global is_running
    pythoncom.CoInitialize()
    try:
        _run_test_inner(config, update_ui)
    finally:
        pythoncom.CoUninitialize()


def _run_test_inner(config, update_ui):
    global is_running
    state = load_state()

    boot_delay      = config['boot_delay']
    reboot_interval = config['reboot_interval']
    startup_delay   = config['startup_delay']

    def countdown(seconds, label):
        """倒计时，每秒检查 is_running，返回 False 表示被中断"""
        for i in range(seconds, 0, -1):
            if not is_running:
                return False
            logger.info(f'{label} {i}s...')
            time.sleep(1)
        return True

    # ── 首次手动启动 ──────────────────────────────────────────────
    if not state['is_test_running']:
        state.update({
            'test_count': 0, 'fail_count': 0,
            'is_test_running': True, 'failures': [], 'config': config
        })
        save_state(state)
        create_startup_task(startup_delay)
        update_ui(state, '准备中，即将重启...')
        logger.info(f'初始化完成，{boot_delay}s 后执行第一次重启')
        if countdown(boot_delay, '首次重启倒计时'):
            subprocess.run('shutdown /r /t 0', shell=True)
        return

    # ── 重启后自动恢复 ─────────────────────────────────────────────
    logger.info(f'重启后恢复，等待系统稳定 {boot_delay}s...')
    if not countdown(boot_delay, '等待系统稳定'):
        return

    while is_running:
        state['test_count'] += 1
        logger.info(f'\n{"=" * 50}')
        logger.info(f'第 {state["test_count"]} 次重启后检测开始')
        update_ui(state, f'第 {state["test_count"]} 次检测中...')

        all_pass, fail_items = run_all_checks(config)

        if all_pass:
            logger.info(f'第 {state["test_count"]} 次 ✓ 全部通过')
            update_ui(state, f'第 {state["test_count"]} 次 ✓ 通过')
        else:
            state['fail_count'] += 1
            state['failures'].append({
                'test_num': state['test_count'],
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'details': fail_items,
            })
            logger.info(f'第 {state["test_count"]} 次 ✗ 失败：{fail_items}')
            update_ui(state, f'第 {state["test_count"]} 次 ✗ 失败')
            if config.get('stop_on_error') == '是':
                state['is_test_running'] = False
                save_state(state)
                delete_startup_task()
                logger.info('检测失败且已配置"异常停止"，压测终止，不再重启')
                update_ui(state, f'已停止（第 {state["test_count"]} 次检测失败）')
                root.after(0, lambda: start_button.configure(state='normal'))
                root.after(0, lambda: stop_button.configure(state='disabled'))
                return

        save_state(state)

        logger.info(f'等待 {reboot_interval}s 后重启...')
        if countdown(reboot_interval, '重启倒计时'):
            logger.info('执行重启')
            subprocess.run('shutdown /r /t 0', shell=True)
        return  # 重启指令发出后线程结束，下次开机由任务计划重新拉起


# ── GUI ───────────────────────────────────────────────────────────

def frame_main():
    global logger, root, start_button, stop_button
    global count_var, fail_var, status_var

    ctk.set_appearance_mode('light')
    ctk.set_default_color_theme('blue')

    root = ctk.CTk()
    root.title(VERSION)
    root.geometry('1100x640')
    root.minsize(900, 520)
    root.protocol('WM_DELETE_WINDOW', lambda: (logging.shutdown(), root.destroy()))

    # ── 左侧边栏（固定 290px）─────────────────────────────────────
    sidebar = ctk.CTkFrame(root, width=290, corner_radius=0,
                            fg_color='white')
    sidebar.pack(side='left', fill='y')
    sidebar.pack_propagate(False)

    # 标题
    ctk.CTkLabel(sidebar, text=VERSION,
                 font=ctk.CTkFont(size=11, weight='bold'),
                 text_color='#1565c0',
                 wraplength=262, justify='left').pack(padx=16, pady=(18, 14), anchor='w')

    ctk.CTkFrame(sidebar, height=1, fg_color='#e5e7eb').pack(fill='x')

    # 配置区（可滚动）
    ctk.CTkLabel(sidebar, text='配置',
                 font=ctk.CTkFont(size=11, weight='bold'),
                 text_color='#374151').pack(padx=16, pady=(14, 6), anchor='w')

    str_keys = {'u_disk_names', 'monitor_names', 'bt_names',
                'charging_mode', 'stop_on_error'}
    cfg_defs = [
        ('boot_delay',         '开机稳定等待（秒）',       '30'),
        ('reboot_interval',    '检测完成后重启等待（秒）',  '10'),
        ('startup_delay',      '自启动延时（秒）',          '30'),
        ('charging_mode',      '充电检测',                  '跳过'),
        ('stop_on_error',      '异常时停止',                '是'),
        ('light_sensor_threshold', '光感阈值lux（0=跳过）',  '0'),
        ('u_disk_names',       'U盘卷标',                   ''),
        ('monitor_names',      '外接显示器',                ''),
        ('bt_names',           '蓝牙设备',                  ''),
    ]
    COMBO_OPTS = {
        'charging_mode':      ['跳过', '充电', '未充电'],
        'stop_on_error':      ['是', '否'],
    }
    MULTISELECT_FNS = {
        'u_disk_names':  enumerate_usb_drives,
        'monitor_names': enumerate_monitors,
        'bt_names':      enumerate_bluetooth_devices,
    }
    DIALOG_TITLES = {
        'u_disk_names':  '选择 U盘设备',
        'monitor_names': '选择显示器',
        'bt_names':      '选择蓝牙设备',
    }
    config_vars = {}

    cfg_scroll = ctk.CTkScrollableFrame(sidebar, fg_color='white',
                                         scrollbar_button_color='#d1d5db',
                                         scrollbar_button_hover_color='#9ca3af',
                                         label_text='', height=310)
    cfg_scroll.pack(fill='x', padx=10)
    cfg_scroll.columnconfigure(0, weight=1)

    # ── 单选下拉（充电检测 / 异常时停止 / 光感检测）──────────────────
    def build_singleselect(parent, var, options, grid_row):
        """grab_set 模态弹窗，外观与输入框一致，无需 bind_all。"""
        popup_ref = [None]

        def get_text():
            v = var.get()
            return (v if v else options[0]) + '  ▾'

        btn = ctk.CTkButton(
            parent, text=get_text(), height=32,
            font=ctk.CTkFont(size=11),
            fg_color='#f5f7fa', text_color='#111827',
            border_width=1, border_color='#d1d5db',
            hover_color='#e8ecf0', anchor='w',
        )
        btn.grid(row=grid_row, column=0, sticky='ew', padx=4, pady=(0, 2))
        var.trace_add('write', lambda *_: btn.configure(text=get_text()))

        def _close(opt=None):
            if not (popup_ref[0] and popup_ref[0].winfo_exists()):
                popup_ref[0] = None
                return
            if opt is not None:
                var.set(opt)
            try:
                popup_ref[0].grab_release()
                popup_ref[0].destroy()
            except Exception:
                pass
            popup_ref[0] = None

        def open_popup():
            if popup_ref[0] and popup_ref[0].winfo_exists():
                _close()
                return
            btn.update_idletasks()
            bx = btn.winfo_rootx()
            by = btn.winfo_rooty() + btn.winfo_height() + 1
            bw = max(btn.winfo_width(), 180)
            popup = tk.Toplevel()
            popup.overrideredirect(True)
            popup.configure(bg='#d1d5db')
            popup.geometry(f'{bw}x{len(options) * 36 + 2}+{bx}+{by}')
            popup.lift()
            popup.grab_set()
            popup_ref[0] = popup
            # grab 捕获到的外部点击 → 关闭不改值
            popup.bind('<Button-1>', lambda e: _close())

            wrap = tk.Frame(popup, bg='white')
            wrap.pack(fill='both', expand=True, padx=1, pady=1)
            for opt in options:
                sel  = (opt == var.get())
                bgc  = '#e8f0fe' if sel else 'white'
                fgc  = '#1a6fc4' if sel else '#111827'
                row  = tk.Frame(wrap, bg=bgc, cursor='hand2')
                row.pack(fill='x')
                lbl  = tk.Label(row, text=opt, bg=bgc, fg=fgc,
                                font=('Microsoft YaHei UI', 11),
                                anchor='w', padx=10, pady=6)
                lbl.pack(fill='x')
                for w in (row, lbl):
                    w.bind('<Enter>',    lambda e, f=row: (
                        f.configure(bg='#e8f0fe'),
                        [c.configure(bg='#e8f0fe') for c in f.winfo_children()]))
                    w.bind('<Leave>',    lambda e, f=row, b=bgc: (
                        f.configure(bg=b),
                        [c.configure(bg=b) for c in f.winfo_children()]))
                    w.bind('<Button-1>', lambda e, o=opt: _close(o))

        btn.configure(command=open_popup)
        return btn

    # ── 多选标签列表（U盘 / 显示器 / 蓝牙）─────────────────────────────
    def build_tag_list(parent, var, enumerate_fn, grid_row, dialog_title):
        """已选设备显示为蓝色标签行（带 − 删除），点 ＋ 按钮打开模态对话框添加。"""
        outer = ctk.CTkFrame(parent, fg_color='#f5f7fa',
                              border_width=1, border_color='#d1d5db',
                              corner_radius=6)
        outer.grid(row=grid_row, column=0, sticky='ew', padx=4, pady=(0, 2))
        outer.columnconfigure(0, weight=1)

        tags_frame = ctk.CTkFrame(outer, fg_color='transparent')
        tags_frame.grid(row=0, column=0, sticky='ew', padx=6, pady=(6, 2))
        tags_frame.columnconfigure(0, weight=1)

        def get_items():
            return [s.strip() for s in var.get().split(',') if s.strip()]

        def refresh_tags():
            for w in tags_frame.winfo_children():
                w.destroy()
            items = get_items()
            if not items:
                ctk.CTkLabel(tags_frame, text='（跳过）',
                             font=ctk.CTkFont(size=11),
                             text_color='#9ca3af').grid(row=0, column=0, sticky='w')
                return
            for i, item in enumerate(items):
                rf = ctk.CTkFrame(tags_frame, fg_color='#dbeafe', corner_radius=4)
                rf.grid(row=i, column=0, sticky='ew', pady=1)
                rf.columnconfigure(0, weight=1)
                ctk.CTkLabel(rf, text=item, font=ctk.CTkFont(size=11),
                             text_color='#1e40af', anchor='w').grid(
                             row=0, column=0, sticky='ew', padx=(6, 0), pady=3)
                ctk.CTkButton(rf, text='−', width=24, height=24,
                              fg_color='transparent', text_color='#dc2626',
                              hover_color='#fee2e2',
                              font=ctk.CTkFont(size=13, weight='bold'),
                              command=lambda it=item: _remove(it)
                              ).grid(row=0, column=1, padx=(0, 3))

        def _remove(item):
            var.set(','.join(x for x in get_items() if x != item))
            refresh_tags()

        def open_add_dialog():
            dlg = tk.Toplevel(root)
            dlg.title(dialog_title)
            dlg.resizable(False, False)
            dlg.transient(root)
            dlg.configure(bg='white')

            # 居中显示在主窗口中央
            dlg_w, dlg_h = 500, 460
            root.update_idletasks()
            rx = root.winfo_rootx() + (root.winfo_width()  - dlg_w) // 2
            ry = root.winfo_rooty() + (root.winfo_height() - dlg_h) // 2
            dlg.geometry(f'{dlg_w}x{dlg_h}+{rx}+{ry}')
            dlg.grab_set()

            tk.Label(dlg, text=dialog_title, bg='white', fg='#111827',
                     font=('Microsoft YaHei UI', 14, 'bold')).pack(
                     anchor='w', padx=18, pady=(18, 4))
            status_lbl = tk.Label(dlg, text='正在检测设备…', bg='white',
                                  fg='#6b7280', font=('Microsoft YaHei UI', 12))
            status_lbl.pack(anchor='w', padx=18)

            list_border = tk.Frame(dlg, bg='#d1d5db')
            list_border.pack(fill='both', expand=True, padx=18, pady=10)
            list_bg = tk.Frame(list_border, bg='white')
            list_bg.pack(fill='both', expand=True, padx=1, pady=1)
            canvas  = tk.Canvas(list_bg, bg='white', highlightthickness=0)
            vsb     = tk.Scrollbar(list_bg, orient='vertical', command=canvas.yview)
            canvas.configure(yscrollcommand=vsb.set)
            inner   = tk.Frame(canvas, bg='white')
            wid     = canvas.create_window((0, 0), window=inner, anchor='nw')

            def _on_cfg(e=None):
                canvas.configure(scrollregion=canvas.bbox('all'))
                canvas.itemconfig(wid, width=canvas.winfo_width())
            inner.bind('<Configure>', _on_cfg)
            canvas.bind('<Configure>', _on_cfg)
            canvas.bind('<MouseWheel>',
                        lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, 'units'))
            canvas.pack(side='left', fill='both', expand=True)
            vsb.pack(side='right', fill='y')

            all_ref = [None]

            def _redraw():
                devs = all_ref[0] or []
                for w in inner.winfo_children():
                    w.destroy()
                existing = set(get_items())
                if not devs:
                    tk.Label(inner, text='未检测到设备', bg='white',
                             fg='#9ca3af',
                             font=('Microsoft YaHei UI', 13)).pack(pady=28)
                    return
                for i, dev in enumerate(devs):
                    if i:
                        tk.Frame(inner, bg='#e5e7eb', height=1).pack(fill='x')
                    already = dev in existing
                    rbg     = '#f0f7ff' if already else 'white'
                    rf      = tk.Frame(inner, bg=rbg)
                    rf.pack(fill='x')
                    tk.Label(rf, text=dev, bg=rbg,
                             fg='#1e40af' if already else '#111827',
                             font=('Microsoft YaHei UI', 13),
                             anchor='w').pack(side='left', padx=14, pady=10,
                                              fill='x', expand=True)
                    if already:
                        tk.Label(rf, text='已添加', bg=rbg, fg='#9ca3af',
                                 font=('Microsoft YaHei UI', 12)).pack(side='right', padx=14)
                    else:
                        def _add(d=dev):
                            items = get_items()
                            if d not in items:
                                items.append(d)
                                var.set(','.join(items))
                                refresh_tags()
                            _redraw()
                        tk.Button(rf, text='＋', bg='#1a6fc4', fg='white',
                                  relief='flat', bd=0, padx=14, pady=5,
                                  font=('Microsoft YaHei UI', 13),
                                  command=_add).pack(side='right', padx=10, pady=6)

            def _refresh():
                devs = enumerate_fn()
                if dlg.winfo_exists():
                    dlg.after(0, lambda: (
                        status_lbl.configure(text=f'已检测到 {len(devs)} 个设备'),
                        all_ref.__setitem__(0, devs),
                        _redraw()
                    ))

            threading.Thread(target=_refresh, daemon=True).start()

            tk.Button(dlg, text='完成', bg='#1a6fc4', fg='white',
                      relief='flat', bd=0, padx=32, pady=8,
                      font=('Microsoft YaHei UI', 13),
                      command=lambda: (dlg.grab_release(), dlg.destroy())
                      ).pack(pady=(0, 16))

        add_frame = ctk.CTkFrame(outer, fg_color='transparent')
        add_frame.grid(row=1, column=0, sticky='e', padx=6, pady=(2, 6))
        ctk.CTkButton(add_frame, text='＋ 添加', height=26, width=76,
                      font=ctk.CTkFont(size=11),
                      fg_color='#1a6fc4', hover_color='#1255a0',
                      corner_radius=5, command=open_add_dialog).pack()

        # var 被外部写入（如加载历史配置）时自动刷新标签显示
        var.trace_add('write', lambda *_: refresh_tags())

        refresh_tags()
        return outer

    for i, (key, label, default) in enumerate(cfg_defs):
        ctk.CTkLabel(cfg_scroll, text=label,
                     font=ctk.CTkFont(size=11),
                     text_color='#6b7280',
                     anchor='w').grid(row=i * 2, column=0, sticky='w',
                                      padx=4, pady=(8, 1))
        var = tk.StringVar(value=default)
        if key in COMBO_OPTS:
            build_singleselect(cfg_scroll, var, COMBO_OPTS[key], i * 2 + 1)
        elif key in MULTISELECT_FNS:
            build_tag_list(cfg_scroll, var, MULTISELECT_FNS[key], i * 2 + 1, DIALOG_TITLES[key])
        else:
            ctk.CTkEntry(cfg_scroll, textvariable=var, height=32,
                         font=ctk.CTkFont(size=11),
                         fg_color='#f5f7fa', border_color='#d1d5db',
                         text_color='#111827').grid(row=i * 2 + 1, column=0, sticky='ew',
                                                    padx=4, pady=(0, 2))
        config_vars[key] = var

    ctk.CTkFrame(sidebar, height=1, fg_color='#e5e7eb').pack(fill='x', pady=(10, 0))

    # 状态区
    ctk.CTkLabel(sidebar, text='运行状态',
                 font=ctk.CTkFont(size=11, weight='bold'),
                 text_color='#374151').pack(padx=16, pady=(14, 8), anchor='w')

    count_var  = tk.StringVar(value='0')
    fail_var   = tk.StringVar(value='0')
    status_var = tk.StringVar(value='等待开始')

    counters = ctk.CTkFrame(sidebar, fg_color='transparent')
    counters.pack(fill='x', padx=12, pady=(0, 10))
    counters.columnconfigure((0, 1), weight=1)

    def counter_tile(col, caption, var, color):
        tile = ctk.CTkFrame(counters, fg_color='#f0f4f8', corner_radius=10)
        tile.grid(row=0, column=col, sticky='ew',
                  padx=(0, 5) if col == 0 else (5, 0))
        ctk.CTkLabel(tile, text=caption,
                     font=ctk.CTkFont(size=10),
                     text_color='#6b7280').pack(anchor='w', padx=10, pady=(8, 0))
        ctk.CTkLabel(tile, textvariable=var,
                     font=ctk.CTkFont(size=28, weight='bold'),
                     text_color=color).pack(anchor='w', padx=10, pady=(0, 8))

    counter_tile(0, '压测次数', count_var, '#4d9ef7')
    counter_tile(1, '失败次数', fail_var,  '#f96060')

    ctk.CTkLabel(sidebar, text='当前状态',
                 font=ctk.CTkFont(size=10),
                 text_color='#6b7280').pack(padx=16, pady=(4, 2), anchor='w')
    ctk.CTkLabel(sidebar, textvariable=status_var,
                 font=ctk.CTkFont(size=11),
                 text_color='#374151',
                 wraplength=258, justify='left').pack(padx=16, anchor='w')

    # ── 右侧主区域 ────────────────────────────────────────────────
    right = ctk.CTkFrame(root, fg_color='white', corner_radius=0)
    right.pack(side='left', fill='both', expand=True, padx=12, pady=12)

    ctk.CTkLabel(right, text='运行日志',
                 font=ctk.CTkFont(size=11, weight='bold'),
                 text_color='#374151').pack(anchor='w', pady=(0, 6))

    log_text = ctk.CTkTextbox(
        right,
        font=ctk.CTkFont(family='Consolas', size=10),
        state='disabled',
        wrap='word',
        fg_color='#f8f9fa',
        text_color='#2d333b',
        scrollbar_button_color='#d1d5db',
        scrollbar_button_hover_color='#9ca3af',
        border_width=1,
        border_color='#e5e7eb',
        corner_radius=8,
    )
    log_text.pack(fill='both', expand=True, pady=(0, 10))

    logger = get_logger(log_text)

    # 底部按钮行
    btn_row = ctk.CTkFrame(right, fg_color='white')
    btn_row.pack(fill='x')

    # ── 恢复历史状态到 UI ─────────────────────────────────────────
    state = load_state()
    if state['test_count'] > 0:
        count_var.set(str(state['test_count']))
        fail_var.set(str(state['fail_count']))
    if state.get('config'):
        for k, v in state['config'].items():
            if k in config_vars:
                config_vars[k].set(str(v))

    def update_ui(s, status_text=''):
        root.after(0, lambda: count_var.set(str(s['test_count'])))
        root.after(0, lambda: fail_var.set(str(s['fail_count'])))
        if status_text:
            root.after(0, lambda: status_var.set(status_text))

    def on_start():
        global is_running
        is_running = True
        cur_state  = load_state()

        if cur_state['is_test_running'] and cur_state.get('config'):
            config = cur_state['config']
            for k, v in config.items():
                if k in config_vars:
                    config_vars[k].set(str(v))
        else:
            try:
                config = {}
                for k, v in config_vars.items():
                    raw = v.get()
                    config[k] = raw if k in str_keys else int(raw)
            except ValueError:
                tk.messagebox.showerror('错误', '配置项请填写整数（名称字段除外）')
                return

        start_button.configure(state='disabled')
        stop_button.configure( state='normal')
        threading.Thread(target=run_test, args=(config, update_ui), daemon=True).start()

    def on_stop():
        global is_running
        is_running = False
        cur_state  = load_state()
        cur_state['is_test_running'] = False
        save_state(cur_state)
        delete_startup_task()
        status_var.set('已停止')
        logger.info('压测已停止，开机自启动任务已删除')
        root.after(0, lambda: start_button.configure(state='normal'))
        root.after(0, lambda: stop_button.configure( state='disabled'))

    start_button = ctk.CTkButton(
        btn_row, text='开始', width=110, height=38,
        font=ctk.CTkFont(size=12, weight='bold'),
        fg_color='#1a6fc4', hover_color='#1255a0',
        command=on_start)
    stop_button = ctk.CTkButton(
        btn_row, text='停止', width=110, height=38,
        font=ctk.CTkFont(size=12, weight='bold'),
        fg_color='#b52020', hover_color='#8f1818',
        state='disabled', command=on_stop)
    log_btn = ctk.CTkButton(
        btn_row, text='打开日志', width=110, height=38,
        font=ctk.CTkFont(size=12),
        fg_color='#2e4057', hover_color='#223040',
        command=lambda: os.startfile(log_path))

    start_button.pack(side='left', padx=(0, 8))
    stop_button.pack( side='left', padx=(0, 8))
    log_btn.pack(     side='left')

    if state['is_test_running']:
        status_var.set('重启后自动恢复中...')
        root.after(500, on_start)

    root.mainloop()


if __name__ == '__main__':
    freeze_support()
    frame_main()
