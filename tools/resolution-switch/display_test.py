import os
import time
import win32api
import ctypes
import PySimpleGUI as sg
import threading
import win32con
from screeninfo import get_monitors


# 添加一个全局变量，用于控制分辨率切换线程的运行状态
running = True
paused = False
run_count = 0
suc = 0
fail = 0
now1 = int(round(time.time() * 1000))
start_time = time.strftime('%Y%m%d%H%M%S', time.localtime(now1 / 1000))
print("程序开始")
class DisplaySettings:
    # 分辨率切换模式
    TYPE1 = "切换刷新率和分辨率"
    TYPE2 = "只切换分辨率"
    TYPE3 = "只切换一次分辨率和刷新率"
    TYPE4 = "切换1K和8K"

    # DEVMODE结构体定义，用于获取和设置屏幕分辨率
    class DEVMODE(ctypes.Structure):
        _fields_ = [
            ("dmDeviceName", ctypes.c_wchar * 32),
            ("dmSpecVersion", ctypes.c_ushort),
            ("dmDriverVersion", ctypes.c_ushort),
            ("dmSize", ctypes.c_ushort),
            ("dmDriverExtra", ctypes.c_ushort),
            ("dmFields", ctypes.c_ulong),
            ("dmOrientation", ctypes.c_short),
            ("dmPaperSize", ctypes.c_short),
            ("dmPaperLength", ctypes.c_short),
            ("dmPaperWidth", ctypes.c_short),
            ("dmScale", ctypes.c_short),
            ("dmCopies", ctypes.c_short),
            ("dmDefaultSource", ctypes.c_short),
            ("dmPrintQuality", ctypes.c_short),
            ("dmColor", ctypes.c_short),
            ("dmDuplex", ctypes.c_short),
            ("dmYResolution", ctypes.c_short),
            ("dmTTOption", ctypes.c_short),
            ("dmCollate", ctypes.c_short),
            ("dmFormName", ctypes.c_wchar * 32),
            ("dmLogPixels", ctypes.c_ushort),
            ("dmBitsPerPel", ctypes.c_ulong),
            ("dmPelsWidth", ctypes.c_ulong),
            ("dmPelsHeight", ctypes.c_ulong),
            ("dmDisplayFlags", ctypes.c_ulong),
            ("dmDisplayFrequency", ctypes.c_ulong),
            ("dmICMMethod", ctypes.c_ulong),
            ("dmICMIntent", ctypes.c_ulong),
            ("dmMediaType", ctypes.c_ulong),
            ("dmDitherType", ctypes.c_ulong),
            ("dmReserved1", ctypes.c_ulong),
            ("dmReserved2", ctypes.c_ulong),
            ("dmPanningWidth", ctypes.c_ulong),
            ("dmPanningHeight", ctypes.c_ulong),
        ]

    # 获取可用的屏幕分辨率和刷新率
    def get_screen_resolutions_and_refresh_rates(self):
        devmode = DisplaySettings.DEVMODE()
        devmode.dmSize = ctypes.sizeof(DisplaySettings.DEVMODE)
        i = 0
        resolutions_and_refresh_rates = set()

        while ctypes.windll.user32.EnumDisplaySettingsW(None, i, ctypes.byref(devmode)):
            resolutions_and_refresh_rates.add((devmode.dmPelsWidth, devmode.dmPelsHeight, devmode.dmDisplayFrequency))
            i += 1

        return resolutions_and_refresh_rates

    # 根据所选模式筛选分辨率和刷新率
    def get_resolution_and_refresh(self, type):
        resolution_list = []
        resolutions_and_refresh_rates = self.get_screen_resolutions_and_refresh_rates()
        if type == self.TYPE2 or type == self.TYPE4:
            for resolution in resolutions_and_refresh_rates:
                res_list = [resolution[0], resolution[1]]
                resolution_list.append(res_list)
            return resolution_list
        if type == self.TYPE1 or type == self.TYPE3:
            for resolution in resolutions_and_refresh_rates:
                res_list = [resolution[0], resolution[1], resolution[2]]
                resolution_list.append(res_list)
            return resolution_list

    # 设置分辨率和刷新率
    @staticmethod
    def set_fbl(display, time_sleep, type):
        if type == DisplaySettings.TYPE2 or type == DisplaySettings.TYPE4:
            width = display[0]
            height = display[1]
            time_sleep = int(time_sleep)
            dm = win32api.EnumDisplaySettings(None, 0)
            dm.PelsWidth = int(width)
            dm.PelsHeight = int(height)
            dm.DisplayFixedOutput = 1
            win32api.ChangeDisplaySettings(dm, 0)
            time.sleep(time_sleep)
        if type == DisplaySettings.TYPE1 or type == DisplaySettings.TYPE3:
            width = display[0]
            height = display[1]
            frequency = display[2]
            time_sleep = int(time_sleep)
            dm = win32api.EnumDisplaySettings(None, 0)
            dm.PelsWidth = int(width)
            dm.PelsHeight = int(height)
            dm.DisplayFrequency = int(frequency)
            dm.DisplayFixedOutput = 1
            win32api.ChangeDisplaySettings(dm, 0)
            time.sleep(time_sleep)

    @staticmethod
    def printAllScreen():
        i = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, i)
                print("[%d] %s (%s)" % (i, device.DeviceString, device.DeviceName))
                i = i + 1
            except:
                break
        return i

    # 获取当前系统分辨率参数
    @staticmethod
    def now_sys(type):
        def get_refresh():
            user32 = ctypes.windll.user32
            device_context = user32.GetDC(None)
            gdi32 = ctypes.windll.gdi32
            refresh_rate = gdi32.GetDeviceCaps(device_context, 116)  # VREFRESH
            user32.ReleaseDC(None, device_context)
            return refresh_rate

        def get_screen():
            monitor = get_monitors()[0]
            width = monitor.width
            height = monitor.height
            return width, height

        sys_frequency = get_refresh()
        sys_width = get_screen()[0]
        sys_height = get_screen()[1]
        if type == DisplaySettings.TYPE2 or type == DisplaySettings.TYPE4:
            sys_display = [sys_width, sys_height]
            return sys_display
        if type == DisplaySettings.TYPE1 or type == DisplaySettings.TYPE3:
            sys_display = [sys_width, sys_height, sys_frequency]
            return sys_display

    # 分辨率切换压测
    def fina_set_display(self, type_thing, interval, logpath, window):
        global running, paused, run_count, suc, fail
        type = type_thing
        time_sleep = int(interval[:-1])
        resolution_and_refreshs = self.get_resolution_and_refresh(type)
        logpath = rf"{logpath}"
        if type == self.TYPE1 or type == self.TYPE2:
            while running:
                for resolution_and_refresh in resolution_and_refreshs:
                    while paused:
                        time.sleep(1)
                    if not running:  # 在循环内部检查running变量
                        break
                    now1 = int(round(time.time() * 1000))
                    deal_time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now1 / 1000))
                    self.set_fbl(resolution_and_refresh, time_sleep, type)
                    run_count += 1
                    window['run_count'].update(run_count)
                    now_flash = self.now_sys(type)
                    if resolution_and_refresh == now_flash:
                        result1 = "成功"
                        suc += 1
                        # window['run_suc'].update(suc)
                    else:
                        result1 = "失败"
                        fail += 1
                        # window['run_fail'].update(fail)
                    now2 = int(round(time.time() * 1000))
                    deal_time = (now2 - now1) / 1000
                    try:
                        with open(rf"{logpath}\{start_time}display_pressure_test.txt", 'a') as file0:
                            file0.write(
                                f"操作时间：{deal_time1}  当前系统分辨率：{now_flash}  设置的分辨率：{resolution_and_refresh}  共耗时 {deal_time} 秒  设置{result1}  共执行了{run_count}次  成功了 {suc} 次  失败了 {fail}次 ")
                            file0.write('\n')
                    except Exception as e:
                        print(e)
        if type == self.TYPE3:
            for resolution_and_refresh in resolution_and_refreshs:
                while paused:
                    time.sleep(1)
                if not running:  # 在循环内部检查running变量
                    break
                now1 = int(round(time.time() * 1000))
                deal_time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now1 / 1000))
                self.set_fbl(resolution_and_refresh, time_sleep, type)
                run_count += 1
                window['run_count'].update(run_count)
                now_flash = self.now_sys(type)
                if resolution_and_refresh == now_flash:
                    result1 = "成功"
                    suc += 1
                    # window['run_suc'].update(suc)
                else:
                    result1 = "失败"
                    fail += 1
                    # window['run_fail'].update(fail)
                now2 = int(round(time.time() * 1000))
                deal_time = (now2 - now1) / 1000
                with open(rf"{logpath}\{start_time}display_pressure_test.txt", 'a') as file0:
                    file0.write(
                        f"操作时间：{deal_time1}  当前系统分辨率：{now_flash}  设置的分辨率：{resolution_and_refresh}  共耗时 {deal_time} 秒  设置{result1}  共执行了{run_count}次  成功了 {suc} 次  失败了 {fail}次 ")
                    file0.write('\n')
        if type == self.TYPE4:
            single_display = [[7680, 4320], [1920, 1080]]
            while running:
                for resolution_and_refresh in single_display:
                    while paused:
                        time.sleep(1)
                    if not running:  # 在循环内部检查running变量
                        break
                    now1 = int(round(time.time() * 1000))
                    deal_time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now1 / 1000))
                    self.set_fbl(resolution_and_refresh, time_sleep, type)
                    run_count += 1
                    window['run_count'].update(run_count)
                    now_flash = self.now_sys(type)
                    if resolution_and_refresh == now_flash:
                        result1 = "成功"
                        suc += 1
                        # window['run_suc'].update(suc)
                    else:
                        result1 = "失败"
                        fail += 1
                        # window['run_fail'].update(fail)
                    now2 = int(round(time.time() * 1000))
                    deal_time = (now2 - now1) / 1000
                    with open(rf"{logpath}\{start_time}display_pressure_test.txt", 'a') as file0:
                        file0.write(
                            f"操作时间：{deal_time1}  当前系统分辨率：{now_flash}  设置的分辨率：{resolution_and_refresh}  共耗时 {deal_time} 秒  设置{result1}  共执行了{run_count}次  成功了 {suc} 次  失败了 {fail}次 ")
                        file0.write('\n')




