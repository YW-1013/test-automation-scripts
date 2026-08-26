import os
from conf import *

suit_dir = CASE_PATH



def get_all_cases():
    cases = []
    cases_name = []
    for dirpath, dirnames, failenames in os.walk(suit_dir):
        for dirname in dirnames:
            if dirname.endswith(".air"):
                cases.append(os.path.join(dirpath, dirname))
                cases_name.append(dirname)
    return cases, cases_name

cases_total_list, cases_name_list = get_all_cases()  # 获取总用例的路径和名称

for number in range(0,len(cases_total_list)):
    # print(cases_name_list[number],cases_total_list[number])
    list_case_name = os.listdir(cases_total_list[number])
    sign_pyname = 0
    for i in list_case_name:
        if i.endswith(".py"):
            py_case_name = i.split(".")[0]
            sign_pyname = 1
            break
    if sign_pyname == 0:
        print(f"{cases_name_list[number]}下没有py脚本")

    dir_case_name = cases_name_list[number].split(".")[0]
    if dir_case_name != py_case_name:
        print(f"{cases_name_list[number]}文件夹名称和py脚本名称不一致")