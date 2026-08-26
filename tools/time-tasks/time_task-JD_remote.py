"""
1、2024-9-29更新V1.1：新增正式环境地址
2、2024-10-18更新V1.2:（1）修改检测时间，关机后120S再进行关机状态的检测；（2）增加可配置选项-状态检测，选择是则进行设备开机状态检测，选择否则不检测；
3、2024-10-24更新V1.3：（1）修改输入中文的标签，获取到的设备为全部的问题；（2）新增京东现场的私有化环境的配置地址
4、2024-11-14更新V1.4：（1）上次写入的京东正式环境地址有误，重新修改
5、2024-11-14更新V1.4-JD：京东分支，用来验证设备开关机后，能否正常远程，只用于该项目，不加入基础脚本中
"""
import os
import sys
import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import time
import json
import requests
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys  # 导入 Keys 类

current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # 当前工作目录
CONFIG_FILE = os.path.join(current_working_dir,"config.json")
LOG_FILE = os.path.join(current_working_dir,"log.txt")
is_paused = threading.Event()
is_running = threading.Event()
def save_config():
    config = {
        "task_mode": task_mode_var.get(),
        "selected_week_days": [var.get() for var in week_vars],
        "selected_tasks": [var.get() for var in task_vars],
        "machine_mode": machine_select_var.get(),
        "machine_sn": get_entry_value(single_multiple_entry, "多台设备以英文,进行分隔"),
        "tag_filter": get_entry_value(tag_entry, "多个标签以英文,进行分隔"),
        "status_filter": get_entry_value(status_entry, "在线输入ONLINE，离线输入OFFLINE"),
        "area_filter": area_entry.get(),
        "char_filter": char_entry.get(),
        "env_config": env_config_var.get(),
        "task_name": task_name_entry.get(),
        "tester": tester_entry.get(),
        "project": project_entry.get(),
        "power_delay": power_delay_entry.get(),
        "boot_delay": boot_delay_entry.get(),
        "restart_delay": restart_delay_entry.get(),
        "screen_off_delay": screen_off_delay_entry.get(),
        "wake_delay": wake_delay_entry.get(),
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            task_mode_var.set(config["task_mode"])
            for i, var in enumerate(week_vars):
                var.set(config["selected_week_days"][i])
            for i, var in enumerate(task_vars):
                var.set(config["selected_tasks"][i])
            machine_select_var.set(config["machine_mode"])

            set_entry(single_multiple_entry, "多台设备以英文,进行分隔", config.get("machine_sn", ""))
            set_entry(tag_entry, "多个标签以英文,进行分隔", config.get("tag_filter", ""))
            set_entry(status_entry, "在线输入ONLINE，离线输入OFFLINE", config.get("status_filter", ""))

            area_entry.delete(0, 'end')
            area_entry.insert(0, config["area_filter"])

            char_entry.delete(0, 'end')
            char_entry.insert(0, config["char_filter"])

            env_config_var.set(config["env_config"])
            task_name_entry.delete(0, 'end')
            task_name_entry.insert(0, config["task_name"])
            tester_entry.delete(0, 'end')
            tester_entry.insert(0, config["tester"])
            project_entry.delete(0, 'end')
            project_entry.insert(0, config["project"])
            power_delay_entry.delete(0, 'end')
            power_delay_entry.insert(0, config.get("power_delay", "100"))
            boot_delay_entry.delete(0, 'end')
            boot_delay_entry.insert(0, config.get("boot_delay", "300"))
            restart_delay_entry.delete(0, 'end')
            restart_delay_entry.insert(0, config.get("restart_delay", "30"))
            screen_off_delay_entry.delete(0, 'end')
            screen_off_delay_entry.insert(0, config.get("screen_off_delay", "30"))
            wake_delay_entry.delete(0, 'end')
            wake_delay_entry.insert(0, config.get("wake_delay", "60"))

def set_entry(entry, default_text, value):
    """Set the entry's value and adjust color."""
    entry.delete(0, 'end')
    if value:
        entry.insert(0, value)
        entry.config(foreground='black')  # 实际输入则为黑色文字
    else:
        entry.insert(0, default_text)
        entry.config(foreground='gray')  # 提示文字为灰色

def print_to_log(message):
    message = str(message)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_message = f"[{timestamp}] {message}"
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(log_message  + '\n')
    log_output.insert(tk.END, log_message  + '\n')
    log_output.see(tk.END)
    print(log_message )


# 用来设置等待时间
def get_time(a):
    a = int(a)
    current_now_time = datetime.datetime.now()
    add_num_time = current_now_time + datetime.timedelta(seconds=a)
    add_num_time = str(add_num_time)
    return add_num_time

def get_url_header(env_select):
    urls = {
        "测试环境": "http://your-server.example.com",
        "私有化环境": "http://192.168.1.100:30017",
        "正式环境":"https://your-server.example.com",
        "京东现场私有化环境":"http://192.168.1.100:30017"
    }
    return urls.get(env_select, None)


def get_token(env_select):
    urls = {
        "测试环境": "http://your-server.example.com/api/auth/login?authType=USER&auth_type=USER&username=YOUR_ACCOUNT&password=YOUR_PASSWORD&clientId=DEVICE_MANAGEMENT",
        "私有化环境": "http://192.168.1.100:30017/api/auth/login?auth_type=choose_tenant&phoneNumber=YOUR_ACCOUNT&tenantId=1",
        "正式环境": "https://your-server.example.com/api/auth/login?authType=USER&auth_type=USER&username=YOUR_ACCOUNT&password=YOUR_PASSWORD&clientId=DEVICE_MANAGEMENT",
        "京东现场私有化环境":"http://192.168.1.100:30017/api/auth/login?auth_type=choose_tenant&phoneNumber=YOUR_ACCOUNT&tenantId=1"
    }
    token_url = urls.get(env_select, None)

    if not token_url:
        return None
    try:
        token_res = requests.post(url=token_url).text
    except:
        return False

    return re.findall(r'"token":"(.*?)","refreshedToken"', token_res)[0]


def get_id_by_tagname(env_select, headers,tag_name):
    url = f"{get_url_header(env_select)}/api/wisdom/tag/query"
    payload = json.dumps({"pageNo": 1, "pageSize": 1000000})
    tag_list = requests.post(url, headers=headers, data=payload).json()
    tag_names = [name.strip() for name in tag_name.split(',')]
    content_items = tag_list['data']['content']
    tag_ids = []
    for item in content_items:
        if item['tagName'] in tag_names:
            tag_ids.append(item['id'])
    return tag_ids


def get_id_by_area(env_select, headers, area_name):
    url = f"{get_url_header(env_select)}/api/meeting/rooms/pageByConfigType"
    payload = json.dumps({
        "pageNo": 1,
        "pageSize": 100,
        "condition": {"configType": "AREA", "value": ""}
    })
    area_list = requests.post(url, headers=headers, data=payload).json()
    return next((item['id'] for item in area_list['data']['content'] if item['value'] == area_name), None)


def get_sn_list(env_select, headers, tag_name=None, area_name=None, keywords=None,status=None):
    url = f"{get_url_header(env_select)}/api/wisdom/v2/queryPage"
    condition = {}
    if keywords:
        condition["keywords"] = keywords
    if status:
        condition["onlineStatus"] = status
    if tag_name:
        condition["tagIds"] = get_id_by_tagname(env_select, headers,tag_name)
    if area_name:
        condition["areaId"] = get_id_by_area(env_select, headers, area_name)
    payload = json.dumps({"pageNo": 1, "pageSize": 1000000, "condition": condition})
    get_sn_list = requests.post(url, headers=headers, data=payload).json()
    return [item['serialNumber'] for item in get_sn_list['data']['content']]


def schedule_task(add_num_time, task_params, headers):
    global sn_list
    url = f"{get_url_header(task_params['env_select'])}/api/wisdom/task/time"

    # 检查选择模式，确保获得正确的SN列表
    if task_params['machine_select_mode'] in ["单台", "多台"]:
        sn = task_params['machine_sn'].split(',')  # 将字符串转为列表
        sn_list = sn
        deviceSelection = "PORTION"
    elif task_params['machine_select_mode'] == "全部":
        sn = []
        deviceSelection = "ALL"
        sn_list = get_sn_list(task_params['env_select'], headers)
    else:
        sn = get_sn_list(task_params['env_select'], headers,
                         task_params['tag_select'], task_params['area_select'],
                         task_params['char_select'],task_params['status_select'])
        sn_list = sn
        deviceSelection = "PORTION"
    task_params['week_select'] = [] if task_params['timed_type'] == "ONCE" else task_params['week_select']

    payload = json.dumps({
        "name": task_params['test_name'],
        "executeType": task_params['timed_type'],
        "values": task_params['week_select'],
        "executeTime": add_num_time,
        "serialNumbers": sn,
        "deviceSelection": deviceSelection,
        "instructName": task_params['type']
    })
    res = requests.post(url, headers=headers, data=payload)
    res.close()
    return res.status_code


def get_devices_status(env_select, headers):
    status_list = []
    for sn in sn_list:
        url = f"{get_url_header(env_select)}/api/wisdom?serialNumber={sn}"
        res = requests.get(url, headers=headers).text
        status = res.split('"status":"')[1].split('","softwareId')[0]
        status_list.append(status)
    return status_list


def get_devices_live_time(env_select, headers):
    online_time_list = []
    for sn in sn_list:
        url = f"{get_url_header(env_select)}/api/wisdom/frequentChangeProperty?serialNumber={sn}"
        res = requests.get(url, headers=headers).text
        time_online = int(res.split('"runningDuration":')[1].split(',"freeDiskSpace"')[0])
        online_time_list.append(time_online)
    return online_time_list


def delete_weekly_task(env_select, headers, task_num):
    url_list = f"{get_url_header(env_select)}/api/wisdom/task/time/list"
    payload = json.dumps({"pageNo": 1, "pageSize": 10})
    res_list = requests.post(url_list, headers=headers, data=payload).json()
    task_id = res_list['data']['content'][task_num - 1]['id']
    url_delete = f"{get_url_header(env_select)}/api/wisdom/task/time/{task_id}"
    requests.delete(url_delete, headers=headers)


def push_report(web_hook, message_body):
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    requests.post(web_hook, json=message_body, headers=headers).json()



def send_message(message):
    webhook = 'YOUR_FEISHU_WEBHOOK_URL'
    message_body = {"msg_type": "text", "content": {"text": message}}
    push_report(webhook, message_body)




def open_log_folder():
    if sys.platform == "win32":
        os.startfile(current_working_dir)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", current_working_dir])
    else:
        subprocess.Popen(["xdg-open", current_working_dir])

def get_entry_value(entry, default_text):
    value = entry.get()
    return "" if value == default_text else value

def update_visibility(*args):
    task_choice = task_mode_var.get()
    machine_choice = machine_select_var.get()
    week_label.grid_forget()
    week_checkboxes_frame.grid_forget()
    sn_label.grid_forget()
    single_multiple_entry.grid_forget()
    filter_entries_frame.grid_forget()

    if task_choice == "循环任务":
        week_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        week_checkboxes_frame.grid(row=1, column=1, sticky='w', pady=5)

    if machine_choice in ["单台", "多台"]:
        sn_label.grid(row=7, column=0, sticky='w', padx=5, pady=5)
        single_multiple_entry.grid(row=7, column=1, sticky='w', pady=5)
    elif machine_choice == "筛选":
        filter_entries_frame.grid(row=7, column=0, columnspan=2, pady=5, sticky='ew')

def update_task_options():
    power_controls_frame.grid_forget()
    restart_controls_frame.grid_forget()
    screen_controls_frame.grid_forget()

    selected_tasks = [var.get() for var in task_vars if var.get()]

    if not selected_tasks:
        task_vars[0].set(tasks[0])
        selected_tasks.append(tasks[0])

    if "开关机" in selected_tasks:
        power_controls_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky='ew')
    if "重启" in selected_tasks:
        restart_controls_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky='ew')
    if "息屏唤醒" in selected_tasks:
        screen_controls_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky='ew')

