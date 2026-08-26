from common.getConfig import myCof
from kemel.commKeyword import CommKeyword

# #初始化公共方法模块
# comKey = CommKeyword()
# #获取所有公共方法配置参数
# comKW = dict(myCof.items('commkey'))
# #获取 取用例方法名称
# method_Name = comKW['获取当前执行用例']
# #通过getattr 获取公共方法模块的对应的模块
# func = getattr(comKey, method_Name, None)
# #执行前面获取的公共方法得到用例
# cases = func(aa=None)
# #打印用例
# print(cases)

class MethodFactory(object):

    def __init__(self):
        self.comKey = CommKeyword()
        self.comKW = dict(myCof.items('commkey'))


    def method_factory(self, **kwargs):
        """
        用例公共方法工厂
        默认传的参数为：
        result:用来接收结果的变量，格式可为${abc}
        method:调用的方法，这里设计方法都使用中文
        param_x:参数，数量不限。格式可为${abc}会替换为已存在的数据
        """

        #m_bool = False
        if kwargs.__len__() > 0:
            try:
                kwargs['method']
            except KeyError:
                return False, 'keyword:用例[method]字段方法没参数为空.'
            try:
                method = self.comKW[str(kwargs['method']).lower()]
            except KeyError:
                return False, 'keyword:方法[' + kwargs['method'] + '] 不存在,或未注册.'
        try:
            func = getattr(self.comKey, method, None)
            _isOk, reselt = func(**kwargs)
            return _isOk, reselt
        except Exception as e:
            return False, 'keyword:执行失败，估计不存在，异常：' + str(e)





# fac = MethodFactory()
# print(fac.method_factory(method='获取当前用例文件名称'))




