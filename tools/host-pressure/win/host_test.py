import subprocess
import re
import os
import time
import logging
import sys
import win32com.client
import requests

current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 当前工作目录
exe_path = os.path.join(current_working_dir, 'host_test_win_V1.0.exe')
restart_count_file = os.path.join(current_working_dir, 'restart_count.txt')

# 配置日志
def setup_logging():
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 创建文件处理器，将日志写入文件
    file_handler = logging.FileHandler('hotspot_connection.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # 创建控制台处理器，将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def read_restart_count():
    """读取重启次数"""
    if not os.path.exists(restart_count_file):
        logging.info(f"文件 {restart_count_file} 不存在，初始重启次数为 0。")
        return 0
    try:
        with open(restart_count_file, 'r') as file:
            content = file.read().strip()
            if content.isdigit():
                return int(content)
            else:
                logging.warning(f"文件 {restart_count_file} 内容无效，初始重启次数为 0。")
                return 0
    except Exception as e:
        logging.error(f"读取文件 {restart_count_file} 失败: {e}")
        return 0

def write_restart_count(count):
    """写入重启次数"""
    try:
        with open(restart_count_file, 'w') as file:
            file.write(str(count))
        logging.info(f"重启次数已更新为: {count}")
    except Exception as e:
        logging.error(f"写入文件 {restart_count_file} 失败: {e}")

def get_connected_devices():
    """获取连接到热点的设备 IP 地址"""
    result = subprocess.run(['netsh', 'wlan', 'show', 'hostednetwork'], capture_output=True, text=True)
    if "No clients are connected" in result.stdout:
        logging.warning("没有设备连接到热点。")
        return []
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    ip_pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
    connected_ips = ip_pattern.findall(result.stdout)
    filtered_ips = [ip for ip in connected_ips if ip.startswith('192.168.137.') and ip not in ['192.168.137.1', '192.168.137.255']]
    if filtered_ips:
        logging.info(f"连接到热点的设备 IP 地址：{filtered_ips}")
    else:
        logging.warning("没有设备连接到192.168.137.x网段（排除192.168.137.1和192.168.137.255）。")
    return filtered_ips

def ping_ip(ip):
    """Ping 指定的 IP 地址，兼容中文和英文输出"""
    response = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], capture_output=True, text=True)
    # 检查中文和英文的 Ping 成功关键词
    if "回复" in response.stdout or "Reply from" in response.stdout:
        logging.info(f"IP {ip} 可以 Ping 通。")
        return True
    else:
        logging.warning(f"与 IP {ip} Ping 不通。")
        return False

def restart_windows():
    """重启 Windows 系统"""
    logging.info("正在重启 Windows 系统...")
    os.system('shutdown /r /t 1')

def task_exists(scheduler, task_name):
    """检查任务是否已经存在"""
    try:
        root_folder = scheduler.GetFolder("\\")
        task = root_folder.GetTask(task_name)
        return task is not None
    except Exception as e:
        return False

def create_task_xml(executable_path, working_directory, script_args=None, delay_seconds=30):
    task_name = 'host_test_task'
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

        # Debug 打印日志查看XML内容是否正确
        print(task_xml)

        # 通过任务计划程序注册任务
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        # 检查任务是否已存在
        if task_exists(scheduler, task_name):
            logging.info(f'任务 "{task_name}" 已存在，取消创建')
            return

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
        logging.info(f'{task_name}任务成功创建')

    except Exception as e:
        print(f"任务创建失败，失败原因为： {e}")

def push_report(web_hook, message_body):
    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    ChatRob = requests.post(url=web_hook, json=message_body, headers=header)
    opener = ChatRob.json()
    logging.info("opener:{}".format(opener))
    if opener["StatusMessage"] == "success":
        logging.info(u"%s 通知消息发送成功！" % opener)
    else:
        logging.info(u"通知消息发送失败，原因：{}".format(opener))

def send_message():
    webhook = 'YOUR_FEISHU_WEBHOOK_URL'
    message_body = {
        "msg_type": "text",
        "content": {
            "text": f"热点连接失败，请检查机器状态"
        }
    }
    push_report(webhook, message_body)

def main():
    setup_logging()  # 初始化日志配置

    # 在脚本的最开始读取并更新重启次数
    restart_count = read_restart_count()
    restart_count += 1
    write_restart_count(restart_count)

    retry_count = 20
    retry_delay = 30  # 重试间隔时间（秒）
    logging.warning("程序启动延时30S")
    time.sleep(30)  # 程序启动等待30S
    create_task_xml(exe_path, current_working_dir, script_args=None, delay_seconds=30)
    for attempt in range(retry_count):
        logging.info(f"尝试第 {attempt + 1} 次...")
        connected_ips = get_connected_devices()
        if not connected_ips:
            logging.warning("没有 IP 连接到设备。")
        else:
            for ip in connected_ips:
                if ping_ip(ip):
                    logging.info("至少有一个设备 IP 可以 Ping 通，准备重启系统。")
                    restart_windows()
        if attempt < retry_count - 1:
            logging.info(f"等待 {retry_delay} 秒后重试...")
            time.sleep(retry_delay)
    logging.error("重试多次后仍出现问题，热点未被连接，已出现问题，请检查")
    send_message()
if __name__ == "__main__":
    main()