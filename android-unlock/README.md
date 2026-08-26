# 安卓锁屏密码解锁压测 android-unlock

> 带 GUI 的安卓设备**锁屏 → 唤醒 → 密码解锁**自动化压测工具，验证反复息屏/唤醒/解锁流程的稳定性与成功率。

---

## 测试流程

1. 通过 adb 锁定屏幕（模拟息屏场景）；
2. 息屏后 ADB 断连 → 按**拇指机器人**物理唤醒设备；
3. 屏幕亮起 / ADB 重连 → 上滑解锁界面 → 逐位按数字输入密码；
4. 验证是否成功进入系统桌面；
5. 循环并统计解锁通过率。

## 版本

| 文件 | GUI 库 |
|------|--------|
| `LockScreen_Unlock_Test.py` | CustomTkinter |
| `LockScreen_Unlock_Test_PyQt6.py` | PyQt6（另一套界面实现） |

## 设计要点

- **物理唤醒**：息屏后 ADB 会断连，改用外接"拇指机器人"物理按键唤醒，贴近真实用户场景。
- **uiautomator2 + adb**：解锁界面上滑、坐标点击、密码输入通过 uiautomator2 驱动。
- **u2.jar 打包兜底**：PyInstaller onefile 模式下资源解压到 `_MEIPASS` 临时目录，系统清理临时目录会导致 `u2.jar` 丢失；脚本首次运行时把 jar 备份到 exe 同目录，`_MEIPASS` 被清理时自动恢复，保证长时压测不中断。

## 技术栈

`Python 3` · `uiautomator2` / `adb` · `tkinter` / `customtkinter` / `PyQt6`（两套 GUI）· `PyInstaller`

> 打包 exe、`u2.jar`、日志未入库。

---

*遵循仓库根目录 [MIT License](../LICENSE)。*