def check_pause_and_stop():
    paused_message_printed = False  # 标志位，保证只打印一次暂停信息
    while is_paused.is_set():  # 等待暂停标记的变化
        if not paused_message_printed:
            print_to_log("已成功暂停")
            paused_message_printed = True
            root.after(0, lambda: pause_button.config(text="继续", state='normal'))
        time.sleep(0.1)

    if not is_running.is_set():  # 检查停止标记
        print_to_log("已成功停止运行\n\n\n")
        root.after(0, update_button_states)
        sys.exit()
    return False

def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

def remote_test():
    chrome_driver_path = 'D:\\chromedriver_win64\\chromedriver.exe'

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    url = "http://your-server.example.com/#/wisdom/device/detail?wisdomId=YOUR_DEVICE_SN"
    driver.get(url)

    wait_for_page_load(driver)

    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div/form/div[2]/button'))
        )
        username_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入用户名']")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入密码']")
        username_input.send_keys("YOUR_ACCOUNT")
        password_input.send_keys("YOUR_PASSWORD")
        login_button.click()

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="router-view"]/div/div/div/div[1]/div[2]/div/input'))
        )
        search_button.click()
        search_button.send_keys('1-0R')
        search_button.send_keys(Keys.ENTER)
        # driver.maximize_window()
        time.sleep(5)
        device_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="router-view"]/div/div/div/div[2]/div[1]/div/div[3]/table/tbody/tr/td[2]/div/span'))
        )
        device_button.click()
        time.sleep(30)

        # 获取所有打开的窗口句柄
        all_handles = driver.window_handles

        # 切换到新窗口
        driver.switch_to.window(all_handles[1])

        wait_for_page_load(driver)

        time.sleep(5)
        flash_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="router-view"]/div/div[1]/i'))
        )
        flash_button.click()

        time.sleep(5)
        remote_control_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="router-view"]/div/div[2]/div[2]/button[3]'))
        )
        remote_control_button.click()

        # 等待30秒，判断是否出现正在控制的字样
        time.sleep(30)
        try:
            driver.find_element(By.XPATH, '//*[@id="router-view"]/div/div[8]/div/div/div[1]/span')
            print_to_log("指定的XPath存在")
            return True
        except NoSuchElementException:
            print_to_log("指定的XPath不存在")
            driver.save_screenshot(
                os.path.join(current_working_dir, f"screenshot_{datetime.datetime.now().strftime('%m%d%H%M%S')}.png"))
            return False

    except TimeoutException as e:
        print_to_log(f"等待元素超时: {str(e)}")
        driver.save_screenshot(os.path.join(current_working_dir, 'timeout_screenshot.png'))



