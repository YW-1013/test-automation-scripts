import json
import os
import openpyxl
from common.initPath import DATADIR
from common.getConfig import myCof

# #拼接用例文件绝对路径
# caseFile = os.path.join(DATADIR, 'testcases.xlsx')
# print(caseFile)
# #读取excel文件
# xl = openpyxl.open(filename=caseFile)
# #打印caseFile里的sheet页名称
# print('打印所有sheet页')
# for sheet in  xl:
#     print(sheet.title)
# #打印excel里的所有的行字段数据
# print('打印Sheet1里的所有的行字段数据')
# sh = xl['Sheet1']
# data = list(sh.rows)
# for da in data:
#     for k in da:
#         print(k.value)


class Getcase(object):
    def __init__(self, sheet_name=None):
        """
        初始化文件名称，sheet名称,excel对像
        :param sheet_name: 传入的sheet名称 ，可以为空。
        """
        filename = myCof.getValue('case', 'testCase')
        self.note = myCof.getValue('identifier', 'note')
        self.caseFile = os.path.join(DATADIR, filename)
        self.sheet_name = sheet_name
        self.wb = None

    def openexcel(self):
        """
        打开excel文件
        如果sheet名称不为空，定位到对应sheet页
        :return:
        """
        self.wb = openpyxl.open(self.caseFile)
        if self.sheet_name is not None:
            self.sh = self.wb[self.sheet_name]


    def read_excels(self):
        """
        格式化用例集
        用例格式JSON见上面的前面的描述
        过滤掉#注释的用例
        :return:
        """
        if self.wb is None:
            self.openexcel()
        datas = list(self.sh.rows)
        title = [i.value for i in datas[0]]
        cases = []
        for i in datas[1:]:
            data = [k.value for k in i]
            case = dict(zip(title, data))
            try:
                if str(case['case_id'])[0] is not self.note:  # 过滤掉note符号开头的用例，注释掉不收集、不执行
                    case['sheet'] = self.sh.title
                    cases.append(case)
            except KeyError:
                cases.append(case)
        return cases

    def read_all_excels(self):
        """
        遍历所有的sheet页
        取得所有用例集，再格式下一次，
        过滤掉#注释的sheet页
        :return:
        """
        self.openexcel()
        cases = []
        for sheet in self.wb:
            if sheet.title[0] is not self.note:  # 过滤掉note符号开头的sheet页，注释掉的不收集，不执行
                self.sh = sheet
                cases += self.read_excels()
        return cases


    def write_excels(self, rows, column, value):
        """
        回写用例字段
        :param rows:
        :param column:
        :param value:
        :return:
        """
        self.openexcel()
        self.sh.cell(row=rows, column=column, value=value)
        self.wb.save(self.caseFile)


# readExce = Getcase()
# res = readExce.read_all_excels()[1]['data']
# res = json.loads(res)
# print(res)
# print(type(res))