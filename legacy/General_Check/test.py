import clr  # 导入扩展模块
import os  # 导入操作系统模块

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建LibreHardwareMonitorLib.dll的完整路径
dll_path = os.path.join(script_dir, 'LibreHardwareMonitorLib.dll')
print(dll_path)

# 将LibreHardwareMonitorLib.dll添加到CLR的引用中
clr.AddReference(dll_path)

# 从LibreHardwareMonitor模块中导入Hardware类
from LibreHardwareMonitor import Hardware

# 创建一个Hardware.Computer的实例对象
computer_tmp = Hardware.Computer()

computer_tmp.IsCpuEnabled = True  # 获取CPU
computer_tmp.IsGpuEnabled = True  # 获取GPU

# 打开硬件监视器
computer_tmp.Open()

# 设置要获取的CPU和GPU温度数量
num_cpu_temps = 9  # 例如设置为4

# 声明空数组，用于存储温度数据
cpu_temperatures = []

# 遍历所有硬件对象
for hardware in computer_tmp.Hardware:
    # 将硬件类型转换为字符串
    hardware_type = str(hardware.HardwareType)

    # 如果硬件类型包含CPU并且CPU温度数据未达到预设数量
    if 'CPU' in hardware_type.upper() and len(cpu_temperatures) < num_cpu_temps:
        # 更新硬件数据
        hardware.Update()

        # 遍历硬件的传感器
        for sensor in hardware.Sensors:
            # 如果传感器类型是温度
            if sensor.SensorType == Hardware.SensorType.Temperature:
                # 输出本次获取到的CPU温度
                # print(sensor.Name, "温度：", sensor.Value)
                # 将CPU温度值添加到数组中
                cpu_temperatures.append(sensor.Value)
                # 如果已达到预设的CPU温度数量，停止获取更多数据
                if len(cpu_temperatures) == num_cpu_temps:
                    break
if cpu_temperatures:
    max_cpu_temp = max(cpu_temperatures)
    print("CPU最高温度：", max_cpu_temp)
else:
    print("未获取到CPU温度信息")
