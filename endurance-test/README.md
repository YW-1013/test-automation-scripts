# 续航（电池）自动化测试 endurance-test

> 面向平板 / 大屏（Windows + Android 双端）的**续航 / 电池寿命自动化测试**脚本集。通过脚本**自动模拟真实用户使用场景**（办公、娱乐、视频播放、网页浏览、待机等），长时间循环运行并记录耗电、时长、性能等数据，把"续航测试"从人工守着掉电变成可无人值守、可量化、可复现的自动化测试。

---

## 设计思路

续航测试的难点在于：**要贴近真实用户使用习惯**，又要**长时间稳定运行、精确记录耗电曲线**。本项目把典型使用场景拆解为可编排的自动化脚本：

- **模拟真实操作**：Windows 端用 `pyautogui` + `win32gui/win32api` + `Selenium` 驱动网易云、QQ、剪映、B 站视频、网页等应用；Android 端用 `uiautomator2` + `adb` 驱动，模拟看视频、刷网页、办公、聊天等。
- **量化记录**：读取电量（`battery-report` / WMI / adb dumpsys battery）、CPU 占用（CPU-Z）、时间戳，生成 Excel / docx 报告，形成可对比的耗电曲线。
- **场景化组合**：把"办公""娱乐""轻办公+娱乐""视频播放""待机"等做成独立场景构件，可单独跑也可组合成混合负载。

## 目录结构

```
endurance-test/
├── windows/                  # Windows 端续航测试
│   ├── endurance_test_pro/   # 综合续航测试（Selenium 驱动多应用）
│   ├── jikewan / biba/       # 不同基准工况（极客湾 / bilibili 等风格）
│   ├── heavy_work/           # 重负载工况
│   ├── scenario/             # 场景化续航测试
│   └── web_test/             # 网页多标签续航测试
├── android/                  # Android 端续航测试
│   ├── endurance_test_pro/   # 综合续航测试（uiautomator2）
│   ├── jikewan/              # 基准工况
│   ├── scenario/             # 场景化续航测试
│   └── video_play/           # 本地视频播放续航
└── scenarios/                # 场景构件（可复用的单场景脚本）
    ├── and_background/                 # 后台待机
    ├── and_entertainment/              # 娱乐场景
    ├── and_little_entertainment_work/  # 轻办公 + 娱乐混合
    ├── entertainment/                  # 娱乐
    ├── heavy_work/                     # 重办公
    └── standby_time_test/              # 待机时长测试
```

> 每个场景目录下的 `config.ini` 为可配置参数（应用路径、点击坐标、各环节时长、循环次数等）。测试素材（视频/PPT/文档）与 exe/报告未随仓库上传。

## 技术栈

`Python 3` · `Selenium`（网页自动化）· `pyautogui` / `win32gui` / `win32api`（Windows 桌面自动化）· `uiautomator2` / `adb`（Android 自动化）· `psutil` / `wmi`（系统与电量）· `openpyxl` / `python-docx`（报告）· `configparser`（参数配置）

---

*遵循仓库根目录 [MIT License](../LICENSE)。*
