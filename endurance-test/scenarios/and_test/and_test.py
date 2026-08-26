import subprocess
import time
import re
import datetime
import os
import configparser
import sys

# 配置部分
current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 当前工作目录
print(current_working_dir)
config_path = os.path.join(current_working_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
settings = config['Settings']

DEVICE_IP = settings.get('ip')
interval = settings.getint('interval')

def run_adb_command(command):
    result = subprocess.run(['adb', '-s', DEVICE_IP, 'shell'] + command.split(), capture_output=True, text=True)
    return result.stdout.strip()

def get_battery_level():
    output = run_adb_command('dumpsys battery')
    for line in output.split('\n'):
        if 'level' in line:
            return int(line.strip().split(': ')[1])
    return None

def get_memory_usage():
    output = run_adb_command('dumpsys meminfo')
    total_memory = None
    available_memory = None
    for line in output.split('\n'):
        if 'Total RAM' in line:
            total_memory = int(re.sub(r'\D', '', line.split()[2]))
        elif 'Free RAM' in line:
            available_memory = int(re.sub(r'\D', '', line.split()[2]))
    used_memory = total_memory - available_memory if total_memory and available_memory else None
    memory_usage_ratio = (used_memory / total_memory) * 100 if total_memory and available_memory else None
    return memory_usage_ratio

def get_cpu_usage():
    output = run_adb_command('dumpsys cpuinfo')
    for line in output.split('\n'):
        if 'TOTAL' in line:
            usage_percent = re.search(r'(\d+(\.\d+)?)%', line)
            if usage_percent:
                return float(usage_percent.group(1))
    return None

def get_gpu_usage():
    output = run_adb_command('dumpsys gpu')
    for line in output.split('\n'):
        if 'GpuLoad=' in line:
            gpu_load = re.search(r'GpuLoad=(\d+)', line)
            if gpu_load:
                return int(gpu_load.group(1))
    return None

def get_network_speed():
    output = run_adb_command('cat /proc/net/dev')
    lines = output.split('\n')
    network_data = {}
    for line in lines:
        if 'eth' in line or 'wlan' in line:
            parts = line.split()
            interface = parts[0].strip(':')
            rx_bytes = int(parts[1])
            tx_bytes = int(parts[9])
            rx_MB = rx_bytes / (1024 * 1024)  # 转换为MB
            tx_MB = tx_bytes / (1024 * 1024)  # 转换为MB
            network_data[interface] = {'rx_MB': rx_MB, 'tx_MB': tx_MB}
    return network_data

def get_cpu_frequency():
    output = run_adb_command('cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq')
    return int(output) / 1000 if output else None

def write_device_info_to_file(filename):
    with open(filename, 'a') as file:
        while True:
            try:
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                battery_level = get_battery_level()
                memory_usage = get_memory_usage()
                cpu_usage = get_cpu_usage()
                gpu_usage = get_gpu_usage()
                network_speed = get_network_speed()
                cpu_frequency = get_cpu_frequency()

                # 构建日志信息
                log_entries = [
                    f"当前时间: {current_time}",
                    f"电池电量: {battery_level} %",
                    f"内存占用率: {memory_usage:.2f} %" if memory_usage is not None else "内存占用率: 获取失败",
                    f"CPU 占用率: {cpu_usage:.2f} %" if cpu_usage is not None else "CPU 占用率: 获取失败",
                    f"GPU 占用率: {gpu_usage:.2f} %" if gpu_usage is not None else "GPU 占用率: 获取失败",
                    "网络速度:"
                ]

                for interface, speeds in network_speed.items():
                    log_entries.append(f"接口 {interface}: 下行 (RX): {speeds['rx_MB']:.2f} MB, 上行 (TX): {speeds['tx_MB']:.2f} MB")

                log_entries.append(f"CPU 频率: {cpu_frequency} MHz" if cpu_frequency is not None else "CPU 频率: 获取失败")
                log_entries.append("-" * 20)

                # 将日志信息写入文件和打印到控制台
                for entry in log_entries:
                    file.write(entry + "\n")
                    print(entry)

                file.flush()  # 确保数据立即写入磁盘
                time.sleep(interval)
            except Exception as e:
                print(f"发生错误: {e}")

if __name__ == '__main__':
    # 获取当前时间并格式化为YYYYMMDDHHMMSS
    current_time_str = datetime.datetime.now().strftime('%m%d%H%M')
    # 构建文件名
    output_filename = f'devices_info_{current_time_str}.txt'
    write_device_info_to_file(output_filename)