def main():
    global running, paused, run_count, suc, fail
    display_settings = DisplaySettings()

    layout = [[sg.Text("切换间隔：", size=(10, 0)),
               sg.Combo(["5S", "10S", "15S", "30S", "60S", "120S"], default_value="15S", size=(70, 1), key="interval")],
              [sg.Text("切换选项：", size=(10, 0)),
               sg.Combo(
                   [display_settings.TYPE1, display_settings.TYPE2, display_settings.TYPE3, display_settings.TYPE4],
                   default_value=display_settings.TYPE1, size=(70, 1), key="switch_option")],
              [sg.Text("日志路径：", size=(10, 0)), sg.Input(key="log_path", size=(58, 1)), sg.FolderBrowse(size=(10, 1))],
              [sg.Button("打开日志文件夹", size=(36, 1)), sg.Button("打开日志文件", size=(36, 1))],
              [sg.Button("开始", size=(14, 1)), sg.Text("", size=(12, 1)), sg.Button("暂停/继续", size=(14, 1)),
               sg.Text("", size=(12, 1)), sg.Button("退出", size=(14, 1))],
              [sg.Text("总次数：", size=(8, 1)), sg.Text("0", key="run_count", size=(5, 1)),
               sg.Text("", size=(12, 1)),
               sg.Text("成功次数：", size=(8, 1)), sg.Text("0", key="suc_count", size=(5, 1)),
               sg.Text("", size=(12, 1)),
               sg.Text("失败次数：", size=(8, 1)), sg.Text("0", key="fail_count", size=(5, 1))],
              [sg.Text("", key="warning", size=(30, 1), text_color="red")]]
    # window = sg.Window("分辨率切换压测", layout)
    window = sg.Window("分辨率切换压测", layout, size=(600, 200), resizable=True)



    def clear_warning(window):
        window["warning"].update("")

    # 事件循环
    while True:
        event, values = window.read(timeout=5000)  # 设置timeout为5000毫秒（5秒）
        if event in (None, "退出"):
            running = False  # 设置running为False，以停止分辨率切换线程
            break
        elif event == "开始":
            if not values["interval"] or not values["switch_option"] or not values["log_path"]:
                window["warning"].update("配置未选完全")
            else:
                running = True
                paused = False
                threading.Thread(target=display_settings.fina_set_display,
                                 args=(values["switch_option"], values["interval"], values["log_path"], window)).start()
        elif event == "暂停/继续":
            if not running:
                window["warning"].update("未开始")
            else:
                paused = not paused
        elif event == "打开日志文件夹":
            if not values["log_path"]:
                window["warning"].update("未选择日志路径")
            else:
                os.startfile(values["log_path"])
        elif event == "打开日志文件":
            if not values["log_path"]:
                window["warning"].update("未选择日志路径")
            else:
                try:
                    os.startfile(os.path.join(values["log_path"], rf'{values["log_path"]}\{start_time}display_pressure_test.txt'))
                except:
                    window["warning"].update("未找到日志文件")

        # 更新成功和失败次数
        window['suc_count'].update(suc)
        window['fail_count'].update(fail)

        # 清空警告文本
        if event != sg.WIN_CLOSED and window["warning"].get() != "":
            threading.Timer(5, clear_warning, args=(window,)).start()

    # 关闭窗口
    window.close()


if __name__ == '__main__':
    main()