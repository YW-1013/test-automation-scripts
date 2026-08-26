import ctypes
import sys
import re
import cv2
import numpy as np
import pyautogui
import time
import subprocess
import os
import win32com.client
import wmi

old_version = "D020"
new_version = "D021"
task_name = 'bios_update_megabook'

file_path = os.path.dirname(os.path.realpath(sys.argv[0]))
template_image_path = os.path.join(file_path,'systemcontrol.jpg')
template_update_path = os.path.join(file_path,'biosupdate.jpg')
old_system_control_path = os.path.join(file_path,f"SystemControl_{old_version}.exe")
exe_path = os.path.join(file_path,'bios_update.exe')
bios_path = os.path.join(file_path,'D020.exe')

def get_bios_version():
    c = wmi.WMI()
    bios = c.Win32_BIOS()[0]  # 获取第一条BIOS记录
    bios_version_full = bios.SMBIOSBIOSVersion
    match = re.search(r'V500R001B01(\S+)', bios_version_full)
    return match.group(1) if match else bios_version_full  # 返回匹配部分或原始值


def is_application_opened(template_path, threshold=0.8):
    try:
        # 读取模板图片
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"无法读取模板图片: {template_path}")

        # 获取屏幕截图
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 使用模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 如果最大匹配值大于阈值，则认为找到了目标应用
        if max_val >= threshold:
            print(f"找到匹配，相似度: {max_val:.2f}")
            return True
        else:
            print(f"未找到匹配，最高相似度: {max_val:.2f}")
            return False

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

#打开控制中心，使用之前的方法就行
def open_systemcontrol():
    x = 2440
    times = 1
    while True:
        print(f"第{times}次尝试打开控制中心")
        pyautogui.click(x, 1750)
        time.sleep(2)
        if is_application_opened(template_image_path, threshold=0.8):
            return x
        else:
            x -= 40
            times += 1
            if x < 2280:
                x = 2440



def bios_update():
    while True:
        x = open_systemcontrol()
        time.sleep(2)
        pyautogui.click(x+270,1011)
        time.sleep(2)
        pyautogui.click(x+200, 1170)
        time.sleep(2)
        if is_application_opened(template_update_path, threshold=0.8):
            print("进入升级")
            pyautogui.click(1890, 1088)
            time.sleep(2)
            pyautogui.click(1609, 997)
            time.sleep(2)
            pyautogui.click(1723, 898)
            time.sleep(2)
            pyautogui.click(1723, 898)
            time.sleep(120)
            break
        else:
            print("点击进入升级页面失败，重新进入")
            continue


def bios_install():
    subprocess.Popen([bios_path])
    time.sleep(30)
    print("点击进行升级")
    pyautogui.click(1600, 1092)
    time.sleep(300)
    if get_bios_version() == old_version:
        print("安装成功")
        return True
    else:
        print("安装失败")
        return False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_task_xml(executable_path, working_directory,script_args=None, delay_seconds=30):
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
        print(f'{task_name}任务成功创建')

    except Exception as e:
        print(f"任务创建失败，失败原因为： {e}")



def main():
    create_task_xml(exe_path, file_path, script_args=None, delay_seconds=30)
    test_times = 0
    while True:
        try:
            version = get_bios_version()
            print(version)
            if version == old_version:
                bios_update()
                if get_bios_version() == new_version:
                    test_times += 1
                    print(f"升级成功了{test_times}次")
                else:
                    print("升级失败")
                    sys.exit()
                continue
            elif version == new_version:
                bios_install()
                continue
            else:
                sys.exit()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    if not is_admin():
        # 重新以管理员权限运行脚本
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    main()

