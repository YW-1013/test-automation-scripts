import tkinter as tk
import os
import tkinter.messagebox as messagebox
import time
import zipfile
import subprocess
import threading
import json
import sys
import shutil

class LogDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("日志下载")
        self.geometry("500x500")

        self.log_types = {
            "logs": tk.IntVar(),
            "logd": tk.IntVar(),
            "dmesg": tk.IntVar(),
            "tombstones": tk.IntVar(),
            "anr": tk.IntVar(),
        }
        self.select_all_var = tk.IntVar()
        self.target_ip_var = tk.StringVar()
        self.zip_name_var = tk.StringVar()
        self.load_config()  # 调用该函数，在初始化时检查并加载配置项

        self.create_widgets()

    def create_widgets(self):
        # 选择需要下载的日志类型
        log_types_frame = tk.Frame(self)
        log_types_frame.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)

        # 标题和全选复选框放在同一个水平框架中
        title_frame = tk.Frame(log_types_frame)
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        log_types_label = tk.Label(title_frame, text="选择需要下载的日志类型")
        log_types_label.pack(side=tk.LEFT)

        select_all_checkbox = tk.Checkbutton(title_frame, text="全选", variable=self.select_all_var,
                                             command=self.toggle_select_all)
        select_all_checkbox.pack(side=tk.LEFT, padx=10)  # 在标题后增加一些间隔

        # 日志类型复选框
        checkboxes_frame = tk.Frame(log_types_frame)
        checkboxes_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # 创建并排列所有日志类型复选框
        for log_type, var in self.log_types.items():
            checkbox = tk.Checkbutton(checkboxes_frame, text=log_type, variable=var)
            checkbox.pack(side=tk.LEFT, expand=True)

        # 大屏IP输入框
        target_ip_frame = tk.Frame(self)
        target_ip_frame.pack(side=tk.TOP, anchor=tk.W, padx=11, pady=10)
        target_ip_label = tk.Label(target_ip_frame, text="请输入大屏的IP地址")
        target_ip_label.grid(row=0, column=0, sticky=tk.W)
        target_ip_entry = tk.Entry(target_ip_frame, textvariable=self.target_ip_var,width=40)
        target_ip_entry.grid(row=0, column=1, sticky=tk.W)

        # 压缩文件命名框
        zip_name_frame = tk.Frame(self)
        zip_name_frame.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        zip_name_label = tk.Label(zip_name_frame, text="请输入压缩文件名称")
        zip_name_label.grid(row=0, column=0, sticky=tk.W)
        zip_name_entry = tk.Entry(zip_name_frame, textvariable=self.zip_name_var,width=40)
        zip_name_entry.grid(row=0, column=1, sticky=tk.W)

        # 按钮
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=10)
        self.start_button = tk.Button(button_frame, text="开始", command=self.start_download)
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        open_folder_button = tk.Button(button_frame, text="打开日志文件夹", command=self.open_folder)
        open_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        clear_logs_button = tk.Button(button_frame, text="清空日志文件夹", command=self.clear_logs_folder)
        clear_logs_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        exit_button = tk.Button(button_frame, text="退出", command=self.quit)
        exit_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)

        # 日志输出框
        self.log_output = tk.Text(self, wrap=tk.WORD)
        self.log_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, side=tk.TOP, anchor=tk.W)

    def toggle_select_all(self):
        all_checked = self.select_all_var.get() == 1
        for log_type in self.log_types:
            self.log_types[log_type].set(all_checked)

    def clear_logs_folder(self):
        logs_folder_path = "./logs"
        try:
            if os.path.exists(logs_folder_path):
                for filename in os.listdir(logs_folder_path):
                    file_path = os.path.join(logs_folder_path, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                self.log_output.insert(tk.END, "日志文件夹已清空\n")
            else:
                self.log_output.insert(tk.END, "日志文件夹不存在\n")
        except Exception as e:
            self.log_output.insert(tk.END, f"清空日志文件夹时发生异常：{e}\n")
        finally:
            self.log_output.see(tk.END)

    def load_config(self):
        config_file = "config.json"
        if os.path.isfile(config_file):
            with open(config_file, "r") as file:
                config = json.load(file)
                self.target_ip_var.set(config.get("target_ip", "192.168.1.100"))
                self.zip_name_var.set(config.get("zip_name", "xxx"))
                selected_log_types = config.get("selected_log_types", [])
                for log_type, var in self.log_types.items():
                    var.set(int(log_type in selected_log_types))
                # 更新全选变量的状态
                self.select_all_var.set(int(len(selected_log_types) == len(self.log_types)))
        else:
            # 默认配置
            default_config = {
                "target_ip": "192.168.1.100",
                "zip_name": "xxx",
                "selected_log_types": list(self.log_types.keys())  # 默认全选
            }
            for log_type in self.log_types:
                self.log_types[log_type].set(1)  # 设置为全选
            self.target_ip_var.set(default_config["target_ip"])
            self.zip_name_var.set(default_config["zip_name"])
            # 设置全选按钮为勾选状态
            self.select_all_var.set(1)
            self.save_config(default_config["target_ip"], default_config["zip_name"])


    def save_config(self, target_ip, zip_name):
        config = {
            "target_ip": target_ip,
            "zip_name": zip_name,
            "selected_log_types": [log_type for log_type, var in self.log_types.items() if var.get() == 1]
        }
        with open("config.json", "w") as file:
            json.dump(config, file)

    def start_download(self):
        self.start_button['state'] = tk.DISABLED  # 禁用开始按钮
        self.log_output.delete('1.0', tk.END)
        selected_log_types = [log_type for log_type, var in self.log_types.items() if var.get() == 1]
        if not selected_log_types:
            messagebox.showerror("错误", "请选择至少一种日志类型")
            return
        if not self.target_ip_var.get() or not self.zip_name_var.get():
            messagebox.showerror("错误", "请输入大屏IP和压缩文件名称")
            return
        target_ip = self.target_ip_var.get()
        zip_name = self.zip_name_var.get()
        self.save_config(target_ip, zip_name)  # 保存配置项
        self.log_output.insert(tk.END, "开始下载日志...\n")
        self.log_output.update_idletasks()  # 更新日志输出框

        # TODO: 调用download_logs函数进行日志下载
        target_ip = self.target_ip_var.get()
        zip_name = self.zip_name_var.get()
        thread = threading.Thread(target=self.download_logs, args=(target_ip, zip_name, selected_log_types))
        thread.start()

    def run_command(self,command):
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    def download_logs(self,target_ip, zip_name, selected_log_types):
        try:
            self.run_command(f"adb connect {target_ip}")
            self.run_command(f"adb -s {target_ip} shell setprop persist.h3c.root_state 123@qwe")
            self.run_command(f"adb -s {target_ip} root")
            timestamp = time.strftime("%m%d%H%M%S", time.localtime())
            target_dir = f"./logs/{timestamp}"
            dis_dir = f"./logs/{zip_name}"
            os.makedirs(target_dir, exist_ok=True)
            for log_type in selected_log_types:
                if log_type == 'logd':
                    self.log_output.insert(tk.END, "开始下载logd日志...\n")
                    self.run_command(f"adb -s {target_ip} pull /data/misc/logd {target_dir}")
                    self.log_output.insert(tk.END, "logd日志下载已完成\n")
                elif log_type == 'logs':
                    self.log_output.insert(tk.END, "开始下载logs日志...\n")
                    self.run_command(f"adb -s {target_ip} pull /data/vendor/logs {target_dir}")
                    self.log_output.insert(tk.END, "logs日志下载已完成\n")
                elif log_type == 'tombstones':
                    self.log_output.insert(tk.END, "开始下载tombstones日志...\n")
                    self.run_command(f'adb -s {target_ip} pull "/data/tombstones" "{target_dir}"')
                    self.log_output.insert(tk.END, "tombstones日志下载已完成\n")
                elif log_type == 'anr':
                    self.log_output.insert(tk.END, "开始下载anr日志...\n")
                    self.run_command(f'adb -s {target_ip} pull "/data/anr" "{target_dir}"')
                    self.log_output.insert(tk.END, "anr日志下载已完成\n")
                elif log_type == 'dmesg':
                    self.log_output.insert(tk.END, "开始下载dmesg日志...\n")
                    self.run_command(f'adb -s {target_ip} shell "dmesg >/data/dmesg.txt"')
                    time.sleep(10)
                    self.run_command(f"adb -s {target_ip} pull /data/dmesg.txt {target_dir}")
                    self.log_output.insert(tk.END, "dmesg日志下载已完成\n")

            os.rename(target_dir, dis_dir)
            # 压缩日志文件为指定压缩文件命名的zip格式压缩包
            zip_file_path = f"./logs/{zip_name}.zip"
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(dis_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, dis_dir))

            self.log_output.insert(tk.END, "所有日志下载完成\n")
            self.log_output.see(tk.END)  # 滚动到最新日志处
        except Exception as e:
            self.log_output.insert(tk.END,f"下载日志时发生异常：{e}\n")
        finally:
            self.after(0, lambda: self.start_button.config(state=tk.NORMAL))

    # TODO: 实现日志下载的逻辑
    # 下载指定类型的日志文件，并将其压缩成一个zip文件
    # 将日志数据写入self.log_output，显示下载进度和日志输出

    def open_folder(self):
        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        logs_folder_path = os.path.join(base_path, "logs")
        os.startfile(logs_folder_path)

if __name__ == "__main__":
    app = LogDownloader()
    app.mainloop()