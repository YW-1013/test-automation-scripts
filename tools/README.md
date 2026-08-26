# tools · 测试辅助工具集

> 日常测试中沉淀的一批小工具/脚本，覆盖**并发承载压测、定时任务管理、日志采集、驱动安装测试、版本核对、视频格式转换、分辨率切换压测、飞书通知**等。多数带 GUI，用 PyInstaller 打包成 exe 供团队直接使用。

> 🔒 **安全说明**：本目录部分脚本原本硬编码了内网地址、账号、密码、机器人 webhook、API Key。上传前已**全部替换为占位符**（`YOUR_ACCOUNT` / `YOUR_PASSWORD` / `YOUR_DEEPSEEK_API_KEY` / `YOUR_FEISHU_WEBHOOK_URL` / `your-server.example.com` / `192.168.1.100`）；真实配置文件不入库，仅保留 `*.example.json` 模板。使用时请自行填入你自己的环境值。

## 工具清单

| 子目录 | 工具 | 说明 |
|--------|------|------|
| `host-pressure/` | **多设备并发承载压测** | Android/Windows 双端，控制机对局域网内（`192.168.137.x` 热点网段）大批设备并发下发命令做后台承载压测，含 client/server 备用方案；用于验证后台在多节点并发下的稳定性 |
| `time-tasks/` | **多设备定时关机/重启管理器** | tkinter GUI，支持单台/多台（SN 逗号分隔）、按周计划，通过 HTTP API 控制设备（含京东现场私有化环境适配）；配置自动存 `config.json` |
| `get-log/` | **Android 日志采集器** | tkinter GUI，勾选日志类型（logs/logd/dmesg/tombstones/anr），ADB 拉取后自动打包 zip，多线程不阻塞界面 |
| `driver-test/` | **Windows 驱动安装自动化测试** | 扫描驱动目录按序逐一安装，WMI 查询安装状态并对比预期，生成带颜色标注的 Excel 报告；含 `sign_check.py` 签名校验 |
| `check-version/` | **固件/应用版本核对** | 读取 Excel 版本清单，核对 Android 设备各固件/应用版本是否符合预期 |
| `create-task/` | **Windows 任务计划创建工具** | tkinter + PIL GUI，通过 win32com 调用 Task Scheduler 创建定时任务（含已存在检测） |
| `change-video/` | **4K/8K 视频格式批量转换** | moviepy 将 4K60/8K60 视频批量转 mov/avi/mkv/mp4，用于测试设备对不同视频格式的兼容性 |
| `resolution-switch/` | **分辨率切换压测** | PySimpleGUI，win32api/ctypes 循环切换显示分辨率，实时统计成功/失败次数，验证显示驱动在分辨率切换时的稳定性 |
| `feishu-robot/` | **飞书机器人通知** | 封装飞书自定义机器人 webhook 推送测试结果的通用函数 |
| `deepseek-api-demo/` | **DeepSeek API 调用示例** | OpenAI SDK 调用 DeepSeek 大模型的最小示例（用于测试用例智能生成等场景探索） |

## 技术栈

`Python 3` · `tkinter` / `PySimpleGUI` / `PIL`（GUI）· `adb` / `uiautomator2`（安卓）· `wmi` / `win32com` / `win32api` / `ctypes`（Windows）· `requests`（HTTP API / webhook）· `openpyxl`（Excel 报告）· `moviepy`（视频转换）· `socket`（并发压测）· `PyInstaller`

---

*代码用于个人技术能力展示，敏感信息已脱敏，遵循仓库根目录 [MIT License](../LICENSE)。*
