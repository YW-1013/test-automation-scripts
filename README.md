# test-automation-scripts

> 个人测试开发作品集 · 消费电子 / 平板大屏 / 软硬件结合方向的自动化测试脚本与自研框架
>
> A personal portfolio of test-automation tools & self-built frameworks for consumer-electronics / embedded-adjacent testing.

本仓库汇总我在实际测试工作中独立设计、开发并落地使用的自动化脚本与工具，涵盖**音频自动化测试框架、OTA 升级压测、驱动核验、续航测试、UI/接口自动化**等方向。所有代码均以 Python 为主，强调 **"把主观体验变成可量化、可回归的客观标准"** 和 **"自研工具化提效"**。

> ⚠️ 说明：仓库仅包含**源码**。所有可执行文件（`.exe`）、打包产物（`build/`、`dist/`）、依赖环境（`.venv/`）、运行日志、测试素材（视频/音频/模型）等均已通过 `.gitignore` 排除；所有 `config` 文件中的真实设备 IP、内网地址、机器人 webhook 已脱敏，仓库只保留占位符版本 `*.example.json`。

## 目录

| 模块 | 说明 |
|------|------|
| [`audio-test-framework/`](./audio-test-framework) | **自研分布式音频自动化测试框架**：client/server 双端 socket 架构，覆盖多种上下电/双系统切换方式，用频谱能量客观判声，支持扬声器/麦克风/相机/U 盘/蓝牙/光感等多项检测 |
| [`ota-upgrade/`](./ota-upgrade) | **OTA 升级自动化压测**：BIOS / 控制中心 OTA 循环升级，WMI/注册表版本比对、图像识别定位、任务计划重启续跑，无人值守防变砖 |
| [`endurance-test/`](./endurance-test) | **续航（电池）自动化测试**：Win/Android 双端模拟办公/娱乐/视频/待机等真实使用场景，量化耗电，含场景构件库 |
| [`reboot-stress/`](./reboot-stress) | **重启/开关机稳定性压测**：每轮开关机后自动做驱动/服务/光感/外设等 8 项自检（GUI 可配置） |
| [`driver-verify/`](./driver-verify) | **驱动清单核验器**：齐全性/版本/签名/异常设备 5 项核验，离线/本机/远程三种采集模式 |
| [`android-unlock/`](./android-unlock) | **安卓锁屏解锁压测**：锁屏→物理唤醒→密码解锁循环，含 u2.jar 打包兜底 |
| [`aging-test/`](./aging-test) | **老化稳定性测试**：Android 出厂老化循环压测，统一异常捕获 + 并行执行 |
| [`education-api/`](./education-api) | **教育平台接口自动化框架**：Selenium/pytest-bdd，BDD + given/when/then 分层，多环境切换 + token 鉴权 |
| [`education-ui/`](./education-ui) | **教育平台 Web UI 自动化框架**：Selenium + pytest + POM，定位器/页面对象/数据三层分离，数据驱动 + Allure |
| [`airtest-batch-runner/`](./airtest-batch-runner) | **Airtest 批量执行器**：基于 Airtest+Poco 的多设备并行用例执行器，采集 logcat/CPU，生成 HTML 报告，控件库分离 |
| [`tools/`](./tools) | **测试辅助工具集**：并发承载压测、定时关机重启、日志采集、驱动安装测试、版本核对、视频转换、分辨率切换压测、飞书通知等 10 个小工具 |
| [`legacy/`](./legacy) | **早期 / 存档脚本**：早期版本或已被新版取代的脚本，作技术存档与思路参考（含早期自研接口框架 test-api、通用控件库等） |

## 技术栈

`Python` · `socket` · `tkinter` · `OpenCV` · `scipy.fft` · `PyAudio` · `uiautomator2 / adb` · `pywifi` · `PyInstaller` · `Selenium` · `pytest`

## 关于我

约 7 年软件测试经验，专注**软硬件结合系统测试、OTA 升级测试、自研测试框架/工具**。习惯用数据驱动与工具化手段管控版本质量与发布风险。

---

*本仓库代码用于个人技术能力展示，遵循 [MIT License](./LICENSE)。*