def on_start():
    global is_paused, is_running, test_times
    is_paused.clear()  # 清除暂停标记
    is_running.set()  # 设置运行标记
    test_times = 0
    start_button.config(state='disabled')
    pause_button.config(state='normal')
    end_button.config(state='normal')
    save_config()
    def run_tasks():
        global paused, test_times
        env_select = env_config_var.get()
        if get_token(env_select) is None or get_token(env_select) is False:
            print_to_log("TOKEN获取异常,需要检查环境配置是否正常")
            root.after(0, update_button_states)
            sys.exit()
        headers = {'Authorization': get_token(env_select),
                   'User-Agent': 'apifox/1.0.0 (https://www.apifox.cn)',
                   'Content-Type': 'application/json'}

        # 添加 task_select 来保存所选任务
        task_select = [var.get() for var in task_vars if var.get()]

        task_params = {
            "timed_type": "ONCE" if task_mode_var.get() == "单次任务" else "WEEKLY",
            "week_select": [str(day + 1) for day, var in enumerate(week_vars) if var.get()],
            "machine_select_mode": machine_select_var.get(),
            "machine_sn": get_entry_value(single_multiple_entry, "多台设备以英文,进行分隔"),
            "tag_select": get_entry_value(tag_entry, "多个标签以英文,进行分隔"),
            "status_select": get_entry_value(status_entry, "在线输入ONLINE，离线输入OFFLINE"),
            "area_select": area_entry.get(),
            "char_select": char_entry.get(),
            "env_select": env_select,
        }
        while True:  # Set to any number of desired runs

            check_pause_and_stop()

            test_times += 1
            footer_label.config(text=f"当前压测轮次：{test_times}轮")
            try:
                if "开关机" in task_select:
                    task_params['type'] = "START_UP"
                    task_params['time'] = get_time(boot_delay_entry.get())
                    task_params['test_name'] = f"{task_name_entry.get()}-第{test_times}轮定时开机测试"
                    schedule_task(task_params['time'], task_params, headers)
                    print_to_log("定时开机指令发送成功")

                    check_pause_and_stop()

                    time.sleep(10)

                    check_pause_and_stop()

                    task_params['type'] = "SHUTDOWN"
                    task_params['time'] = get_time(power_delay_entry.get())
                    task_params['test_name'] = f"{task_name_entry.get()}-第{test_times}轮定时关机测试"
                    schedule_task(task_params['time'], task_params, headers)
                    print_to_log("定时关机指令发送成功")

                    check_pause_and_stop()

                    time.sleep(int(power_delay_entry.get()) + 120)

                    check_pause_and_stop()
                    if status_check_var.get() == "是":
                        if all(i == "OFFLINE" for i in get_devices_status(env_select, headers)):
                            print_to_log("所有设备都关机了，定时关机测试通过")
                        else:
                            print_to_log("有设备未关机，定时关机测试不通过")
                            send_message(f"有设备未关机，第{test_times}轮定时关机测试不通过")
                            root.after(0, update_button_states)
                            sys.exit()

                    if task_mode_var.get() == "WEEKLY":
                        delete_weekly_task(env_select, headers, 1)
                        print_to_log("已删除指定循环任务")

                    check_pause_and_stop()


                    time.sleep(int(boot_delay_entry.get())-int(power_delay_entry.get()))

                    check_pause_and_stop()
                    if remote_test() is True:
                        print_to_log("可以正常远程")
                    else:
                        print_to_log("无法正常远程")
                        root.after(0, update_button_states)
                        sys.exit()

                    if status_check_var.get() == "是":
                        if all(i == "ONLINE" for i in get_devices_status(env_select, headers)):
                            print_to_log("所有设备都开机了，定时开机测试通过")
                        else:
                            print_to_log("有设备未开机，定时开机测试不通过")
                            send_message(f"有设备未开机，第{test_times}轮定时开机测试不通过")
                            root.after(0, update_button_states)
                            sys.exit()
                    if task_mode_var.get() == "WEEKLY":
                        delete_weekly_task(env_select, headers, 1)
                        print_to_log("已删除指定循环任务")

                    check_pause_and_stop()

                if "重启" in task_select:
                    task_params['type'] = "RESTART"
                    task_params['time'] = get_time(restart_delay_entry.get())
                    task_params['test_name'] = f"{task_name_entry.get()}-第{test_times}轮定时重启测试"
                    schedule_task(task_params['time'], task_params, headers)
                    print_to_log("定时重启指令发送成功")

                    check_pause_and_stop()

                    time.sleep(int(restart_delay_entry.get()) + 120)

                    if status_check_var.get() == "是":
                        if all(map(lambda x: 0 < x < 300, get_devices_live_time(env_select, headers))):
                            print_to_log("所有设备都重启成功了，定时重启测试通过")
                        else:
                            print_to_log("有设备未重启成功，定时重启测试不通过")
                            send_message(f"有设备未重启，第{test_times}轮定时重启测试不通过")
                            root.after(0, update_button_states)
                            sys.exit()
                    if task_mode_var.get() == "WEEKLY":
                        delete_weekly_task(env_select, headers, 1)
                        print_to_log("已删除指定循环任务")
                    check_pause_and_stop()

                if "息屏唤醒" in task_select:
                    task_params['type'] = "CLOSEDISPLAY"
                    task_params['time'] = get_time(screen_off_delay_entry.get())
                    task_params['test_name'] = f"{task_name_entry.get()}-第{test_times}轮定时息屏测试"
                    schedule_task(task_params['time'], task_params, headers)
                    print_to_log("定时息屏指令发送成功")
                    time.sleep(int(screen_off_delay_entry.get()) + 10)

                    check_pause_and_stop()

                    task_params['type'] = "AWAKEN"
                    task_params['time'] = get_time(wake_delay_entry.get())
                    task_params['test_name'] = f"{task_name_entry.get()}-第{test_times}轮定时唤醒测试"
                    schedule_task(task_params['time'], task_params, headers)
                    print_to_log("定时唤醒指令发送成功")
                    time.sleep(int(wake_delay_entry.get()) + 10)
                    if task_mode_var.get() == "WEEKLY":
                        delete_weekly_task(env_select, headers, 1)
                        print_to_log("已删除指定循环任务")

                    check_pause_and_stop()

                print_to_log(f"第{test_times}轮测试完成\n")
                time.sleep(30)
            except Exception as e:
                print_to_log(f"报错信息为：{e},继续下一轮")
                time.sleep(20)
                test_times -= 1
                continue

    task_thread = threading.Thread(target=run_tasks)
    task_thread.start()

