import wmi
from win32pdh import PDH_FMT_DOUBLE
from win32pdh import OpenQuery, CloseQuery, AddCounter
from win32pdh import CollectQueryData, GetFormattedCounterValue
import time

device_list = [ 'Intel(R) AI Boost', '受信任的平台模块 2.0','Intel Processor','Bosch Accelerometer',  'Vishay Ambient Light Sensor', '磁盘驱动器','标准 NVM Express 控制器','Microsoft 存储空间控制器','Microsoft AC 适配器', '通用即插即用监视器', 'PS/2 标准键盘','HID Keyboard Device','英特尔(R) 无线 Bluetooth(R)','Bluetooth Device (RFCOMM Protocol TDI)','I2C HID 设备','符合 HID 标准的触摸屏','符合 HID 标准的手写笔', 'Intel(R) Dynamic Tuning Technology','Facial Recognition (Windows Hello) Software Device','适用于 USB 音频的英特尔® 智音技术', 'Realtek Audio Effects Component', 'Intel(R) Wi-Fi 7 BE200 320MHz','Intel(R) Platform Monitoring Technology (PMT) Driver','Intel(R) Arc(TM) 130V GPU (8GB)','USB 视频设备']


STATUS_CODES = {
            0: "正常",
            1: "配置错误",
            2: "未分配资源",
            3: "筛选器驱动加载失败",
            4: "驱动加载失败",
            5: "注册表损坏",
            6: "需要重启",
            7: "部分配置失败",
            8: "未签名驱动",
            9: "未知设备",
            10: "需要重新启动",
            11: "配置冲突",
            12: "需要进一步配置",
            13: "硬件不存在",
            14: "驱动加载失败",
            15: "启动失败",
            16: "已禁用",
            17: "系统故障",
            18: "未找到驱动",
            19: "被策略禁用",
            20: "设备不存在",
            21: "需要重新扫描",
            22: "驱动程序未安装",
            23: "需要验证配置",
            24: "需要重新安装驱动",
            25: "部分配置信息丢失",
            26: "需要驱动程序安装",
            27: "未知配置问题",
            28: "设备被阻止",
            29: "遗留设备",
            30: "驱动兼容性问题",
            31: "需要用户干预"
        }


def get_all_devices():
    """获取所有设备及其状态码"""
    c = wmi.WMI()
    devices = {}

    # 获取正常设备
    for item in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
        if item.Description:
            devices[item.Description] = 0

    # 获取异常设备
    for error_code in STATUS_CODES:
        if error_code == 0: continue
        for item in c.Win32_PnPEntity(ConfigManagerErrorCode=error_code):
            if item.Description:
                devices[item.Description] = error_code
    return devices


def check_abnormal_devices(target_devices=[]):
    """检查并返回异常设备列表"""
    all_devices = get_all_devices()
    check_list = target_devices + list(all_devices.keys())

    abnormal = []
    for desc in check_list:
        status_code = all_devices.get(desc, -1)
        if status_code == -1:
            abnormal.append((desc, "未找到", "设备不存在"))
        elif status_code != 0:
            reason = STATUS_CODES.get(status_code, "未知状态码")
            abnormal.append((desc, "异常", reason))

    return abnormal


def check_all_driver():
    # 获取异常设备列表
    abnormal_devices = check_abnormal_devices(device_list)

    # 输出异常设备表格
    if abnormal_devices:
        log_content = f"设备异常 {len(abnormal_devices)} 个\n"
        log_content += "\n".join(
            [f"异常设备名称：{d[0]}；异常原因：{d[2]}"
             for d in abnormal_devices]
        )
        print(log_content)

    else:
        print("所有设备状态正常")


def get_freq():
    ncores = 8

    paths = []
    counter_handles = []
    query_handle = OpenQuery()
    for i in range(ncores):
        paths.append("\Processor Information(0,{:d})\% Processor Performance".format(i))
        counter_handles.append(AddCounter(query_handle, paths[i]))

    CollectQueryData(query_handle)
    time.sleep(1)
    CollectQueryData(query_handle)

    freq = []
    for i in range(ncores):
        (counter_type, value) = GetFormattedCounterValue(counter_handles[i], PDH_FMT_DOUBLE)
        freq.append(value * 2.10 / 100)
        # 2.496 is my base speed, I didn't spend time to automate this part

    # print("{:.3f} Ghz".format(max(freq)))
    CloseQuery(query_handle)
    return "{:.3f} GHz".format(max(freq))



if __name__ == "__main__":
    check_all_driver()
    input("输入任意键退出")
