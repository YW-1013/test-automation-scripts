import ctypes

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    # Windows specific code
    if is_admin():
        print("脚本正在以管理员权限运行")
    else:
        print("脚本正在以普通权限运行")
    input()