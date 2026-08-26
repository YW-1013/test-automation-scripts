# -*- coding: UTF-8 -*-
import subprocess
from datetime import datetime
import time
from conf import *

path = LOG_ALL_PATH
def get_latest_subdir(path):
    # 获取路径下所有文件夹
    subdirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    # 按照创建时间排序
    sorted_subdirs = sorted(subdirs, key=lambda x: os.path.getctime(x), reverse=True)
    # 返回最新创建的文件夹
    return sorted_subdirs[0]



def get_cpuinfo():
    if IS_REBOOT == "True":
        time.sleep(70)
    else:
        time.sleep(10)
    path_total = os.path.join(get_latest_subdir(path), "cpuinfo.txt")
    while True:
        # 获取当前时间
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        with open(path_total, 'a') as f:
            f.write("\n\n\n\n\n")

        # 将当前时间写入cpuinfo.txt文件中
        with open(path_total, 'a') as f:
            f.write("Current time: {}\n".format(current_time))

        # 执行获取CPU、内存信息的adb命令，并将结果写入cpuinfo.txt文件中
        cmd = f"adb shell top -d 1 -n 1 >> {path_total}"
        subprocess.call(cmd, shell=True)

        # 等待1秒
        time.sleep(1)

        # 尝试连接设备，如果连接失败则等待40秒后重新连接
        try:
            cmd = "adb devices"
            result = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
            if "device" not in result:
                raise Exception("Device not connected.")
        except Exception as e:
            print(e)
            time.sleep(40)
            continue