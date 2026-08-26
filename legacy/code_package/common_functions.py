import requests
import re
import json
import time
import datetime
import struct
import socket
import select
import subprocess
import pywifi
from pywifi import const

run_number = 0
run_success = 0
run_fail = 0
time_stamp = 0

wifi_name = "H3C-F7B5z"
wifi_password = "YOUR_WIFI_PASSWORD"


def chesksum(data):
    n = len(data)
    m = n % 2
    sum = 0
    for i in range(0, n - m, 2):
        sum += (data[i]) + ((data[i + 1]) << 8)  # 传入data以每两个字节（十六进制）通过ord转十进制，第一字节在低位，第二个字节在高位
    if m:
        sum += (data[-1])
    # 将高于16位与低16位相加
    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)  # 如果还有高于16位，将继续与低16位相加
    answer = ~sum & 0xffff
    #  主机字节序转网络字节序列（参考小端序转大端序）
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body):
    #  把字节打包成二进制数据
    icmp_packet = struct.pack('>BBHHH32s', data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body)
    icmp_chesksum = chesksum(icmp_packet)  # 获取校验和
    #  把校验和传入，再次打包
    icmp_packet = struct.pack('>BBHHH32s', data_type, data_code, icmp_chesksum, data_ID, data_Sequence, payload_body)
    return icmp_packet


def raw_socket(dst_addr, icmp_packet):
    '''
       连接套接字,并将数据发送到套接字
    '''
    # 实例化一个socket对象，ipv4，原套接字，分配协议端口
    rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    # 记录当前请求时间
    send_request_ping_time = time.time()
    # 发送数据到网络
    rawsocket.sendto(icmp_packet, (dst_addr, 80))
    # 返回数据
    return send_request_ping_time, rawsocket, dst_addr


def reply_ping(send_request_ping_time, rawsocket, data_Sequence, timeout=2):
    while True:
        # 开始时间
        started_select = time.time()
        # 实例化select对象，可读rawsocket，可写为空，可执行为空，超时时间
        what_ready = select.select([rawsocket], [], [], timeout)
        # 等待时间
        wait_for_time = (time.time() - started_select)
        # 没有返回可读的内容，判断超时
        if what_ready[0] == []:  # Timeout
            return -1
        # 记录接收时间
        time_received = time.time()
        # 设置接收的包的字节为1024
        received_packet, addr = rawsocket.recvfrom(1024)
        # 获取接收包的icmp头
        # print(icmpHeader)
        icmpHeader = received_packet[20:28]
        # 反转编码
        type, code, checksum, packet_id, sequence = struct.unpack(
            ">BBHHH", icmpHeader
        )

        if type == 0 and sequence == data_Sequence:
            return time_received - send_request_ping_time

        # 数据包的超时时间判断
        timeout = timeout - wait_for_time
        if timeout <= 0:
            return -1


def dealtime(dst_addr, sumtime, shorttime, longtime, accept, i, time):
    sumtime += time
    print(sumtime)
    if i == 4:
        print("{0}的Ping统计信息：".format(dst_addr))
        print(
            "数据包：已发送={0},接收={1}，丢失={2}（{3}%丢失），\n往返行程的估计时间（以毫秒为单位）：\n\t最短={4}ms，最长={5}ms，平均={6}ms".format(i + 1, accept,
                                                                                                          i + 1 - accept,
                                                                                                          (
                                                                                                                      i + 1 - accept) / (
                                                                                                                      i + 1) * 100,
                                                                                                          shorttime,
                                                                                                          longtime,
                                                                                                          sumtime))
def ping(host):
    send, accept, lost = 0, 0, 0
    sumtime, shorttime, longtime, avgtime = 0, 1000, 0, 0
    # TODO icmp数据包的构建
    data_type = 8  # ICMP Echo Request
    data_code = 0  # must be zero
    data_checksum = 0  # "...with value 0 substituted for this field..."
    data_ID = 0  # Identifier
    data_Sequence = 1  # Sequence number
    payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'  # data

    # 将主机名转ipv4地址格式，返回以ipv4地址格式的字符串，如果主机名称是ipv4地址，则它将保持不变
    dst_addr = socket.gethostbyname(host)
    # print("正在 Ping {0} [{1}] 具有 32 字节的数据:".format(host, dst_addr))
    for i in range(0, 4):
        send = i + 1
        # 请求ping数据包的二进制转换
        icmp_packet = request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence + i, payload_body)
        # 连接套接字,并将数据发送到套接字
        send_request_ping_time, rawsocket, addr = raw_socket(dst_addr, icmp_packet)
        # 数据包传输时间
        times = reply_ping(send_request_ping_time, rawsocket, data_Sequence + i)
        if times > 0:
            print("来自 {0} 的回复: 字节=32 时间={1}ms".format(addr, int(times * 1000)))

            accept += 1
            return_time = int(times * 1000)
            sumtime += return_time
            if return_time > longtime:
                longtime = return_time
            if return_time < shorttime:
                shorttime = return_time
            time.sleep(0.7)
        else:
            lost += 1
            return False

        if send == 4:
            if i == 3:
                return True



def push_report(web_hook,message_body):
    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    try:
        ChatRob = requests.post(url=web_hook, json=message_body, headers=header)
        opener = ChatRob.json()
        print("opener:{}".format(opener))
        if opener["StatusMessage"] == "success":
            print(u"%s 通知消息发送成功！" % opener)
        else:
            print(u"通知消息发送失败，原因：{}".format(opener))
    except:
        print("本次消息推送失败了")
