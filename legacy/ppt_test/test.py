import requests
from lxml import etree
import time
import string
from feishu_sheet import FeishuSheet
def get_wps_all_version_cn():
    url = 'https://www.wandoujia.com/apps/280841/history'
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'}
    rsp = requests.get(url=url, headers=headers)
    content = rsp.content
    tree = etree.HTML(content)
    vcode_list = tree.xpath('//ul[@class="old-version-list"]/li/a/@data-app-vcode')
    dl_url_list = []
    for vcode in vcode_list:
        v_url = url + '_v' + vcode
        rsp = requests.get(v_url, headers=headers)
        rsp.close()
        time.sleep(0.5)
        content = rsp.content
        tree = etree.HTML(content)
        try:
            dl_url = tree.xpath('//div[@class="button-wrap"]/a[@class="__normal_realname__ normal-dl-btn"]/@data-href')[0]
            dl_url_list.append(dl_url)
            version = tree.xpath('//p[@class="version-name"]/span/text()')[0]
            dl_url_list.append(version)
        except:
            print('当前版本已失效，无安装包')
    return dl_url_list
        # print(dl_url)
    # return dl_url_list
def get_wps_vcode_list():
    url = 'https://www.wandoujia.com/apps/280841/history'
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'}
    rsp = requests.get(url=url, headers=headers)
    content = rsp.content
    tree = etree.HTML(content)
    vcode_list = tree.xpath('//ul[@class="old-version-list"]/li/a/@data-app-vcode')
    return vcode_list
# def get_dl_url(vcode):
#     url = f'https://www.wandoujia.com/apps/280841/history_v{vcode}'
#     rsp = requests.get(url=url, allow_redirects=False)
#     content = rsp.content
#     tree = etree.HTML(content)
#     dl_url = tree.xpath('//div[@class="button-wrap"]/a[@class="__normal_realname__ normal-dl-btn"]/@data-href')[0]
#     return dl_url
if __name__ == '__main__':
    # url_all = get_wps_all_version_cn()
    # print(len(url_all))
    # print(url_all)
    # for i in url_all:
    #     print(i)
    def get_excel_column_name(column_index):
        """
        根据Excel表格的列索引，生成对应的列标识符
        :param column_index: 列索引，从1开始
        :return: 列标识符
        """
        if not isinstance(column_index, int) or column_index < 1:
            raise ValueError('Invalid column index: {}'.format(column_index))
        column_index -= 1
        quotient = column_index // 26
        remainder = column_index % 26
        if quotient == 0:
            return string.ascii_uppercase[remainder]
        else:
            return get_excel_column_name(quotient) + string.ascii_uppercase[remainder]


    sh_token = 'YOUR_SPREADSHEET_TOKEN'
    sheet_id = ''
    # token两小时过期，推荐每次循环重新新建对象
    feishu_st = FeishuSheet(sh_token)
    # 新增一列
    feishu_st.add_cols(sheet_id, 1)
    # 获取列数
    col_index = feishu_st.get_col_index(sheet_id)
    # 根据列数生成最后一列对应excel列名
    col_name = get_excel_column_name(col_index)
    # 在对应列第一行写入版本名
    feishu_st.values(sheet_id, [["1.2.3.0"]], f'{col_name}1', f'{col_name}1')