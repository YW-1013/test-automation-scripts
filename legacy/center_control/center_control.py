import datetime
import time
import uiautomator2 as u2
import subprocess

ip_control = "192.168.1.100"
ip_power = "192.168.1.100"

subprocess.Popen(f'adb connect {ip_control}')
# 连接设备
d1 = u2.connect(ip_control)

def run_command(command):
    process = subprocess.Popen(
        command,
        bufsize=10000,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    out, err = process.communicate()

    # 没有必要关闭 process.stdin, 因为没有使用
    if process.stdout:
        process.stdout.close()
    if process.stderr:
        process.stderr.close()

    try:
        process.kill()
    except OSError:
        pass

    return out.decode()

def get_adb_devices():
    # 运行 'adb devices' 命令并解析设备列表
    output = run_command('adb devices')
    devices = output.strip().split('\n')[1:]
    return devices

a = 1
while True:
    print(f"{datetime.datetime.now()}:第{a}次关机")
    d1.click(400, 864) # 点击关机
    time.sleep(60)
    subprocess.Popen(f'adb connect {ip_power}')
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    print(devices)
    if f"{ip_power}:5555" in device_status.keys() and device_status[f"{ip_power}:5555"].strip() == 'device':
        raise RuntimeError("设备未成功关机")
    else:
        print("成功关机")
    print(f"{datetime.datetime.now()}:第{a}次开机")
    d1.click(230, 864)
    time.sleep(100)
    subprocess.Popen(f'adb connect {ip_power}')
    devices = get_adb_devices()
    device_status = {device.split('\t')[0]: device.split('\t')[1] for device in devices}
    print(devices)
    if f"{ip_power}:5555" not in device_status.keys() or device_status[f"{ip_power}:5555"].strip() != 'device':
        raise RuntimeError("设备未成功开机")
    else:
        print("成功开机")
    print(f"第{a}轮测试通过")
    a += 1
    print("=================================================================================================================")