import requests
import logging
logger = logging.getLogger("root")
logger.setLevel(logging.INFO)

sh_token = "YOUR_SPREADSHEET_TOKEN"

# 获取tat，返回值类型为string
def get_tat():
    url= "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    #应用凭证里的 app id 和 app secret
    post_data = {"app_id": "YOUR_FEISHU_APP_ID", "app_secret": 'YOUR_FEISHU_APP_SECRET'}
    r = requests.post(url, data=post_data)
    return r.json()["tenant_access_token"]

# 获取表格的所有sheet_id，返回值类型为一维数组
def get_sheet_id(tat, sh_token):
    sheet_id_list = []
    url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{sh_token}/sheets/query/'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(tat)
    }
    rsp = requests.get(url, headers=headers).json()
    for msg in rsp['data']['sheets']:
        sheet_id_list.append(msg['sheet_id'])
    logger.info(rsp['msg'])
    return sheet_id_list

# 获取表格的所有sheet的标题，返回值类型为一维数组
def get_sheet_title(tat, sh_token):
    sheet_title_list = []
    url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{sh_token}/sheets/query/'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(tat)
    }
    rsp = requests.get(url, headers=headers).json()
    for msg in rsp['data']['sheets']:
        sheet_title_list.append(msg['title'])
    logger.info(sheet_title_list)
    return sheet_title_list

# 获取数据，返回值类型为二维数组
def get_value(tat, sh_token, sheet_id, start_range, end_range):
    url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sh_token}/values/{sheet_id}!{start_range}:{end_range}'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(tat)
    }
    rsp = requests.get(url, headers=headers).json()
    logger.info(f'获取{start_range}至{end_range}数据：' + rsp['msg'])
    return rsp['data']['valueRange']['values']

list_ids = get_value(get_tat(), sh_token, "6om725", "C", "E")
for list_id in list_ids:
    if list_id[1] != "封装名称" and list_id[1] != None and list_id[1] != "函数封装":
        print(f"#{list_id[0]}")
        print(f"{list_id[1]} = '{list_id[2]}'")
