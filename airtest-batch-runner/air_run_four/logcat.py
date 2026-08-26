# -*- coding: UTF-8 -*-
from datetime import datetime, date
from conf import *
import os
import subprocess
import time

path = LOG_ALL_PATH

def get_latest_subdir(path):
    # 获取路径下所有文件夹
    subdirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    # 按照创建时间排序
    sorted_subdirs = sorted(subdirs, key=lambda x: os.path.getctime(x), reverse=True)
    # 返回最新创建的文件夹
    return sorted_subdirs[0]

def logcat_time():
    if IS_REBOOT == "True":
        time.sleep(70)
    else:
        time.sleep(10)
    logcat_file = os.path.join(get_latest_subdir(path),"logcat.txt")  # 日志文件路径
    retry_max_times = 30000  # 最大重试次数
    retry_interval = 20  # 重试间隔（秒）
    last_logcat_time = 0  # 上一次日志写入时间

    while True:
        # 检查 adb 连接状态
        devices = os.popen("adb devices").read().strip().split('\n')[1:]
        if len(devices) == 0:
            print("没有找到设备，请检查设备连接状态！")
            time.sleep(retry_interval)
            continue

        # 获取日志
        try:
            # 检查日志目录是否存在
            os.makedirs(os.path.dirname(logcat_file), exist_ok=True)

            # 检查文件是否存在，获取上一次日志写入时间
            if os.path.exists(logcat_file):
                last_logcat_time = os.path.getmtime(logcat_file)

            # 执行 logcat 命令，将日志输出到文件中
            with open(logcat_file, 'a', encoding='utf-8') as f:
                cmd = "adb logcat -v time"
                if last_logcat_time > 0:
                    cmd += " -T %.3f" % last_logcat_time
                subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, check=True, shell=True)

        except subprocess.CalledProcessError as e:
            print("执行 logcat 命令出错：", e)
            retry_max_times -= 1
            if retry_max_times <= 0:
                print("已达到最大重试次数，程序退出！")
                break
            else:
                print("等待 %d 秒后重试..." % retry_interval)
                time.sleep(retry_interval)
                continue

        except KeyboardInterrupt:
            print("用户中断程序，退出！")
            break

# if __name__ == '__main__':
#     logcat_time()