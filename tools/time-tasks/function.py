import requests
import re
import json
import datetime


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
        "京东现场私有化环境":"http://192.168.1.100:30017/api/auth/login?auth_type=USER&username=YOUR_ACCOUNT&password=YOUR_PASSWORD"
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
    print(f"tagnameurl:{url}")
    payload = json.dumps({"pageNo": 1, "pageSize": 1000000})
    tag_list = requests.post(url, headers=headers, data=payload).json()
    status = requests.post(url, headers=headers, data=payload).status_code
    print(f"status:{status}")
    print(f"tag_list:{tag_list}")
    tag_names = [name.strip() for name in tag_name.split(',')]
    print(f"tag_names:{tag_names}")
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



# def get_token111():
#     token_url = "https://your-server.example.com/api/auth/login?authType=USER&auth_type=USER&username=YOUR_ACCOUNT&password=YOUR_PASSWORD&clientId=DEVICE_MANAGEMENT"
#     token_res = requests.post(url=token_url).text
#     return re.findall(r'"token":"(.*?)","refreshedToken"', token_res)[0]

# headers = {'Authorization': get_token111(),
#            'User-Agent': 'apifox/1.0.0 (https://www.apifox.cn)',
#            'Content-Type': 'application/json'}
#
# url_list = "https://your-server.example.com/api/wisdom/task/time/list"
# payload = json.dumps({"pageNo": 1, "pageSize": 100})
# res_list = requests.post(url_list, headers=headers, data=payload).json()
# task_id = res_list['data']['content']
# for i in task_id:
#     task_id1 = i['id']
#     print(task_id1)
#     url_delete = f"https://your-server.example.com/api/wisdom/task/time/{task_id1}"
#     requests.delete(url_delete, headers=headers)


