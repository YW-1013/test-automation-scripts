import os
import subprocess
import time
from retry import retry
import logging
import re
import sys

def setup_logger():
    # 第一步，创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级开关
    current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 当前工作目录
    # 创建文件输出处理器
    log_dir = os.path.join(current_working_dir, "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, '{}.log'.format(time.strftime("%Y%m%d_%H%M%S", time.localtime())))
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 第三步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)

    # 第四步，将handler添加到logger里面
    logger.addHandler(file_handler)

    # 如果需要同时需要在终端上输出，定于一個streamHandler
    print_handler = logging.StreamHandler()  # 往屏幕上输出
    print_handler.setFormatter(formatter)  # 设置屏幕上显示的格式
    logger.addHandler(print_handler)

    return logger

# 禁用启用网卡
def refresh_interface():
    os.popen('netsh interface set interface name="WLAN" admin=disable')
    time.sleep(2)
    os.popen('netsh interface set interface name="WLAN" admin=enable')

@retry((AttributeError))
def get_wlan_msg():
    hotspot_msg = os.popen('netsh wlan show interfaces').read()

    ssid = re.search(r'SSID(.+)\n', hotspot_msg).group(1).split(': ')[1]
    channel = re.search(r'信道(.+)\n', hotspot_msg).group(1).split(': ')[1]
    w_type = re.search(r'无线电类型(.+)\n', hotspot_msg).group(1).split(': ')[1]
    return ssid, channel, w_type

if __name__ == '__main__':
    logger = setup_logger()
    hotspot_name = input('连接至待压测热点后，输入热点名称：')
    channel_dict = {}
    ip = '192.168.137.1'
    err = 0


    for i in range(1, 1000):
        logger.info(f'==========第{i}次重启机器==========')
        subprocess.Popen(f'adb connect {ip}')
        time.sleep(2)
        subprocess.Popen(f'adb -s {ip} reboot')
        logger.info('重启机器，等待60s')
        time.sleep(60)

        for j in range(1, 6):
            logger.info(f'第{j}次尝试连接热点')
            connect_wlan = subprocess.run(f'netsh wlan connect {hotspot_name}', stdout=subprocess.PIPE)
            logger.info(f'连接热点{hotspot_name}:' + connect_wlan.stdout.decode('gbk'))
            time.sleep(15)
            ssid, channel, w_type = get_wlan_msg()
            last_channel = channel
            if ssid == hotspot_name:
                logger.info('成功连接到热点')
                logger.info(f'当前WiFi无线电类型为：{w_type}')
                if int(channel) <= 13:
                    logger.info('当前WiFi为2.4G频段')
                    err += 1
                else:
                    logger.info('当前WiFi为5G频段')
                logger.info(f'累计出现{err}次2.4G频段')

                logger.info(f'当前信道为{channel}')
                if channel in channel_dict:
                    channel_dict[channel] += 1
                else:
                    channel_dict[channel] = 1
                for channel, count in channel_dict.items():
                    logger.info(f'信道{channel} 出现了 {count} 次')
                break
            else:
                logger.info('无法连接到热点,刷新WiFi列表')
                refresh_interface()
                time.sleep(15)



        for i in range(10):
            ssid, channel, w_type = get_wlan_msg()
            if channel != last_channel:
                logger.error(f'当前信道为{channel},信道发生变化！！')
                if channel in channel_dict:
                    channel_dict[channel] += 1
                else:
                    channel_dict[channel] = 1
                if int(channel) <= 13:
                    logger.info('当前WiFi为2.4G频段')
                    err += 1
                else:
                    logger.info('当前WiFi为5G频段')
                logger.info(f'累计出现{err}次2.4G频段')
                last_channel = channel
            else:
                logger.info(f'当前信道为{channel},信道无变化')
                last_channel = channel



            time.sleep(15)