# legacy · 早期 / 存档脚本

> ⚠️ 本目录收录的是**早期版本或已被新版取代**的测试脚本，仅作技术存档与思路参考，**不代表当前最佳实现**。其中不少能力已在仓库其它模块以更完善的形式重写（如 `tools/`、`driver-verify/`、`reboot-stress/` 等）。
>
> 🔒 所有硬编码的账号、密码、飞书应用凭证、设备 SN、内网 IP/域名、DB/邮箱配置均已脱敏为占位符；真实配置不入库，仅保留 `*.example.*` 模板。

---

## 脚本清单

| 目录 | 说明 | 现状 |
|------|------|------|
| `power_check/` | 充电/电源状态压测（含飞书推送、WiFi 连接） | 部分能力并入 `reboot-stress/` |
| `drivertest/` | 早期驱动安装测试（DriverTest/JD 变体） | 已被 `tools/driver-test`、`driver-verify` 取代 |
| `check_version/` | 早期版本核对 | 已被 `tools/check-version` 取代 |
| `code_package/` | 通用函数库（controlid 控件库 / feishu_sheet 飞书表格 SDK 封装 / common_functions） | 复用型代码沉淀 |
| `center_control` `chao_power` `chao_reboot` | 控制中心 / 超融合上下电 / 重启早期脚本 | 早期版本 |
| `GPU_test/` | GPU 压测 | 存档 |
| `General_Check/` | 通用硬件信息检查（LibreHardwareMonitor） | 存档 |
| `Time_Zone/` | 时区切换测试 | 存档 |
| `VT_test/` | 虚拟化(VT)开关测试 | 存档 |
| `Wifi_Switch/` | WiFi 开关切换测试 | 存档 |
| `ppt_test/` | PPT 播放相关测试 | 存档 |
| `remote_test/` | 远程控制页面测试（Selenium） | 存档 |
| `test-api/` | 早期自研接口测试框架（关键字驱动 + DDT 数据驱动 + HTMLTestRunner 报告 + 邮件/DB 支持） | 学习/存档版 |
| `yuanshen/` | 场景脚本 | 存档 |

## 说明

保留这些脚本是为了体现**能力演进的过程**——从早期一次性脚本，到后来 `tools/` 与各专项模块里工具化、可配置、可打包的版本。看当前实现请优先参考仓库其它模块。

---

*代码用于个人技术能力展示，敏感信息已脱敏，遵循仓库根目录 [MIT License](../LICENSE)。*
