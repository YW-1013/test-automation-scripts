import unittest
import json
from library.ddt import ddt, data
from common.log import mylog
from kemel.methodFactory import MethodFactory


isOK = True
e = Exception()

null = None

@ddt
class TestCase(unittest.TestCase):
    metFac = MethodFactory()
    isOK, cases = metFac.method_factory(method='获取当前执行用例')
    isOK, fileName = metFac.method_factory(method='获取当前用例文件名称')
    if isOK is False:
        mylog.error('获取用例失败')
        quit()

    def _opear_keyword(self, **kwargs):
        return self.metFac.method_factory(**kwargs)


    def _assert_res_expr(self, rules, reponse, expr):
        """
        断言方法
        :param rules:结果包含、结果等于、结果状态
        :param res:
        :param expr:
        :return:
        """
        try:
            res = reponse.json()
        except Exception:
            res = reponse.text

        headers = reponse.headers
        code = str(reponse.status_code)
        _reason = 'success'
        if rules == '结果包含':
            if type(expr) is str:
                res = json.dumps(res, ensure_ascii=False)
                print_result = json.dumps(json.loads(res), sort_keys=True, indent=2, ensure_ascii=False)
            else:
                print_result = res
            try:
                self.assertIn(expr, res)
            except AssertionError as e:
                _isOk = False
                _reason = '结果:\n【' + print_result + '】\n  不包含校验值:\n  【' + expr + '】'
            else:
                _isOk = True
                _reason = '结果:\n【' + print_result + '】\n  包含有校验值:\n  【' + expr + '】'
        elif rules == '结果等于':
            if type(expr) is str:
                res = json.dumps(res, ensure_ascii=False)
                print_result = json.dumps(json.loads(res), sort_keys=True, indent=2, ensure_ascii=False)
            else:
                print_result = res
            try:
                self.assertEqual(expr, res)
            except AssertionError as e:
                _isOk = False
                _reason = '结果:\n【' + res + '】\n  不等于校验值:\n  【' + expr + '】'
            else:
                _isOk = True
                _reason = '结果:\n【' + res + '】\n  等于校验值:\n  【' + expr + '】'
        elif rules == '结果状态':
            try:
                self.assertEqual(expr, code)
            except AssertionError as e:
                _isOk = False
                _reason = '结果:\n【' + code + '】\n  不等于校验值:\n  【' + expr + '】'
            else:
                _isOk = True
                _reason = '结果:\n【' + code + '】\n  等于校验值:\n  【' + expr + '】'
        elif rules == '头部包含':
            if type(expr) is str:
                headers = json.dumps(headers, ensure_ascii=False)
                print_header = json.dumps(json.loads(headers), sort_keys=True, indent=2, ensure_ascii=False)
            else:
                print_header = headers
            try:
                self.assertIn(expr, headers)
            except AssertionError as e:
                _isOk = False
                _reason = '结果头:\n【' + print_header + '】\n  不包含校验值:\n 【' + expr + '】'
            else:
                _isOk = True
                _reason = '结果头:\n【' + print_header + '】\n  包含有校验值:\n 【' + expr + '】'
        elif rules == '头部等于':
            if type(expr) is str:
                headers = json.dumps(headers, ensure_ascii=False)
                print_header = json.dumps(json.loads(headers), sort_keys=True, indent=2, ensure_ascii=False)
            else:
                print_header = headers
            try:
                self.assertEqual(expr, headers)
            except AssertionError as e:
                _isOk = False
                _reason = '结果头:\n【' + print_header + '】\n  不等于校验值:\n  【' + expr + '】'
            else:
                _isOk = True
                _reason = '结果头:\n【' + print_header + '】\n  等于校验值:\n  【' + expr + '】'
        return _isOk, _reason


    def postPinrt(self, **case):
        if case['interface'] is not None:
            print('\n------------------------------------------------------------------\n')
        print('接口：【' + case['interface'] + '】')
        if case['method'] is not None:
            print('类型：【' + case['method'] + '】')
        if case['data'] is not None:
            print('参数：【' + case['data'] + '】')
        if 'get' == str.lower(case['method']):
            if '?' in str(case['url']):
                url = str(case['url'])
                a, param = url.split('?')
                if param is not None:
                    print('参数：【')
                    datalist = str(param).split('&')
                    for data in datalist:
                        print(data)
                    print('】')
            else:
                print('【没带参数】')
        print('\n------------------------------------------------------------------\n')




    @data(*cases)
    def test_audit(self, case):
        _isOk = True


        if case['interface'] == 'commfun':
            """
            如果接口是公共方法，那么字段如下
            method：公共方法名
            title: 返回接果
            url：参数
            data：参数 ...暂时四个参数
            """
            _isOk, _strLog = self._opear_keyword(method=case['method'],
                                                 result=case['title'],
                                                 param_1=case['url'],
                                                 param_2=case['headers'],
                                                 param_3=case['data'],
                                                 param_4=case['validaterules'])
        else:
            rows = case['case_id'] + 1
            title = case['title']
            expect = str(case['expected'])
            _isOK, result = self.metFac.method_factory(**case)
            if _isOk:
                response = result
                code = str(response.status_code)
                try:
                    res = json.dumps(response.json())
                    self.metFac.method_factory(method='设置变量', result='response', param_1=response)    #返回json存
                except ValueError:
                    res = response.text
                    self.metFac.method_factory(method='设置变量', result='response', param_1=res)     #返回html 或xml、 txt存

                if case['validaterules'] is None:
                    _isOk = True
                    _strLog = '用例[' + str(case['case_id']) + ']：[' + title + ']执行完成.'
                else:
                    rules = case['validaterules']
                    _isOk, _reason = self._assert_res_expr(rules, response, expect)
                    if _isOk:
                        _strLog = '用例[' + str(case['case_id']) + ']：[' + title + ']执行通过. \n 校验结果：\n' + _reason + '123454'
                    else:
                        _strLog = "用例[" + str(case['case_id']) + ']：[' + title + ']执行不通过.\n 原因：\n' + _reason + '123455'
                        #报错的接口，给企业微信发送信息
                        self.metFac.method_factory(title=title, method='发送消息', api=case['interface'], url=case['url'], code=code, result=res)
            else:
                _strLog = "用例[" + str(case['case_id']) + ']：[' + title + ']执行不通过. \n 原因：\ n' + result + '123456'

        if _isOk:
            mylog.info(_strLog)
            print(_strLog)
            self.postPinrt(**case)

        else:
            mylog.error(_strLog)
            print(_strLog)
            self.postPinrt(**case)
            raise



test = TestCase()
test.test_audit()
