# 重启 / 开关机稳定性压测 reboot-stress

> 带 GUI 的 Windows 平板**重启/开关机循环压测工具**：每轮开关机后自动做多项硬件与系统自检，用于暴露"反复上下电后驱动丢失、外设失联、系统服务异常、桌面组件丢失"等稳定性问题。

---

## 检测项（每轮开关机后自动执行）

1. **驱动异常检测**：WMI `ConfigManagerErrorCode != 0` 判定异常设备。
2. **系统事件日志**：采集 Critical 级别事件（仅记录，不计入失败——开机固有事件如 EventID 10111/10120 会被排除）。
3. **关键系统服务**：检查关键服务运行状态。
4. **充电状态检测**（可选）：跳过 / 充电中 / 未充电。
5. **光感传感器检测**（可选）：通过 PowerShell WinRT 读取 ALS 数值，低于阈值 lux 判异常（覆盖"自动亮度读数归零"bug）。
6. **外接 U 盘识别**（按卷标名）。
7. **外接显示器识别**（按设备名）。
8. **蓝牙设备识别**：PowerShell `Get-PnpDevice` 按 InstanceId 前缀（BTHENUM/BTHHFENUM/BTHLE）枚举已配对外设。

## 设计要点

- **GUI 可配置**：CustomTkinter/Tkinter 界面，检测项、阈值、外设名（U盘/显示器/蓝牙多选）均可勾选配置，打开弹窗时自动刷新当前设备列表。
- **异常即停选项**：`stop_on_error` 可选，检测失败时停止压测不再重启，便于保留现场。
- **误报治理**：从版本迭代看，大量工作用于区分"真异常"与"开机固有事件/传感器读取失败"，减少误报。

## 技术栈

`Python 3` · `tkinter` / `customtkinter`（GUI）· `wmi` / `win32com` / `psutil`（系统信息）· `PowerShell`（PnpDevice / WinRT 传感器）· `PyInstaller`

> 运行需管理员权限；打包 exe 与日志未入库。

---

*遵循仓库根目录 [MIT License](../LICENSE)。*
