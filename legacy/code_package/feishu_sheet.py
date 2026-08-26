import threading

import requests
import json

# from log import logger

# def every_n_seconds(n):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             while True:


r'''通用参数释义

:param tat: 飞书机器人应用的tenant_access_token，调用api的凭证，通过get_tat函数获取，最大有效期2小时
:param sh_token: 所操作的飞书文档的spreadsheet值，从url中获取
                 示例：https://your-tenant.feishu.cn/sheets/{spreadsheet}
:param sheet_id: 所操做飞书文档工作表的id，从url中获取
                 示例：https://your-tenant.feishu.cn/sheets/{spreadsheet}?sheet={sheet_id}
:param values: 写入、查找的值
:param new_values: (仅用于replace函数)通过values查找后进行替换的值
:param start_range: 操作的起始位置（单元格、行、列皆可），类型为string，参照https://open.feishu.cn/document/ukTMukTMukTM/uATMzUjLwEzM14CMxMTN/overview中四种定位方式
:param end_range: 操作的结束位置（单元格、行、列皆可），类型为string，参照https://open.feishu.cn/document/ukTMukTMukTM/uATMzUjLwEzM14CMxMTN/overview中四种定位方式
:param start_index: 操作的起始位置（行、列），类型为int，从第{start_index}行/列开始
:param start_index: 操作的结束位置（行、列），类型为int，到第{start_index}行/列结束
:return: 返回得到数据
'''
class FeishuSheet():
    def __init__(self, sh_token):
        self.tat = self.get_tat()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tat
        }
        self.sh_token = sh_token

    def get_tat(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        # 应用凭证里的 src id 和 src secret
        post_data = {"app_id": "YOUR_FEISHU_APP_ID", "app_secret": 'YOUR_FEISHU_APP_SECRET'}
        rsp = requests.post(url, data=post_data)
        return rsp.json()["tenant_access_token"]

    # 获取表格的所有sheet_id，返回值类型为一维数组
    def get_sheet_id(self):
        sheet_id_list = []
        url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{self.sh_token}/sheets/query/'
        rsp = requests.get(url, headers=self.headers).json()
        for msg in rsp['data']['sheets']:
            sheet_id_list.append(msg['sheet_id'])
        # logger.info(rsp['msg'])
        return sheet_id_list

    # 获取表格的所有sheet的标题，返回值类型为一维数组
    def get_sheet_title(self):
        sheet_title_list = []
        url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{self.sh_token}/sheets/query/'
        rsp = requests.get(url, headers=self.headers).json()
        for msg in rsp['data']['sheets']:
            sheet_title_list.append(msg['title'])
        # logger.info(sheet_title_list)
        return sheet_title_list

    # 获取数据，返回值类型为二维数组
    def get_value(self, sheet_id, start_range, end_range):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/values/{sheet_id}!{start_range}:{end_range}'
        rsp = requests.get(url, headers=self.headers).json()
        # logger.info(f'获取{start_range}至{end_range}数据：' + rsp['msg'])
        return rsp['data']['valueRange']['values']

    # 插入数据：插入行列同时写入数据
    def values_prepend(self, sheet_id, values, start_range, end_range):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/values_prepend'
        post_data = {
            "valueRange": {
                "range": f"{sheet_id}!{start_range}:{end_range}",
                "values": values
            }
        }
        rsp = requests.post(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 写入数据
    def values(self, sheet_id, values, start_range, end_range):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/values'
        post_data = {

            "valueRange": {
                "range": f"{sheet_id}!{start_range}:{end_range}",
                "values": values
            }
        }
        rsp = requests.put(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 隐藏行
    def hide_rows(self, sheet_id, start_index, end_index):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/dimension_range'
        post_data = {
            "dimension":{
                "sheetId": f"{sheet_id}",
                "majorDimension": "ROWS",
                "startIndex": f"{start_index}",
                "endIndex": f"{end_index}"
                },
            "dimensionProperties": {
                "visible": 'false',
                # "fixedSize":50
                }
            }

        rsp = requests.put(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 隐藏列
    def hide_cols(self, sheet_id, start_index, end_index):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/dimension_range'
        post_data = {
            "dimension":{
                "sheetId": f"{sheet_id}",
                "majorDimension": "COLUMNS",
                "startIndex": f"{start_index}",
                "endIndex": f"{end_index}"
                },
            "dimensionProperties": {
                "visible": 'false',
                # "fixedSize":50
                }
            }

        rsp = requests.put(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 插入行
    def insert_rows(self, sheet_id, start_index, end_index):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/insert_dimension_range'
        post_data = {
            "dimension": {
                "sheetId": f"{sheet_id}",
                "majorDimension": "ROWS",
                "startIndex": start_index,
                "endIndex": end_index
                }
            }

        rsp = requests.post(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 插入列
    def insert_cols(self, sheet_id, start_index, end_index):

        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/insert_dimension_range'
        post_data = {
            "dimension": {
                "sheetId": f"{sheet_id}",
                "majorDimension": "COLUMNS",
                "startIndex": start_index,
                "endIndex": end_index
                },
            }

        rsp = requests.post(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 删除行
    def delete_rows(self, sheet_id, start_index, end_index):

        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/insert_dimension_range'
        post_data = {
            "dimension": {
                "sheetId": f"{sheet_id}",
                "majorDimension": "ROWS",
                "startIndex": f"{start_index}",
                "endIndex": f"{end_index}"
                }
            }

        rsp = requests.delete(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 删除列
    def delete_cols(self, sheet_id, start_index, end_index):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/insert_dimension_range'

        post_data = {
            "dimension": {
                "sheetId": f"{sheet_id}",
                "majorDimension": "COLUMNS",
                "startIndex": f"{start_index}",
                "endIndex": f"{end_index}"
                }
            }

        rsp = requests.delete(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    # 查找，返回值为查找值的位置，类型为数组, eg:  ['C2']
    def find(self, sheet_id, values, start_range, end_range):
        url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{self.sh_token}/sheets/{sheet_id}/find'
        post_data = {
            "find_condition": {
                "range": f"{sheet_id}!{start_range}:{end_range}",
                # 是否区分大小写
                "match_case": "true",
                # 是否完全匹配
                "match_entire_cell": "false",
                # 是否正则匹配
                "search_by_regex": "false",
                # 是否仅搜索公式
                "include_formulas": "false"
                },
            "find": values
            }

        rsp = requests.post(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])
        return rsp.json()['data']['find_result']['matched_cells']

    # 查找并替换
    def replace(self, sheet_id, values, new_values, start_range, end_range):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/find'
        post_data = {
            "find_condition": {
                "range": f"{sheet_id}!{start_range}:{end_range}",
                # 是否区分大小写
                "match_case": "true",
                # 是否完全匹配
                "match_entire_cell": "false",
                # 是否正则匹配
                "search_by_regex": "false",
                # 是否仅搜索公式
                "include_formulas": "false"
                },
            "find": f"{values}",
            "replacement": f"{new_values}"
            }

        rsp = requests.post(url, data=json.dumps(post_data), headers=self.headers)
        # logger.info(rsp.json()['msg'])

    def get_row_index(self, sheet_id):
        url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{self.sh_token}/sheets/{sheet_id}'
        rsp = requests.get(url, headers=self.headers).json()
        # logger.info(rsp['msg'])
        return rsp['data']['sheet']['grid_properties']['row_count']

    def get_col_index(self, sheet_id):
        url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{self.sh_token}/sheets/{sheet_id}'
        rsp = requests.get(url, headers=self.headers).json()
        # logger.info(rsp['msg'])
        return rsp['data']['sheet']['grid_properties']['column_count']

    def add_cols(self, sheet_id, length):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/dimension_range'
        post_data = {
            "dimension": {
                "sheetId": sheet_id,
                "majorDimension": "COLUMNS",
                "length": length
            }
        }
        rsp = requests.post(url, data=json.dumps(post_data), headers=self.headers).json()
        # logger.info(rsp['msg'])

    def add_rows(self, sheet_id, length):
        url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.sh_token}/dimension_range'
        post_data = {
            "dimension": {
                "sheetId": sheet_id,
                "majorDimension": "ROWS",
                "length": length
            }
        }
        rsp = requests.post(url, data=json.dumps(post_data), headers=self.headers).json()
        # logger.info(rsp['msg'])