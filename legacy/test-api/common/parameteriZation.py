import re
import json
from common.getConfig import myCof
null=None
# phone = myCof.getValue('par','phone')
# print(phone)
# pwd = myCof.getValue('par', 'pwd')
# print(pwd)
#定义一个字符串，里面有两个变量
# data = '{PHONE : ${phone}, PASSWORD: ${pwd}}'
# #定义正则匹配规则
# ru = r'\${(.*?)}'
# #循环取变量名称
# while re.search(ru, data):
#     #取值第一个变量
#     res = re.search(ru, data)
#     #取出名称
#     key = res.group(1)
#     #取出环境变量
#     value = myCof.getValue('par', key)
#     #替换变量
#     data = re.sub(ru, value, data, 1)
# #打印替换后的字符串
# print(data)

# 给临时变量的空类
# class Paramete():
#     pass
# # 设置临时变量
# setattr(Paramete, 'phone', 'YOUR_PHONE')
# setattr(Paramete, 'pwd', '654321')
# # 直接调用取值打印
# # print('直接打印：' + Paramete().phone)
# # 通过getattr打印
# # print('getattr打印：' + getattr(Paramete, 'phone'))
# data = '{PHONE : ${phone}, PASSWORD: ${pwd}}'
# #定义正则匹配规则
# ru = r'\${(.*?)}'
# #循环取变量名称
# while re.search(ru, data):
#     #取值第一个变量
#     res = re.search(ru, data)
#     #取出名称
#     key = res.group(1)
#     #取出环境变量
#     value = getattr(Paramete, key)
#     #替换变量
#     data = re.sub(ru, value, data, 1)
#
# print(data)

class Paramete:
    pass

def replace_data(data):
    """
    替换变量
    :param data:
    :return:
    """
    ru = r'\${(.*?)}'
    while re.search(ru, data):
        res = re.search(ru, data)
        item = res.group()
        keys = res.group(1)

        # 先找系统环境变量，如果有则替换；如果没有则找临时变量
        try:
            value = myCof.get('test_data', keys)
        except Exception as e:
            try:
                value = getattr(Paramete, keys).encode('utf-8').decode('unicode_escape')
            except Exception as e:
                value = getattr(Paramete, keys)
        finally:
            if keys == 'response':
                d_header = dict(value.headers)
                d_resbody = eval(value.text)
                d_response = dict(d_header)
                d_response.update(d_resbody)
                value_1 = json.dumps(d_response).encode('utf-8').decode('unicode_escape')
                data = re.sub(ru, value_1, data, 1)
            else:
                data = re.sub(ru, value, data, 1)
    return data

def analyzing_param(param):
    """
     ${abc}取出abc
    :param param:
    :return:
    """
    ru = r'\${(.*?)}'
    if re.search(ru, param):
        return re.findall(ru, param)[0]
    return param

# print(replace_data('${phone}, ${pwd}'))