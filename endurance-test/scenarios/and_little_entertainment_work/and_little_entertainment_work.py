import subprocess
import time
import os
import configparser
import uiautomator2 as u2
import sys
import datetime

# 配置部分
current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 当前工作目录
config_path = os.path.join(current_working_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
settings = config['Settings']

DEVICE_IP = settings.get('ip')
bilibili_duration = settings.getint('bilibili_duration')
douyin_duration = settings.getint('douyin_duration')
meeting_duration = settings.getint('meeting_duration')
PPT_duration = settings.getint('PPT_duration')
feishu_duration = settings.getint('feishu_duration')
file_operation_duration = settings.getint('file_operation_duration')

kill_app_path = os.path.join(current_working_dir, 'kill_app.sh')

def run_command(command):
    process = subprocess.Popen(command, bufsize=10000, stdout=subprocess.PIPE, close_fds=True)
    out = process.communicate()[0]
    if process.stdin: process.stdin.close()
    if process.stdout: process.stdout.close()
    if process.stderr: process.stderr.close()
    try:
        process.kill()
    except OSError:
        pass
    return out.decode()

def connect_to_device():
    # 设置 root 状态
    run_command(f"adb -s {DEVICE_IP} shell setprop persist.h3c.root_state 123@qwe")
    run_command(f"adb -s {DEVICE_IP} root")
    run_command(f"adb -s {DEVICE_IP} push {kill_app_path} /data/local/tmp")

def start_test():
    run_command(f"adb -s {DEVICE_IP} shell chmod 777 /data/local/tmp/kill_app.sh")
    run_command(f"adb -s {DEVICE_IP} shell ./data/local/tmp/kill_app.sh")
    print("已关闭所有应用")
    time.sleep(5)

def start_bilibili_refresh(device):
    # 启动Bilibili应用
    run_command(f'adb -s {DEVICE_IP} shell am start tv.danmaku.bilibilihd/tv.danmaku.bili.MainActivityV2')
    if device(text="我知道了").exists(timeout=5):
        device(text="我知道了").click()

    # 刷新首页内容
    end_time = time.time() + bilibili_duration
    while time.time() < end_time:
        d.swipe_ext('down')
        time.sleep(5)
    run_command(f"adb -s {DEVICE_IP} shell am force-stop tv.danmaku.bilibilihd")


def start_weishi_swipe(device):
    # 启动抖音应用
    run_command(f'adb -s {DEVICE_IP} shell am start com.tencent.weishi/com.tencent.oscar.module.main.MainActivity')
    if device(text="我知道了").exists(timeout=20):
        device(text="我知道了").click()
    # 下滑视频
    end_time = time.time() + douyin_duration
    while time.time() < end_time:
        d.swipe_ext('up')
        time.sleep(10)
    run_command(f"adb -s {DEVICE_IP} shell am force-stop com.tencent.weishi")

def tenxun_meeting(device):
    # 启动腾讯会议应用
    run_command(f'adb -s {DEVICE_IP} shell am start com.tencent.wemeet.app/com.tencent.wemeet.sdk.meeting.premeeting.home.HomeActivity')
    if device(text="取消").exists(timeout=10):
        device(text="取消").click()
    if device(text="入会").exists(timeout=20):
        device(text="入会").click()
    if device(text="姚伟").exists(timeout=20):
        device(text="姚伟").click()
    time.sleep(meeting_duration)
    run_command(f"adb -s {DEVICE_IP} shell am force-stop com.tencent.wemeet.app")

def play_ppt(device):
    try:
        run_command(f"adb -s {DEVICE_IP} shell  mkdir /sdcard/AAA")
    except Exception as makdir_error:
        print(makdir_error)
    print("复制本地的PPT文件到安卓设备")
    run_command(f"adb -s {DEVICE_IP} push {current_working_dir}/test.pptx /sdcard/AAA")
    run_command(f'adb -s {DEVICE_IP} shell am start com.h3c.filemanager/.ui.ActivityMain')
    if device(text="AAA").exists(timeout=20):
        device(text="AAA").click()
    if device(text="test.pptx").exists(timeout=20):
        device(text="test.pptx").click()
    if device(text="WPS Office").exists(timeout=20):
        device(text="WPS Office").click()
    time.sleep(5)
    run_command(f'adb -s {DEVICE_IP} shell input keyevent 135')
    time.sleep(PPT_duration)
    start_test()

def feishu_chat(device):
    run_command(f'adb -s {DEVICE_IP} shell am start com.ss.android.lark/.authorization.AuthorizationActivity')
    if device(text="同意").exists(timeout=20):
        device(text="同意").click()
    if device(text="test").exists(timeout=20):
        device(text="test").click()
    time.sleep(3)

    start_time = time.time()
    while time.time() - start_time < feishu_duration:
        # 发送消息
        device.send_keys("飞书聊天测试")
        device.press('enter')
        # 等待下一次发送
        time.sleep(3)
    run_command(f"adb -s {DEVICE_IP} shell am force-stop com.ss.android.lark")


def file_operations():
    zip_file = "test.zip"  # 压缩文件名
    unzipped_folder = "test"  # 解压后的文件夹名
    sdcard_path = "/sdcard/TestFiles"

    # 时间控制
    start_time = time.time()
    while time.time() - start_time < file_operation_duration:
        print("进行文件拷贝、解压、压缩...")
        time.sleep(3)  # 间隔执行

        # 创建目标目录
        run_command(f"adb -s {DEVICE_IP} shell mkdir -p {sdcard_path}")

        # 拷贝文件到安卓设备
        print("复制本地文件到安卓设备")
        run_command(f"adb -s {DEVICE_IP} push {current_working_dir}/{zip_file} {sdcard_path}/{zip_file}")


        # 解压文件
        print("解压文件")
        run_command(f"adb -s {DEVICE_IP} shell unzip -o {sdcard_path}/{zip_file} -d {sdcard_path}")


        # 压缩文件
        print("压缩文件")
        run_command(f"adb -s {DEVICE_IP} shell \"cd {sdcard_path} && tar -cvf compressed.tar {unzipped_folder}\"")


        # 删除测试文件（调试完成后启用）
        print("删除测试文件")
        run_command(f"adb -s {DEVICE_IP} shell rm -rf {sdcard_path}")

if __name__ == '__main__':

    connect_to_device()

    # 连接到设备
    d = u2.connect(DEVICE_IP)

    times = 0
    while True:

        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:执行一键下课")
        start_test()


        # 刷新Bilibili首页内容
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始刷新 Bilibili 首页内容")
        start_bilibili_refresh(d)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:Bilibili 首页内容刷新完成")

        # 刷新腾讯微视视频
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始刷新腾讯微视视频")
        start_weishi_swipe(d)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:腾讯微视视频刷新完成")

        # 进行腾讯会议
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始进行腾讯会议")
        tenxun_meeting(d)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:腾讯会议完成")

        # 播放PPT
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始播放PPT")
        play_ppt(d)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:播放PPT完成")

        # 进行飞书聊天
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始飞书聊天")
        feishu_chat(d)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:飞书聊天完成")

        # # 进行文件拷贝解压压缩
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始文件操作")
        file_operations()
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:文件操作结束")

        times += 1
        print(f"第{times}轮测试完成")
