import os
import sys
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import tkinter as tk
import win32com.client
import traceback
import time

def task_exists(scheduler, task_name):
    """检查任务是否已经存在"""
    try:
        root_folder = scheduler.GetFolder("\\")
        task = root_folder.GetTask(task_name)
        return task is not None
    except Exception as e:
        return False

def create_task_xml(task_name, executable_path, working_directory, script_args=None, delay_seconds=30):
    TASK_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-16"?>
    <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <Triggers>
        <LogonTrigger>
          <Enabled>true</Enabled>
          <Delay>PT{delay_seconds}S</Delay>
        </LogonTrigger>
      </Triggers>
      <Principals>
        <Principal id="Author">
          <UserId>{user_id}</UserId>
          <LogonType>InteractiveToken</LogonType>
          <RunLevel>HighestAvailable</RunLevel>
        </Principal>
      </Principals>
      <Settings>
        <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
        <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
        <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
        <StartWhenAvailable>true</StartWhenAvailable>
        <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
        <IdleSettings>
          <StopOnIdleEnd>false</StopOnIdleEnd>
          <RestartOnIdle>false</RestartOnIdle>
        </IdleSettings>
        <AllowStartOnDemand>true</AllowStartOnDemand>
        <Enabled>true</Enabled>
        <Hidden>false</Hidden>
        <RunOnlyIfIdle>false</RunOnlyIfIdle>
        <WakeToRun>false</WakeToRun>
        <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
        <Priority>7</Priority>
        <AllowHardTerminate>false</AllowHardTerminate>
      </Settings>
      <Actions Context="Author">
        <Exec>
          <Command>{command}</Command>
          <Arguments>{arguments}</Arguments>
          <WorkingDirectory>{working_directory}</WorkingDirectory>
        </Exec>
      </Actions>
    </Task>"""

    try:
        # 获取当前登录用户名称
        user_name = os.getlogin()

        # 生成任务XML
        task_xml = TASK_XML_TEMPLATE.format(
            delay_seconds=delay_seconds,
            command=executable_path,
            arguments=script_args if script_args else "",
            working_directory=working_directory,
            user_id=user_name
        )

        # Debug 打印日志查看XML内容是否正确
        print(task_xml)

        # 通过任务计划程序注册任务
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        # 检查任务是否已存在
        if task_exists(scheduler, task_name):
            print(f'Task "{task_name}" already exists. Skipping creation.')
            return

        task_definition = scheduler.NewTask(0)
        task_definition.XmlText = task_xml

        # 使用当前登录用户的凭证
        root_folder.RegisterTaskDefinition(
            task_name,
            task_definition,
            6,  # 6 表示，如果任务已存在则更新
            user_name,
            None,
            3  # 3 表示使用当前登录用户的凭证
        )
        print(f'Task "{task_name}" created successfully.')

    except Exception as e:
        print(f"Failed to create task: {e}")
        print(traceback.format_exc())

def open_image(image_name):
    # 确定当前工作目录
    current_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

    # 构建图片的绝对路径
    image_path = os.path.join(current_directory, image_name)

    # 检查文件是否存在
    if not os.path.isfile(image_path):
        print(f"File '{image_name}' does not exist in the directory '{current_directory}'.")
        return

    # 使用Tkinter显示并全屏图片
    try:
        root = tk.Tk()
        root.title(image_name)

        # 读取图片
        img = Image.open(image_path)
        photo = ImageTk.PhotoImage(img)

        # 创建一个全屏窗口
        def toggle_fullscreen(event=None):
            is_fullscreen = not root.attributes("-fullscreen")
            root.attributes("-fullscreen", is_fullscreen)
            bind_events(is_fullscreen)

        def exit_fullscreen(event=None):
            root.attributes("-fullscreen", False)
            bind_events(False)

        def bind_events(fullscreen):
            if fullscreen:
                root.bind("<Escape>", exit_fullscreen)
                root.bind("<Double-1>", exit_fullscreen)  # 绑定鼠标双击事件
            else:
                root.bind("<Escape>", toggle_fullscreen)
                root.bind("<Double-1>", toggle_fullscreen)  # 绑定鼠标双击事件

        canvas = tk.Canvas(root, width=img.width, height=img.height)
        canvas.pack()
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)

        # 进入全屏模式
        toggle_fullscreen()

        root.mainloop()
        print(f"Image '{image_name}' opened successfully.")
    except Exception as e:
        print(f"Failed to open image: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    # 定义任务名称
    task_name = "create_task"

    # 用作示例的可执行文件路径
    current_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
    executable_path = os.path.join(current_directory, 'create_task.exe')

    # 设置工作目录（可选）
    working_directory = current_directory

    # 延迟秒数，默认30秒（可以根据需要修改）
    delay_seconds = 30

    # 添加任务计划程序
    create_task_xml(task_name, executable_path, working_directory, script_args=None, delay_seconds=delay_seconds)

    # 替换为你想打开的图片名称
    image_name = "test.jpg"

    # 检查命令行参数
    if len(sys.argv) > 1:
        image_name = sys.argv[1]

    # 为了在任务计划程序中测试时避免立刻退出，加上延时
    if len(sys.argv) >= 2:
        time.sleep(int(sys.argv[1]))

    open_image(image_name)