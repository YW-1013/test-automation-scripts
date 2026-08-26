# Airtest 批量执行器 airtest-batch-runner

> 基于 **Airtest + Poco** 的**多设备并行**自动化用例批量执行器：一次运行把整套 Airtest 用例分发到多台安卓设备并行执行，自动采集 logcat 与 CPU 信息，跑完汇总生成 HTML 测试报告。用于安卓大屏 / 平板功能用例的批量回归。

> 🔒 上传前已对设备 IP、飞书表格 token 等做脱敏（占位符 `192.168.1.100` / `YOUR_SPREADSHEET_TOKEN`）。

---

## 版本

| 目录 | 说明 |
|------|------|
| `air_run_four/` | 4 台设备并行版 |
| `air_run_six/` | 6 台设备并行版（在 four 基础上扩展到最多 6 台） |

两版功能一致，区别是并行设备数上限。

## 核心能力

- **多设备并行执行**：通过 `config.ini` 配置多台设备 IP / 用例路径，主控 `main.py` 把用例分发到各设备并行跑，成倍缩短回归时间。
- **运行时数据采集**：`logcat.py` 采集各设备日志、`cpuinfo.py` 采集 CPU 占用，便于结合功能结果定位性能/崩溃问题。
- **HTML 报告**：跑完按 `summary_template.html` 汇总生成可视化测试报告。
- **控件库分离**：`controlid.py` 集中管理 Poco 控件定位（按业务控件封装），用例与控件解耦，UI 变更只改控件库。
- **用例来源可对接飞书**：`document_to_code.py` 可从飞书表格拉取用例清单转成可执行结构（demo）。
- **一键启动**：`a_run_this.cmd` 以管理员权限启动（Airtest 操作需要）。

## 目录说明

```
air_run_six/
├── main.py                # 主控：设备分发 + 并行调度 + 报告汇总
├── conf.py / config.ini   # 配置（设备、用例路径、参数）
├── controlid.py           # Poco 控件定位库
├── cpuinfo.py             # CPU 信息采集
├── logcat.py              # logcat 日志采集
├── dir_check.py           # 用例目录检查
├── summary_template.html  # HTML 报告模板
└── a_run_this.cmd         # 启动脚本（管理员）
```

## 技术栈

`Python 3` · `Airtest` · `Poco`（控件定位）· `adb` / `logcat` · 多设备并行 · HTML 报告

---

*代码用于个人技术能力展示，敏感信息已脱敏，遵循仓库根目录 [MIT License](../LICENSE)。*
