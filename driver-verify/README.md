# 驱动清单核验器 driver-verify

> 校验一台 Windows 设备上的**驱动是否齐全、版本是否达标、是否全部签名、有无异常设备**，把"人工逐条对着驱动清单核对"变成一键自动比对。

---

## 组成

| 文件 | 说明 |
|------|------|
| `collect_drivers.ps1` | 驱动采集脚本（PowerShell）。在目标机上运行，导出当前所有驱动信息为 `driver_collect.json`（含设备名、版本、签名状态、`ConfigManagerErrorCode` 等）。 |
| `verify_drivers.py` | 驱动清单校验器（Python）。读取"驱动清单 Excel"与采集出的 json，做 5 项比对并输出结论。 |

## 5 项核验逻辑

1. **齐全性**：清单里的驱动是否都装了（缺失 → FAIL）。
2. **版本达标**：实机版本 == 期望 → PASS；实机 > 期望 → 偏高 PASS 并提示；实机 < 期望 → FAIL。
3. **清单内签名**：清单驱动是否都已签名（未签名 → FAIL）。
4. **清单外签名**：实机全部驱动签名情况（表外未签名 → 仅 WARN）。
5. **异常设备**：黄色感叹号 / 未挂载 / 无驱动等（`ConfigManagerErrorCode != 0`）→ 输出供人工判断。

## 三种采集模式

- **离线模式**（推荐）：目标机跑 `collect_drivers.ps1` 拿 json，再在本机比对，互不干扰。
- **本机模式**：`--local` 直接对当前机器采集并比对。
- **远程模式**：`--remote <ip> --user <user>` 通过 PowerShell Remoting(WinRM) 采集目标机。

## 用法

```bash
# 离线比对
python verify_drivers.py --excel "驱动清单.xlsx" --json driver_collect.json
# 本机采集并比对
python verify_drivers.py --excel "驱动清单.xlsx" --local
```

> 需管理员权限；驱动清单 Excel 与采集 json 为业务数据，未随仓库上传。

`Python 3` · `PowerShell`（Get-PnpDevice / WMI）· `argparse` · `openpyxl`

---

*遵循仓库根目录 [MIT License](../LICENSE)。*
