"""
switch_to_android.py — 无 UI 触发"应用控制中心 (H3C SystemControl)"切换到安卓系统。

本实现的协议 100% 来自对以下程序集的反编译（ILSpy）:
    H3C.Channel.Core.dll      —— 消息封装 / 枚举 / URL 常量
    H3C.Channel.Client.dll    —— ClientWebSocket / 连接握手 / 发送
    SysCtrl.Shared.Common.dll —— SysSwitchIpcBusinessForApp（切换调用）

链路（与 UI 按钮完全一致）:
    App 客户端 --ws--> ServiceHost 服务端
    1) 连接 ws://localhost:<port>/H3C_APPS_Channel
    2) 发送 ApplyClientConnecting，登记本客户端名 "SystemControl"
    3) 发送 ClientCommunication：目标 "SystemControlService"，事件 "SwitchSystemToAndroid"
    4) 服务端执行 SystemSwitchByCmBios（经 Insyde segwindrv 写 OemVariable）并回发
       事件 "SystemSwitchResult"，Data 为 int：0=失败 / -1=无安卓启动项 / 其它=成功→重启
本脚本 **不碰固件**，只是复用服务端已测试过的切换逻辑。

依赖: pip install websocket-client
用法: python switch_to_android.py            # 预检 + 演练（不下发）
      python switch_to_android.py --commit   # 真正下发（会重启进安卓！）
      python switch_to_android.py --commit --port 48372
"""

from __future__ import annotations
import argparse
import ctypes
import json
import socket
import subprocess
import sys
import time
import uuid

# ===== 反编译确认的协议常量（H3C.Channel.Core.ChannelCustomText / ChannelMessageType）=====
WS_PATH = "H3C_APPS_Channel"
DEFAULT_PORT = 48372                 # 本机服务实际监听端口（源码默认 27101）
APP_CLIENT_NAME = "SystemControl"          # 本客户端登记名（见运行日志）
SERVICE_CLIENT_NAME = "SystemControlService"   # 目标：执行切换的服务

# ChannelMessageType 枚举整数值
T_APPLY_CLIENT_CONNECTING = 0
T_CLIENT_COMMUNICATION = 6

EVENT_SWITCH_TO_ANDROID = "SwitchSystemToAndroid"   # SysSwitchIpcBusinessKeys.SwitchSystemToAndroidKey
EVENT_SWITCH_RESULT = "SystemSwitchResult"          # SysSwitchIpcBusinessKeys.SystemSwitchResultKey
SWITCH_TIMEOUT = 5.0                                 # 源码：等待 5000ms

RESULT_MEANING = {0: "失败（response data 0）",
                  -1: "失败：无安卓启动项（No Android boot option）"}


# ---------- 消息封装（对应 ChannelServerMessage / ChannelSendingMessage / ClientEvent）----------
def _server_frame(msg_type: int, inner: dict) -> str:
    """ChannelServerMessage: {"Type":int,"MessageData":"<inner json string>"}（双重编码）。"""
    return json.dumps({"Type": msg_type, "MessageData": json.dumps(inner, ensure_ascii=False)},
                      ensure_ascii=False)


def _connect_frame() -> str:
    # ChannelConnectingMessage{Client}
    return _server_frame(T_APPLY_CLIENT_CONNECTING, {"Client": APP_CLIENT_NAME, "Message": None})


def _switch_frame() -> str:
    # ChannelSendingMessage{TargetClient,SourceClient,Data,Event:ClientEvent,...}
    inner = {
        "TargetClient": SERVICE_CLIENT_NAME,
        "SourceClient": APP_CLIENT_NAME,
        "Data": "",
        "Event": {
            "EventName": EVENT_SWITCH_TO_ANDROID,
            "EventId": str(uuid.uuid4()),
            "NeedCallBack": True,
            "IsCallBack": False,
            "BackingResponse": None,
        },
        "Message": None,
    }
    return _server_frame(T_CLIENT_COMMUNICATION, inner)


def _parse_incoming(raw: str):
    """解析服务端帧；若为 SystemSwitchResult，返回 int 结果，否则 None。"""
    try:
        outer = json.loads(raw)
        inner = json.loads(outer.get("MessageData") or "{}")
    except Exception:
        return None
    ev = (inner.get("Event") or {}).get("EventName")
    if ev != EVENT_SWITCH_RESULT:
        return None
    data = inner.get("Data")
    try:
        return int(str(data).strip())
    except Exception:
        return None


