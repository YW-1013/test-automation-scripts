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
play_bilibili_duration = settings.getint('play_bilibili_duration')

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

def start_wangyiyun(device):
    # 启动网易云
    run_command(f'adb -s {DEVICE_IP} shell am start com.netease.cloudmusic/.activity.MainActivity')
    if device(text="每日推荐").exists(timeout=20):
        device(text="每日推荐").click()
    # if device(text="VIP热歌榜").exists(timeout=20):
    #     device(text="VIP热歌榜").click()
    if device(text="播放全部").exists(timeout=20):
        device(text="播放全部").click()

def tenxun_meeting(device):
    # 启动腾讯会议应用
    run_command(f'adb -s {DEVICE_IP} shell am start com.tencent.wemeet.app/com.tencent.wemeet.sdk.meeting.premeeting.home.HomeActivity')
    if device(text="取消").exists(timeout=10):
        device(text="取消").click()
    if device(text="入会").exists(timeout=20):
        device(text="入会").click()
    if device(text="姚伟").exists(timeout=20):
        device(text="姚伟").click()

def play_1080p_video(device):
    run_command(f'adb -s {DEVICE_IP} shell am start tv.danmaku.bilibilihd/tv.danmaku.bili.MainActivityV2')
    if device(text="我知道了").exists(timeout=5):
        device(text="我知道了").click()
    device.xpath('//*[@resource-id="tv.danmaku.bilibilihd:id/expand_search"]').click()
    time.sleep(5)
    device.send_keys("1080p")
    if device(text="1080p视频").exists(timeout=10):
        device(text="1080p视频").click()
    time.sleep(5)
    device(text='【1080P高清】暖心励志动画短片 合集 持续更新中').click()
    time.sleep(0.5)
    device.xpath('//*[@resource-id="tv.danmaku.bilibilihd:id/bbplayer_halfscreen_expand"]').click()
    time.sleep(play_bilibili_duration)
    run_command(f"adb -s {DEVICE_IP} shell am force-stop tv.danmaku.bilibilihd")


if __name__ == '__main__':

    connect_to_device()

    # 连接到设备
    d = u2.connect(DEVICE_IP)

    times = 0
    while True:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:执行一键下课")
        start_test()

        # 网易云音乐播放
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始网易云音乐播放")
        start_wangyiyun(d)

        # 腾讯会议
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始腾讯会议")
        tenxun_meeting(d)

        # B站观看1080P视频
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:开始B站观看1080P视频")
        play_1080p_video(d)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:B站观看1080P视频完成")

        times += 1
        print(f"第{times}轮测试完成")
