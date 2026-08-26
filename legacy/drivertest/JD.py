import uiautomator2 as u2
import subprocess
import time
import schedule
from datetime import datetime

ip = '2af98a2b'
# 连接到设备
# subprocess.Popen(f'adb connect {ip}')
d = u2.connect(ip)


def schedule_task(target_time):
    while True:
        current_time = datetime.now().strftime('%H:%M:%S')  # 当前时间，精确到毫秒
        # 提取小时、分钟、秒和毫秒进行比较
        if current_time == target_time:
            # d(text="结算").click()
            d(text="提交订单").click()
            break
        time.sleep(0.001)  # 休眠1毫秒，降低CPU使用率


if __name__ == "__main__":
    # 定义任务要在什么时候运行，格式为 'HH:MM:SS.sss'
    target_time = '20:00:00'
    print("Waiting to execute task at", target_time)
    schedule_task(target_time)