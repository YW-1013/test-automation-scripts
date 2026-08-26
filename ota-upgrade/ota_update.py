import ctypes
import sys
import winreg
import re
import cv2
import numpy as np
import pyautogui
import time
import subprocess
import os

old_version = "1.3.8.1"
new_version = "100.0.0.75"


file_path = os.path.dirname(os.path.realpath(sys.argv[0]))
template_image_path = os.path.join(file_path,'systemcontrol.jpg')
template_update_path = os.path.join(file_path,'systemcontrolupdate.jpg')
old_system_control_path = os.path.join(file_path,f"SystemControl_MegaBook2025_{old_version}.exe")

def get_app_version():
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    pattern = re.compile(r"SystemControl.*", re.IGNORECASE)

    for path in reg_paths:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            if pattern.search(app_name):
                                version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                return version
                        except WindowsError:
                            continue
        except WindowsError:
            continue

    return "null"


def is_application_opened(template_path, threshold=0.8):
    try:
        # 读取模板图片
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"无法读取模板图片: {template_path}")

        # 获取屏幕截图
        screenshot = pyautogui.screenshot(region=(2071, 704, 690, 1000))
        screenshot.save('screenshot.png')
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

#打开控制中心，使用之前的方法就行
def open_old_systemcontrol():
    x = 2440
    times = 1
    while True:
        print(f"第{times}次尝试打开控制中心")
        pyautogui.click(x, 1750)
        time.sleep(2)
        if is_application_opened(template_update_path, threshold=0.8):
            return x
        else:
            x -= 40
            times += 1
            if x < 2280:
                x = 2440



def systemcontrol_update():
    x = 2440
    times = 1
    while True:
        print(f"第{times}次尝试打开控制中心")
        pyautogui.click(x, 1750)
        time.sleep(2)
        if is_application_opened(template_update_path, threshold=0.8):
            print("进入升级")
            pyautogui.click(x + 150, 1385)
            time.sleep(120)
            break
        else:
            x -= 40
            times += 1
            if x < 2280:
                x = 2440





def systemcontrol_uninstall():
    while get_app_version() != "null":
        subprocess.run([r'C:\Program Files\Megabook\SystemControl\unins000.exe', '/SILENT', '/NORESTART'],
                       check=True)
        time.sleep(60)


def systemcontrol_install():
    subprocess.run([old_system_control_path, '/SILENT', '/NORESTART'],check=True)
    time.sleep(30)
    if get_app_version() == old_version:
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

def main():
    test_times = 0
    while True:
        try:
            version = get_app_version()
            if version == old_version:
                systemcontrol_update()
                if get_app_version() == new_version:
                    test_times += 1
                    print(f"升级成功了{test_times}次")
                else:
                    print("升级失败")
                    sys.exit()
                continue
            elif version == new_version:
                systemcontrol_uninstall()
                continue
            else:
                systemcontrol_install()
                continue
        except Exception as e:
            print(e)

if __name__ == '__main__':
    if not is_admin():
        # 重新以管理员权限运行脚本
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    main()