
import unittest
import os
from common.initPath import CASEDIR, REPORTDIR
from kemel.methodFactory import MethodFactory
from library.HTMLTestRunnerNew import HTMLTestRunner

class TestRun(object):
    metFac = MethodFactory()
    def __init__(self):
        self.suit = unittest.TestSuite()
        load = unittest.TestLoader()
        self.suit.addTest(load.discover(CASEDIR))

        self.runner = HTMLTestRunner(
            stream=open(os.path.join(REPORTDIR, 'report.html'), 'wb'),
            title='接口自动化测试报告',
            description='代替手动冒烟、手动回归，做更精准的测试',
            tester='Yaowei'
        )

    def excute(self):
        self.runner.run(self.suit)
        self.metFac.method_factory(method='发送邮件')



if __name__=='__main__':
    run = TestRun()
    run.excute()