def on_pause():
    if is_paused.is_set():
        print_to_log("继续运行")
        is_paused.clear()
        pause_button.config(text="暂停", state='normal')  # Update to "暂停" and enable button
        end_button.config(state='normal')
    else:
        print_to_log("正在暂停中，请等待")
        is_paused.set()
        pause_button.config(state='disabled')
        end_button.config(state='disabled')

def on_end():
    print_to_log("正在停止中，请等待")
    is_paused.clear()  # 清除暂停标记
    end_button.config(state='disabled')
    pause_button.config(state='disabled')  # 立即将暂停按钮置灰
    is_running.clear()

def update_button_states():
    start_button.config(state='normal')
    pause_button.config(state='disabled')
    end_button.config(state='disabled')

def clear_entry_on_focus_in(entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, 'end')
        entry.config(foreground='black')

def restore_entry_on_focus_out(entry, default_text):
    if entry.get() == "":
        entry.insert(0, default_text)
        entry.config(foreground='gray')



def frame_main():
    global task_mode_var, week_vars, task_vars, power_delay_entry, boot_delay_entry
    global restart_delay_entry, screen_off_delay_entry, wake_delay_entry,status_check_var
    global machine_select_var, single_multiple_entry, tag_entry,status_entry, area_entry, char_entry
    global env_config_var, task_name_entry, tester_entry, project_entry
    global week_label, week_checkboxes_frame, sn_label, filter_entries_frame
    global power_controls_frame, restart_controls_frame, screen_controls_frame
    global tasks
    global paused, test_times
    global footer_label, start_button, pause_button, end_button
    global root,log_output

    paused = False
    test_times = 0

    root = tk.Tk()
    root.title("定时任务压测脚本V1.4-JD")

    main_frame = tk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=5, pady=5)

    entry_frame = tk.Frame(main_frame)
    entry_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

    tk.Label(entry_frame, text="任务模式").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    task_mode_var = tk.StringVar()
    task_mode_combo = ttk.Combobox(entry_frame, textvariable=task_mode_var, state='readonly', width=20)
    task_mode_combo['values'] = ("单次任务", "循环任务")
    task_mode_combo.set("单次任务")
    task_mode_combo.grid(row=0, column=1, sticky='ew', padx=(0, 5))

    week_label = tk.Label(entry_frame, text="周几选择")
    week_checkboxes_frame = tk.Frame(entry_frame)
    days = ["1", "2", "3", "4", "5", "6", "7"]
    week_vars = [tk.IntVar() for _ in days]
    for i, day in enumerate(days):
        c = ttk.Checkbutton(week_checkboxes_frame, text=day, variable=week_vars[i])
        c.pack(side='left')

    tk.Label(entry_frame, text="任务选择").grid(row=2, column=0, sticky='nw', padx=5, pady=5)
    task_checkboxes_frame = tk.Frame(entry_frame)
    task_checkboxes_frame.grid(row=2, column=1, sticky='w', padx=(0, 5), pady=5)

    tasks = ["开关机", "息屏唤醒", "重启"]
    task_vars = [tk.StringVar(value=task) for task in tasks]

    for i, task in enumerate(tasks):
        c = ttk.Checkbutton(task_checkboxes_frame, text=task, variable=task_vars[i], onvalue=task, offvalue="",
                            command=update_task_options)
        c.pack(anchor='w')

    task_vars[0].set(tasks[0])

    power_controls_frame = tk.Frame(entry_frame)
    tk.Label(power_controls_frame, text="关机延时").grid(row=0, column=0, padx=(5, 5), pady=5)
    power_delay_entry = tk.Entry(power_controls_frame, width=30)
    power_delay_entry.grid(row=0, column=1, sticky='ew', padx=(0, 5), pady=5)
    power_delay_entry.insert(0, "100")

    tk.Label(power_controls_frame, text="开机延时").grid(row=1, column=0, padx=(5, 5), pady=5)
    boot_delay_entry = tk.Entry(power_controls_frame, width=30)
    boot_delay_entry.grid(row=1, column=1, sticky='ew', padx=(0, 5), pady=5)
    boot_delay_entry.insert(0, "300")

    restart_controls_frame = tk.Frame(entry_frame)
    tk.Label(restart_controls_frame, text="重启延时").grid(row=0, column=0, padx=(5, 5), pady=5)
    restart_delay_entry = tk.Entry(restart_controls_frame, width=30)
    restart_delay_entry.grid(row=0, column=1, sticky='ew', padx=(0, 5), pady=5)
    restart_delay_entry.insert(0, "30")

    screen_controls_frame = tk.Frame(entry_frame)
    tk.Label(screen_controls_frame, text="息屏延时").grid(row=0, column=0, padx=(5, 5), pady=5)
    screen_off_delay_entry = tk.Entry(screen_controls_frame, width=30)
    screen_off_delay_entry.grid(row=0, column=1, sticky='ew', padx=(0, 5), pady=5)
    screen_off_delay_entry.insert(0, "30")

    tk.Label(screen_controls_frame, text="唤醒延时").grid(row=1, column=0, padx=(5, 5), pady=5)
    wake_delay_entry = tk.Entry(screen_controls_frame, width=30)
    wake_delay_entry.grid(row=1, column=1, sticky='ew', padx=(0, 5), pady=5)
    wake_delay_entry.insert(0, "60")

    tk.Label(entry_frame, text="机器选择").grid(row=6, column=0, sticky='w', padx=5, pady=5)
    machine_select_var = tk.StringVar()
    machine_select_combo = ttk.Combobox(entry_frame, textvariable=machine_select_var, state='readonly', width=20)
    machine_select_combo['values'] = ("单台", "多台", "全部", "筛选")
    machine_select_combo.set("单台")
    machine_select_combo.grid(row=6, column=1, sticky='ew', padx=(0, 5), pady=5)

    sn_label = tk.Label(entry_frame, text="设备SN")
    single_multiple_entry = ttk.Entry(entry_frame, width=30)
    single_multiple_entry.insert(0, "多台设备以英文,进行分隔")
    single_multiple_value = get_entry_value(single_multiple_entry, "多台设备以英文,进行分隔")
    single_multiple_entry.bind('<FocusIn>', lambda e: clear_entry_on_focus_in(single_multiple_entry, "多台设备以英文,进行分隔"))
    single_multiple_entry.bind('<FocusOut>', lambda e: restore_entry_on_focus_out(single_multiple_entry, "多台设备以英文,进行分隔"))

    filter_entries_frame = tk.Frame(entry_frame)
    tk.Label(filter_entries_frame, text="标签筛选").grid(row=0, column=0, padx=(5, 5), pady=5)
    tag_entry = tk.Entry(filter_entries_frame, width=30)
    tag_entry.grid(row=0, column=1, padx=(0, 5), pady=5)
    tag_entry.insert(0, "多个标签以英文,进行分隔")
    tag_value = get_entry_value(tag_entry, "多个标签以英文,进行分隔")
    tag_entry.config(foreground='gray')
    tag_entry.bind('<FocusIn>', lambda e: clear_entry_on_focus_in(tag_entry, "多个标签以英文,进行分隔"))
    tag_entry.bind('<FocusOut>', lambda e: restore_entry_on_focus_out(tag_entry, "多个标签以英文,进行分隔"))

    # Status Filter
    tk.Label(filter_entries_frame, text="状态筛选").grid(row=1, column=0, padx=(5, 5), pady=5)
    status_entry = tk.Entry(filter_entries_frame, width=30)
    status_entry.grid(row=1, column=1, padx=(0, 5), pady=5)
    status_entry.insert(0, "在线输入ONLINE，离线输入OFFLINE")
    status_entry.config(foreground='gray')
    status_value = get_entry_value(status_entry, "在线输入ONLINE，离线输入OFFLINE")
    status_entry.bind('<FocusIn>', lambda e: clear_entry_on_focus_in(status_entry, "在线输入ONLINE，离线输入OFFLINE"))
    status_entry.bind('<FocusOut>',lambda e: restore_entry_on_focus_out(status_entry, "在线输入ONLINE，离线输入OFFLINE"))

    tk.Label(filter_entries_frame, text="区域筛选").grid(row=2, column=0, padx=(5, 5), pady=5)
    area_entry = tk.Entry(filter_entries_frame, width=30)
    area_entry.grid(row=2, column=1, padx=(0, 5), pady=5)
    tk.Label(filter_entries_frame, text="字符筛选").grid(row=3, column=0, padx=(5, 5), pady=5)
    char_entry = tk.Entry(filter_entries_frame, width=30)
    char_entry.grid(row=3, column=1, padx=(0, 5), pady=5)


    tk.Label(entry_frame, text="环境配置").grid(row=8, column=0, sticky='w', padx=5, pady=(15, 5))
    env_config_var = tk.StringVar()
    env_config_combo = ttk.Combobox(entry_frame, textvariable=env_config_var, state='readonly', width=20)
    env_config_combo['values'] = ("私有化环境", "测试环境","正式环境","京东现场私有化环境")
    env_config_combo.set("私有化环境")
    env_config_combo.grid(row=8, column=1, sticky='ew', padx=(0, 5), pady=(15, 5))

    tk.Label(entry_frame, text="任务名称").grid(row=9, column=0, sticky='w', padx=5, pady=5)
    task_name_entry = ttk.Entry(entry_frame, width=30)
    task_name_entry.grid(row=9, column=1, sticky='ew', padx=(0, 5), pady=5)

    tk.Label(entry_frame, text="测试人员").grid(row=10, column=0, sticky='w', padx=5, pady=5)
    tester_entry = ttk.Entry(entry_frame, width=30)
    tester_entry.grid(row=10, column=1, sticky='ew', padx=(0, 5), pady=5)

    tk.Label(entry_frame, text="测试项目").grid(row=11, column=0, sticky='w', padx=5, pady=5)
    project_entry = ttk.Entry(entry_frame, width=30)
    project_entry.grid(row=11, column=1, sticky='ew', padx=(0, 5), pady=5)

    tk.Label(entry_frame, text="状态检测").grid(row=12, column=0, sticky='w', padx=5, pady=5)
    status_check_var = tk.StringVar()
    status_check_combo = ttk.Combobox(entry_frame, textvariable=status_check_var, state='readonly', width=20)
    status_check_combo['values'] = ("是", "否")
    status_check_combo.set("否")
    status_check_combo.grid(row=12, column=1, sticky='ew', padx=(0, 5))


    frame3 = tk.Frame(main_frame)
    frame3.pack(side='left', fill='both', expand=True, padx=5, pady=5)

    tk.Label(frame3, text="日志输出").pack(anchor='w', padx=5)
    log_output = tk.Text(frame3, height=20)
    log_output.pack(fill='both', expand=True, padx=5, pady=5)

    footer_frame = tk.Frame(root)
    footer_frame.pack(fill='both', expand=True, padx=5, pady=5)

    footer_label = tk.Label(footer_frame, text="当前压测轮次：0轮")
    footer_label.pack(side='left', padx=5)

    button_frame = tk.Frame(footer_frame)
    button_frame.pack(fill='both', expand=True, padx=5)

    start_button = ttk.Button(button_frame, text="开始", command=on_start)
    start_button.pack(side='left', fill='both', expand=True, padx=5, pady=5)

    pause_button = ttk.Button(button_frame, text="暂停", command=on_pause)
    pause_button.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    pause_button.config(state='disabled')

    end_button = ttk.Button(button_frame, text="结束", command=on_end)
    end_button.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    end_button.config(state='disabled')

    ttk.Button(button_frame, text="打开日志文件夹", command=open_log_folder).pack(side='left', fill='both', expand=True, padx=5, pady=5)

    task_mode_var.trace('w', update_visibility)
    machine_select_var.trace('w', update_visibility)

    load_config()
    update_visibility()
    update_task_options()
    root.mainloop()

if __name__ == '__main__':
    frame_main()