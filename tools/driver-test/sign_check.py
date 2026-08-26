import os
import subprocess
import json

def get_sys_files(driver_dir):
    return [os.path.join(driver_dir, f) for f in os.listdir(driver_dir) if f.lower().endswith('.sys')]

def check_signature(file_path):
    # 调用powershell的Get-AuthenticodeSignature
    ps_cmd = [
        "powershell",
        "-Command",
        f"Get-AuthenticodeSignature -FilePath \"{file_path}\" | ConvertTo-Json"
    ]
    try:
        result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=10)
        out = result.stdout.strip()
        if not out:
            return "Unknown"
        data = json.loads(out)
        status = data.get("Status", "Unknown")
        return status
    except Exception as e:
        return f"Error: {e}"

def main():
    not_sign = []
    driver_dir = r"C:\Windows\System32\drivers"
    files = get_sys_files(driver_dir)
    for f in files:
        status = check_signature(f)
        print(f"{os.path.basename(f):40s} 签名状态: {status}")
        if status != 0:
            not_sign.append(f)
    if len(not_sign) > 0 :
        print(f"{not_sign}驱动文件没有签名")
    else:
        print("所有驱动文件都已签名")
    input("窗口保留中")
if __name__ == "__main__":
    main()