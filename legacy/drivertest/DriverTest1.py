import wmi

def get_driver_info():
    # 创建 WMI 客户端实例
    c = wmi.WMI()

    print(f"{'Driver Name':<50} {'Manufacturer':<30} {'Version':<20}")
    print("="*100)

    try:
        # 查询 Win32_PnPSignedDriver 获取驱动信息
        drivers = c.Win32_PnPSignedDriver()
        for driver in drivers:
            driver_name = driver.DeviceName if driver.DeviceName else "Unknown"
            manufacturer = driver.Manufacturer if driver.Manufacturer else "Unknown"
            version = driver.DriverVersion if driver.DriverVersion else "Unknown"

            print(f"{driver_name:<50} {manufacturer:<30} {version:<20}")
    except Exception as e:
        print(f"Error retrieving driver information: {e}")

if __name__ == '__main__':
    get_driver_info()