# message_body = {
#     "msg_type": "text",
#     "content": {
#         "text": "测试项目：京东项目压测\n" +
#                 f">>测试项：{type5} \n" +
#                 f">>总次数：{run_number} \n" +
#                 f">>失败次数：{run_fail} \n" +
#                 f">>成功次数：{run_success} \n" +
#                 ">>本次测试结果：%s \n" % code_response5.text
#     }
#
# }
# webhook = 'YOUR_FEISHU_WEBHOOK_URL'
# push_report(webhook, message_body)


def get_time(a):
    current_now_time = datetime.datetime.now()
    # print(current_now_time)
    add_num_time = current_now_time + datetime.timedelta(seconds=a)
    # print(add_num_time)
    add_num_time = str(add_num_time)
    return add_num_time


def get_task_token1():
    url1 = "https://your-server.example.com/auth/login?auth_type=user&username=YOUR_ACCOUNT&password=YOUR_PASSWORD"
    res1 = requests.post(url=url1).text
    # print(res1)
    token1 = (re.findall(r'"token":"(.*?)","refreshedToken"', res1, re.S))
    token1 = token1[0]
    return token1

def get_task_token2(token):
    url2 = "https://your-server.example.com/auth/login?auth_type=choose_tenant&phoneNumber=YOUR_ACCOUNT&tenantId=212"
    headers1 = {"Authorization": token}
    res2 = requests.post(url=url2, headers=headers1).text
    token2 = (re.findall(r'"token":"(.*?)","refreshedToken"', res2, re.S))
    token2 = token2[0]
    return token2

def get_task_token3():
    url = "https://your-server.example.com/auth/login?auth_type=wisdom&serialNumber=YOUR_DEVICE_SN&secret=YOUR_SECRET"
    payload = {}
    response = requests.request("POST", url, data=payload).text
    token3 = (re.findall(r'"token":"(.*?)","refreshedToken"', response, re.S))
    return token3

def push_task(add_num_time):
    token1 = get_task_token1()  # 获取第一个token
    token2 = get_task_token2(token1)  # 获取第二个token
    url3 = "https://your-server.example.com/wisdom/task/time"
    headers2 = {'Authorization': token2,
                'User-Agent': 'apifox/1.0.0 (https://www.apifox.cn)',
                'Content-Type': 'application/json'}

    payload = json.dumps({
        "name": "全部项目的压测",
        "executeType": "ONCE",
        "values": [],
        "executeTime": add_num_time,
        "serialNumbers": ["YOUR_DEVICE_SN"],
        "deviceSelection": "PORTION",
        "instructName": "RESTART"
    })
    res = requests.request("post", url=url3, headers=headers2, data=payload)
    return res


#重启网卡
def restart_wifi_adapter():
    try:
        # 执行命令来重启网卡
        subprocess.run(["netsh", "interface", "set", "interface", "WLAN", "admin=disable"])
        time.sleep(5)
        # subprocess.run(["netsh", "interface", "set", "interface", "WLAN", "admin=enable"])
        time.sleep(5)
        print("Wi-Fi adapter restarted successfully.")
        time.sleep(20)
    except:
        print("已重启网卡")
    time.sleep(60)


#获取当前可连接wifi列表
def get_wifi_list():
    wifi_list = []
    result = subprocess.check_output(['netsh', 'wlan', 'show', 'network'])
    result = result.decode('gbk')
    lst = result.split('\r\n')
    lst = lst[4:]
    for index in range(len(lst)):
        # if index % 5 == 0:
        if lst[index].startswith("SSID"):
            wifi_name = lst[index]
            try:
                wifi_name1 = wifi_name.split(":")[1]
            except IndexError:
                continue
            else:
                wifi_list.append(wifi_name1.strip())
    return(wifi_list)

def connect_wifi(ssid,passwoed):
    wifi = pywifi.PyWiFi()
    ifaces = wifi.interfaces()[0]
    ifaces.disconnect()
    time.sleep(1)
    wifistatus = ifaces.status()
    if wifistatus == const.IFACE_DISCONNECTED:
        ifaces.scan()
        time.sleep(2)
        SSIDS = ifaces.scan_results()
        ssid = ssid#输入要连接的WiFi名称
        pswd = passwoed#输入要连接的WiFi密码
        for SSID in SSIDS:
            #检查是否扫描到对于wifi
            if SSID.ssid == ssid:
                profile = pywifi.Profile()
                profile.ssid = SSID.ssid
                profile.auth = const.AUTH_ALG_OPEN
                profile.akm.append(const.AKM_TYPE_WPA2PSK)
                profile.cipher = const.CIPHER_TYPE_CCMP
                profile.key = pswd
                ifaces.remove_all_network_profiles()
                tep_profile = ifaces.add_network_profile(profile)
                ifaces.connect(tep_profile)
                time.sleep(5)
                if ifaces.status() == const.IFACE_CONNECTED:
                    print("Link:OK")
                    return True
                else:
                    print("WifiPassword:NG")
                    return False


#获取已连接的wifi名称
def get_connected_wifi_name():
    # 抓取网卡接口
    wifi = pywifi.PyWiFi()
    # 获取无线网卡
    ifaces = wifi.interfaces()[0]
    # 获取无线网卡信息
    profile = ifaces.scan_results()[0]
    # 获取名字
    return profile.ssid




