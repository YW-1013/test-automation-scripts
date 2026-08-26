import json
import jsonpath
import datetime
from common.getConfig import myCof
from common.getCase import Getcase
from common.operatorDB import OpeartorDB
from common.parameteriZation import Paramete, analyzing_param, replace_data
from common.sendApirequest import SendApirequests
from common.sendEmail import SendMail
from common.sendMsg import SendMsg

null = None




class CommKeyword(object):
    def __init__(self):
        self.operatordb = OpeartorDB()
        self.getCase = Getcase()
        self.sendApi = SendApirequests()
        self.sendMail = SendMail()
        self.sedMsg = SendMsg()


    def get_exceut_case(self, **kwargs):
        """
        获取当前执行用例
        :return: bl, cases 一参数返回成功与否，二参数用例或失败原因
        """
        try:
            cases = self.getCase.read_all_excels()
        except Exception as e:
            return False, '获取用例失败，原因：' + str(e)
        return True, cases

    def get_current_casefile_name(self, **kwargs):
        """
        获取执行用例文件名称
        :return: 返回用例文件名称
        """
        try:
            fileName = myCof.getValue('case', 'testcase')
        except Exception as e:
            return False, '参数中未设置用例文件名称，请检查配置文件'
        return True, fileName

    def send_api(self, **kwargs):
        """
        发送用例请求 post, get
        :param kwargs:  请求的参数 ，有url,headers,data等
        :return:  bl, cases 一参数返回成功与否，二参数请求结果或失败原因
        """
        try:
            url = replace_data(kwargs['url'])
            method = kwargs['method']
            if kwargs['headers'] is None:
                headers = None
            else:
                _isOk, result = self.format_headers(replace_data(kwargs['headers']))
                if _isOk:
                    headers = result
                else:
                    return _isOk, result

            if kwargs['data'] is not None:
                try:
                    jsondata = json.loads(replace_data(kwargs['data']))
                    data = None
                except ValueError:
                    data = replace_data(kwargs['data'])
                    jsondata = None
            else:
                data = None
                jsondata = None

            response = self.sendApi.request_Obj(method=method, url=url, json=jsondata, data=data, headers=headers)
        except Exception as e:
            return False, '发送请求失败' + str(e)
        return True, response , url





    def set_sheet_dict(self):
        """
        :return: excl文件里面的sheet页信息
        """
        xlsx = Getcase(myCof.get('excel', 'casename'))
        sh_dict = xlsx.sheet_count()
        setattr(Paramete, 'sheetdict', sh_dict)
        sheetdict = getattr(Paramete, 'sheetdict')
        return sheetdict


    def set_common_param(self, key, value):
        """
        :param key:  公共变量名
        :param value: 参数
        :return:
        """
        setattr(Paramete, key, value)

    def get_commom_param(self, key):
        """
        :param key: 公共变量名
        :return: 取变量值
        """
        return getattr(Paramete, key)


    def get_current_sheet_name(self):
        """
        :return: 返回当前执行用例的sheet页名称
        """
        sh_index = self.get_commom_param('sheetindex')
        sh_dict = self.get_commom_param('sheetdict')
        for sh in sh_dict:
            if sh.title().find(str(sh_index)) != -1:
                sheet_name = sh_dict[sh.title().lower()]
        return sheet_name

    def get_json_value_as_key(self, *args, **kwargs):
        """
        得到json中key对应的value,存变量param
        默认传的参数为：
        result:用来接收结果的变量
        method:调用的方法 ，带不带${    } 都行
        param_x:参数，数量不限。格式可为${    }会替换为已存在的数据
        """
        try:
            param = kwargs['result']
            jsonstr = kwargs['param_1']
            key = kwargs['param_2']
        except KeyError:
            return False, '方法缺少参数，执行失败'

        param = analyzing_param(param)
        jsonstr = replace_data(jsonstr)
        key = replace_data(key)

        if param is None or jsonstr is None or key is None:
            return False, '传入的参数为空，执行失败'
        try:
            print(jsonstr)
            result = json.loads(jsonstr)
        except Exception as e:
            a = str(e)
            return False, '传入字典参数格式错误，执行失败'
        key = '$..' + key
        try:
            value = str(jsonpath.jsonpath(result, key)[0])
        except Exception:
            return False, '字典中[' + jsonstr + ']没有键[' + key + '], 执行失败'
        setattr(Paramete, param, value)
        return True, ' 已经取得[' + value + ']==>[${' + param + '}]'



    def format_headers(self, param):
        """
        格式化请求头
        :param param:excel里读出出来的header，是从浏览器f12里直接copy的
        :return:
        """
        if param is None:
            return False, 'Headers为空'
        list_header = param.split('\n')
        headers = {}

        for li in list_header:
            buff = li.split(':')
            try:
                headers[buff[0]] = buff[1]
            except IndexError:
                return False, 'Headers格式不对'
        return True, headers


    def set_variable(self, **kwargs):
        """
        设置变量
        :param kwargs:
        :return:
        """
        try:
            var = kwargs['result']
            param = kwargs['param_1']
        except KeyError:
            return False, '方法缺少参数，执行失败'
        if var is None or param is None:
            return False, '传入的参数为空，执行失败'
        setattr(Paramete, var, param)
        return True, ' 已经设置变量[' + param + ']==>[${' + var + '}]'


    def execut_sql(self, **kwargs):
        """
        执行SQL
        :param kwargs:
        :return:
        """
        try:
            sql = kwargs['param_1']
        except KeyError:
            return False, '方法缺少参数，执行失败'
        try:
            var = kwargs['result']
            par = kwargs['param_2']
        except Exception:
            var = None
        isOK, result = self.operatordb.excetSql(sql)
        if isOK and var is not None:
            data = result[par]
            setattr(Paramete, var, data)
            return True, '执行SQL:[' + sql + ']成功，取得' + par + '的数据[' + data + ']==>[${' + var + '}]'
        elif isOK and var is None:
            return True, '执行SQL:[' + sql + ']成功'
        elif isOK is False:
            return isOK, result


    def send_email(self, **kwargs):
        """
        发送邮件
        :return:
        """
        return self.sendMail.send_email()


    def send_msg(self, **kwargs):
        """
        发送消息
        :param kwargs:
        :return:
        """
        title = kwargs['title']
        url = kwargs['url']
        code = kwargs['code']
        result = kwargs['result'].encode('utf-8').decode('unicode_escape')
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在
        msg = nowTime + '\n用例名称：' + title + '\n请求：' + url + '\n响应码：' + code + '\n响应信息：' + result
        self.sedMsg.sendMsg(msg)


# header = 'Access-Control-Allow-Credentials: true\nAccess-Control-Allow-Origin: http://test-hcz-static.pingan.com.cn\naccessToken: YOUR_ACCESS_TOKEN'
# _isOK, headers = format_headers(header)
# print(headers, type(headers))