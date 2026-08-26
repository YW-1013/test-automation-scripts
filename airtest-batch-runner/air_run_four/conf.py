import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

DEVICES_URL = config.get('device_info', 'device')
DEVICE_PLATFORM = config.get('device_info', 'platform')
DEVICE_INFO = f"{DEVICE_PLATFORM}:///{DEVICES_URL}"

BASE_DIR = os.getcwd()   #当前脚本所在的目录


# 配置文件绝对路径
CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')

# 测试用例目录绝对路径
CASE_PATH = os.path.join(BASE_DIR, config.get('paths', 'name'))
if not os.path.exists(CASE_PATH):
    os.mkdir(CASE_PATH)

# 日志总目录绝对路径
LOG_ALL_PATH = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_ALL_PATH):
    os.mkdir(LOG_ALL_PATH)

#报告名称
REPORT_NAME = config.get('report_name', 'report_name')


#报告模板存放目录
TEMPLATE_REPORT_PATH = os.path.join(BASE_DIR)


#历史报告目录路径
HISTORY_REPORT_PATH = os.path.join(BASE_DIR,"history_logs")

#运行前是否重启一次
IS_REBOOT = config.get('reboot', 'is_reboot')


REBOOT_NUM = config.get('reboot_num', 'reboot_num')

THRESHOLD = config.get('global_settings', 'THRESHOLD')
IMAGE_MAXSIZE = config.get('global_settings', 'IMAGE_MAXSIZE')
SAVE_IMAGE = config.get('global_settings', 'SAVE_IMAGE')

SUIT_SELECT = config.get('suit_select', 'suit_select')

RUN_TIMES = int(config.get('run_times', 'run_times'))


if __name__ == '__main__':
    print(SUIT_SELECT)

