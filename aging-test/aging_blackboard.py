import uiautomator2 as ut
import time
import random
import os
import re
import multiprocessing
import threading
# from pyzbar.pyzbar import decode
from PIL import Image
import requests
import logging
import traceback


def outer(func):
    def inner(self):
        try:
            arg = func(self)
        except:
            self.logger.error(str(traceback.format_exc()))
        return arg
    return inner


class Aging:
    def __init__(self):
        # self.ip_address = "192.168.137.1:5555"
        self.ip_address = "192.168.4.93:5555"
        #
        self.device = ut.connect(self.ip_address)
        self.package_name = ["com.h3c.settings/.main.ui.activity.SettingActivity",
                             "com.h3c.commentary/com.example.multiscreenui.MainActivity",
                             "com.h3c.filemanager/.ui.ActivityMain",
                             "com.h3c.store/.components.main.MainActivity",
                             "com.h3c.screenshot/com.h3c.screenshot.ui.MainActivity",
                             "com.h3c.screencap/.ui.ActivityMain"]

        self.app_list = ["setting", "annotation", "fileManger", "store", "screenshot", "screencap"]
        self.name = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.count = 0
        # 启动时间、cpu、内存存放的文件夹名
        self.dirname = time.strftime("%Y%m%d%H%M%S", time.localtime())
        os.mkdir("timeRecord\\" + self.dirname)
        # os.mkdir("system\\" + self.dirname)
        os.mkdir("app\\" + self.dirname)
        self.logger = logging.getLogger()    # 第一步，创建一个logger

    # 日志记录
    def log_record(self):
        # 第一步，创建一个logger
        # logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)  # Log等级开关

        # 第二步，创建一个handler，用于写入日志文件
        log_name = "log\\" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + "_log.log"
        logfile = log_name
        file_handler = logging.FileHandler(logfile, mode='a+')
        file_handler.setLevel(logging.INFO)  # 输出到file的log等级的开关

        # 第三步，定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        file_handler.setFormatter(formatter)

        # 第四步，将handler添加到logger里面
        self.logger.addHandler(file_handler)

        # 如果需要同时需要在终端上输出，定于一個streamHandler
        print_handler = logging.StreamHandler()  # 往屏幕上输出
        print_handler.setFormatter(formatter)  # 设置屏幕上显示的格式
        self.logger.addHandler(print_handler)
        # return logger

    # 判断应用是否正在运行
    def judge_appstate(self, app_name):
        app_list = self.device.app_list_running()
        if app_name in app_list:
            return True
        else:
            return False

    def get_time(self, app_name, filename):
        # 获取应用响应时间
        result = os.popen(f"adb shell am start -W -n {app_name}").read()
        # print(result)
        run_style = str(re.findall(r'LaunchState:(.*?)Activity', result.replace('\n', ''))[0])
        run_wait_time = int(re.findall(r'WaitTime:(.*?)Complete', result.replace('\n', ''))[0])
        with open("timeRecord\\" + self.dirname + "\\" + filename + "_blackboard_2.3.39.1.csv", "a+") as f:
            f.write(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "," + run_style + "," + str(run_wait_time) + "\n")

    def sys_mem_cpu(self):
        cpu_mem_result = os.popen(f"adb shell top -n 1").read().split("\n")
        # Total RAM
        mem_all = str(re.findall(r'Mem: (.*?)K', cpu_mem_result[2].strip())[0])
        # Used RAM
        mem_used = str(re.findall(r'total, (.*?)K used', cpu_mem_result[2].strip())[0])
        # Used RAM / Total RAM
        mem_percent = round((int(mem_used) / int(mem_all)), 4) * 100
        # cpu总占比
        cpu_all = os.popen("adb shell dumpsys cpuinfo | findstr TOTAL").read().split("%")[0]
        # 获取当前gpu
        gpu_used = os.popen("adb shell cat /sys/class/drm/card0/gt_cur_freq_mhz").read()
        # 获取最大gpu
        gpu_max = os.popen("adb shell cat /sys/class/drm/card0/gt_max_freq_mhz").read()
        gpu = int(gpu_used) / int(gpu_max) * 100
        # 将系统cpu和内存写入文件
        with open("system\\" + self.dirname + "_blackboard_2.3.39.1.csv", "a+") as f:
            f.write(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ","
                + str(mem_all) + "," + str(mem_used) + "," + str(mem_percent) + "," + str(cpu_all) + "," + str(gpu) + "\n")

    def app_mem_cpu(self, app_name, filename):
        p = app_name.split("/")[0]
        cpu_mem_result = os.popen(f"adb shell top -n 1").read().split("\n")
        # Total RAM
        mem_all = str(re.findall(r'Mem: (.*?)K', cpu_mem_result[2].strip())[0])
        mem_app = (os.popen(r'adb shell dumpsys meminfo | findstr ' + p).readline())
        # 应用所占内存
        package_mem_used = re.findall(r"([\d,]+)K", mem_app)[0].replace(",", "")
        # 应用占总内存的百分比
        package_men_percent = round(int(package_mem_used) / int(mem_all), 4) * 100
        # 应用cpu占比
        cpu_app = os.popen("adb shell dumpsys cpuinfo | findstr " + p).read().split("%")[0]
        # print(cpu_app)
        if cpu_app != "":
            if cpu_app.strip().startswith("+"):
                cpu_app = int(cpu_app.split("+")[1]) / 8
        else:
            cpu_app = 0
        # 将应用cpu和内存写入文件
        with open("app\\" + self.dirname + "\\" + filename + "_blackboard_2.3.39.1.csv", "a+") as f:
            f.write(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ","
                + str(package_mem_used) + "," + str(package_men_percent) + "," + str(cpu_app) + "\n")

    @outer
    def start_setting(self):
        # 计算setting启动时间
        self.get_time(self.package_name[0], self.app_list[0])
        # 全屏模式下的随机操作
        for i in range(50):
            self.device.click(x=random.randint(1, 3840), y=random.randint(1, 2160))
            if random.randint(0, 1) == 0:
                self.device.swipe(384, 1866, 384, 600)
            else:
                self.device.swipe(384, 600, 384, 1866)

    @outer
    def start_annotation(self):
        # 计算批注启动时间
        self.get_time(self.package_name[1], self.app_list[1])
        time.sleep(2)
        # 随机拖动批注和切换笔/触控状态
        x1 = 1958
        y1 = 1680
        for i in range(50):
            x2 = random.randint(1, 3840)
            y2 = random.randint(1, 2160)
            self.device.swipe(x1, y1, x2, y2)
            time.sleep(1)
            x1, y1 = self.device(resourceId="com.h3c.commentary:id/menuitem_write_main_commentary").center()
        for j in range(50):
            self.device.click(x1, y1)
            time.sleep(2)
        # 退出批注
        self.device(resourceId="com.h3c.commentary:id/menuitem_write_exit_commentary").click()

    @outer
    def start_filemanager(self):
        # 计算文件管理器启动时间
        self.get_time(self.package_name[2], self.app_list[2])
        # 全屏模式下随机操作
        for i in range(50):
            x = random.randint(1, 3840)
            y = random.randint(1, 2160)
            self.device.click(x, y)
            time.sleep(1)

    @outer
    def start_store(self):
        # 计算应用管理中心的启动时间
        self.get_time(self.package_name[3], self.app_list[3])
        # 随机操作
        for i in range(50):
            self.device.click(x=random.randint(1, 3840), y=random.randint(1, 2160))
            if random.randint(0, 1) == 0:
                self.device.swipe(384, 1866, 384, 600)
            else:
                self.device.swipe(384, 600, 384, 1866)

    @outer
    def start_screenshot(self):
        # 截屏之后保存到本地10次
        for i in range(10):
            self.device.app_start("com.h3c.screenshot", "com.h3c.screenshot.ui.MainActivity")
            time.sleep(2)
            # 截全屏
            self.device.click(1000, 1000)
            time.sleep(1)
            self.device(resourceId="com.h3c.screenshot:id/tv_save").click()
            time.sleep(2)
            self.device(resourceId="com.h3c.screenshot:id/btn_save").click()
            time.sleep(2)

        # 截屏之后点击扫码带走，关闭扫码带走弹窗10次
        # self.device.app_start("com.h3c.screenshot", "com.h3c.screenshot.ui.MainActivity")
        # time.sleep(2)
        # for i in range(10):
        #     self.device(resourceId="com.h3c.screenshot:id/tv_scan").click()
        #     time.sleep(5)
        #     self.device(resourceId="com.h3c.screenshot:id/iv_close").click()
        #     time.sleep(1)

        # 打开关闭截屏10次
        for i in range(10):
            self.device.app_start("com.h3c.screenshot", "com.h3c.screenshot.ui.MainActivity")
            time.sleep(2)
            self.device(resourceId="com.h3c.screenshot:id/iv_close").click()
            time.sleep(3)

    @outer
    def start_screencap(self):
        self.device.app_start("com.h3c.screencap", ".ui.ActivityMain")
        # 打开麦克风
        self.device(resourceId="com.h3c.screencap:id/img_mic_start").click()
        # 开始录屏
        self.device(resourceId="com.h3c.screencap:id/btn_start").click()
        time.sleep(100)  # 录屏两分钟
        self.device.click(7311, 1944)     # 点击展开
        time.sleep(1)
        self.device(resourceId="com.h3c.screencap:id/btnStop").click()    # 结束录屏
        time.sleep(100)  # 视频预览两分钟
        # self.device(resourceId="com.h3c.screencap:id/textLocalSave").click()  # 保存到本地
        self.device.click(7219, 2034)      # 保存到本地
        # self.device(resourceId="com.h3c.screencap:id/textConfirm").click()
        self.device.click(5867, 1404)  # 保存
        time.sleep(2)
        # self.device(resourceId="com.h3c.screencap:id/textDownloadSave").click()  # 点击扫码带走
        # time.sleep(2)
        # self.device(resourceId="com.h3c.screencap:id/close").click()              # 关闭扫码带走
        # self.device(resourceId="com.h3c.screencap:id/re_record").click()          # 点击重新录制
        self.device.click(3993, 2034)
        time.sleep(2)
        self.device(resourceId="com.h3c.screencap:id/btn_close").click()          # 关闭录屏

    # 判断设备连接状况
    def judge_connect_state(self):
        if len(os.popen(f"adb devices").read().split("\n")) == 3:
            os.popen(f"adb connect 192.168.4.93")
            # os.popen(f"adb connect 192.168.4.20")

    def start_aging(self):
        with open("system\\" + self.dirname + "_blackboard_2.3.39.1.csv", "a+") as f:
            f.write("OpenTime,all_mem(K),used_mem(K),mem_percent(%),cpu(%),gpu(%)\n")  # title
        for i, app in enumerate(self.app_list):
            self.app_list[i] = app + "_" + self.name
            with open("timeRecord\\" + self.dirname + "\\" + self.app_list[i] + "_blackboard_2.3.39.1.csv", "a+") as f:
                f.write("OpenTime,LaunchState,WaitTime(ms)\n")  # title
            with open("app\\" + self.dirname + "\\" + self.app_list[i] + "_blackboard_2.3.39.1.csv", "a+") as f:
                f.write("OpenTime,package_used_mem(K),package_used_percent(K),cpu_app(%)\n")  # title
        self.log_record()
        for i in range(300):
            try:
                self.judge_connect_state()
                self.start_setting()
                time.sleep(2)
                self.start_annotation()
                time.sleep(2)
                self.start_filemanager()
                time.sleep(2)
                self.start_store()
                time.sleep(2)
                self.start_screenshot()
                time.sleep(2)
                # self.start_screencap()
                # time.sleep(2)
                self.count += 1
                # monkey
                os.popen("adb shell monkey --pct-motion 50 --throttle 1000 --pct-syskeys 0 --ignore-crashes 100")
                time.sleep(110)
            except:
                self.logger.error(str(traceback.format_exc()))
            finally:
                # monkey会唤起关机弹窗
                if self.device(resourceId="com.h3c.launcher:id/img_btn_cancel").exists:
                    self.device(resourceId="com.h3c.launcher:id/img_btn_cancel").click()
               # monkey随机打开批注会报错
                if self.device(resourceId="com.h3c.commentary:id/menuitem_write_exit_commentary").exists:
                    self.device(resourceId="com.h3c.commentary:id/menuitem_write_exit_commentary").click()
                # monkey随机打开截屏无法唤起dock栏
                if self.device(resourceId="com.h3c.screenshot:id/iv_close").exists:
                    self.device(resourceId="com.h3c.screenshot:id/iv_close").click()
                # monkey随机打开版本查看应用无法唤起dock栏
                if self.device(resourceId="com.h3c.app.otaservice:id/btn_positive").exists:
                    self.device(resourceId="com.h3c.app.otaservice:id/btn_positive").click()
                self.device.swipe(1920, 2155, 1920, 1980)  # 上滑呼出dock栏
                # 判断一键下课元素是否存在，再进行点击
                while not self.device(resourceId="com.h3c.launcher:id/iv_finish_class").exists:
                    if "com.h3c.screenshot" in self.device.app_list_running():
                        self.device.app_stop("com.h3c.screenshot")
                    if "com.h3c.commentary" in self.device.app_list_running():
                        self.device.app_stop("com.h3c.commentary")
                    self.device.swipe(5760, 2155, 5760, 1980)  # 上滑呼出dock栏
                    time.sleep(2)
                self.device(resourceId="com.h3c.launcher:id/iv_finish_class").click()  # 点击一键下课
                time.sleep(2)
                self.device(resourceId="com.h3c.launcher:id/btn_positive").click()  # 确定下课，退出所有应用
                time.sleep(3)
            continue
        self.logger.info("总运行次数：%d" % self.count)

    # 开始检测系统、应用性能
    def start_monitor(self):
        while True:
            try:
                self.sys_mem_cpu()
                app_list = self.device.app_list_running()
                for i, app in enumerate(self.package_name):
                    if app.split("/")[0] in app_list:
                        self.app_mem_cpu(app, self.app_list[i])
                time.sleep(3)
            except:
                self.logger.error(str(traceback.format_exc()))
            continue

    def aging_process(self):
        # p_main = multiprocessing.Process(target=self.start_aging)   # 进程无法使用多个popen
        # p_monitor = multiprocessing.Process(target=self.start_monitor, daemon=True)
        p_main = threading.Thread(target=self.start_aging)
        p_monitor = threading.Thread(target=self.start_monitor)
        return p_main, p_monitor


if __name__ == '__main__':
    aging = Aging()
    p_main, p_monitor = aging.aging_process()
    p_monitor.daemon = True
    p_main.start()
    p_monitor.start()