# ------------------------------- 预检 -------------------------------
def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def service_running(name: str = "SystemControlService") -> bool:
    try:
        out = subprocess.run(["sc", "query", name], capture_output=True,
                             text=True, timeout=10).stdout
        return "RUNNING" in out.upper()
    except Exception:
        return False


def port_open(port: int, timeout: float = 2.0) -> bool:
    for fam, host in ((socket.AF_INET6, "::1"), (socket.AF_INET, "127.0.0.1")):
        try:
            with socket.socket(fam, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((host, port)) == 0:
                    return True
        except OSError:
            continue
    return False


def preflight(port: int) -> list[str]:
    p = []
    if sys.platform != "win32":
        p.append("仅支持 Windows")
    if not is_admin():
        p.append("需管理员权限运行")
    if not service_running():
        p.append("SystemControlService 未运行")
    if not port_open(port):
        p.append(f"IPC 端口 {port} 不可连接")
    return p


def _connect_ws(port: int, timeout: float):
    """依次尝试 localhost/::1/127.0.0.1（服务端可能仅监听 IPv6 回环）。"""
    from websocket import create_connection
    last = None
    for host in ("localhost", "[::1]", "127.0.0.1"):
        url = f"ws://{host}:{port}/{WS_PATH}"
        try:
            return create_connection(url, timeout=timeout), url
        except Exception as e:
            last = e
    raise last


# ------------------------------- 主流程 -------------------------------
def switch_to_android(confirm: bool = False, dry_run: bool = True,
                      port: int = DEFAULT_PORT) -> bool:
    problems = preflight(port)
    if problems:
        print("预检未通过：")
        for x in problems:
            print("  -", x)
        return False
    print(f"预检通过：admin={is_admin()}  service=RUNNING  port {port} 可连")

    if dry_run or not confirm:
        print("[dry-run] 未下发。真正执行请加 --commit。")
        print("  连接帧:", _connect_frame())
        print("  切换帧:", _switch_frame())
        return False

    try:
        ws, url = _connect_ws(port, SWITCH_TIMEOUT + 2)
    except ImportError:
        print("缺少依赖：pip install websocket-client"); return False
    except Exception as e:
        print("连接失败：", e); return False

    print("已连接", url)
    try:
        ws.send(_connect_frame())                 # 1) 登记客户端名
        time.sleep(0.2)
        ws.send(_switch_frame())                  # 2) 下发切换命令
        print(f"已发送 {EVENT_SWITCH_TO_ANDROID} → {SERVICE_CLIENT_NAME}，等待结果（≤{int(SWITCH_TIMEOUT)}s）…")

        deadline = time.time() + SWITCH_TIMEOUT
        while time.time() < deadline:
            ws.settimeout(max(0.2, deadline - time.time()))
            try:
                raw = ws.recv()
            except Exception:
                break
            if not raw:
                continue
            res = _parse_incoming(raw if isinstance(raw, str) else raw.decode("utf-8", "ignore"))
            if res is None:
                continue
            if res in RESULT_MEANING:
                print("[FAIL]", RESULT_MEANING[res]); return False
            print(f"[OK] 服务已受理切换（result={res}），系统即将重启进安卓。"); return True

        print("未在 5s 内收到 SystemSwitchResult（服务可能已开始切换/重启）。")
        return False
    finally:
        try:
            ws.close()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser(description="无 UI 触发切换到安卓系统")
    ap.add_argument("--commit", action="store_true", help="真正下发（会立即重启进安卓）")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"IPC 端口（默认 {DEFAULT_PORT}）")
    args = ap.parse_args()
    ok = switch_to_android(confirm=args.commit, dry_run=not args.commit, port=args.port)
    return 0 if ok else 1


if __name__ == "__main__":
    rc = main()
    # 双击运行时保持窗口，便于查看 dry-run 输出；切换成功会重启，pause 无碍
    try:
        input("\n按回车键退出…")
    except EOFError:
        pass
    raise SystemExit(rc)
