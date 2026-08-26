import os
import logging
from common.getConfig import myCof
from common.initPath import LOGDIR
from logging.handlers import TimedRotatingFileHandler

# # 获取日志等配置参数
# level = myCof.getValue('log', 'level')
# # 设置日志格式，%(asctime)s表示时间，%(name)s表示传入的标识名，%(levelname)s表示日志等级，%(message)s表示日志消息
# format = '%(asctime)s - %(name)s-%(levelname)s: %(message)s'
# # 设置日志基础等级, 设置
# logging.basicConfig(level=level, format=format)
# # 初始化日志对像，Hunwei是name
# mylog = logging.getLogger('Hunwei')
# #拼接日志目录
# log_path = os.path.join(LOGDIR, 'testReport')
# #生成文件句柄，filename是文件路径，when表是时间D表示天，backuCount=15目录下最多15个日志文件，enccoding='utf-8'日志字符格式
# fh = TimedRotatingFileHandler(filename=log_path, when="D", backupCount=15, encoding='utf-8')
# #设置历史日志文件名称的格式，会自动按照某天生成对应的日志
# fh.suffix = "%Y-%m-%d.log"
# #设置文件输出的日志等级
# fh.setLevel(level)
# #设置文件输出的日志格式
# fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s-%(levelname)s: %(message)s"))
# #将文件句柄加入日志对象
# mylog.addHandler(fh)
#
# mylog.debug('debug')
# mylog.info('info')
# mylog.warn('warm')
# mylog.error('error')
# mylog.fatal('fatal')



class Log(object):

    @staticmethod
    def getMylog():
        # 获取日志等配置参数
        level = myCof.getValue('log', 'level')
        # 设置日志格式，%(asctime)s表示时间，%(name)s表示传入的标识名，%(levelname)s表示日志等级，%(message)s表示日志消息
        format = '%(asctime)s - %(name)s-%(levelname)s: %(message)s'
        # 设置日志基础等级, 设置
        logging.basicConfig(level=level, format=format)
        # 初始化日志对像，Hunwei是name
        mylog = logging.getLogger('Hunwei')
        # 拼接日志目录
        log_path = os.path.join(LOGDIR, 'testReport')
        # 生成文件句柄，filename是文件路径，when表是时间D表示天，backuCount=15目录下最多15个日志文件，enccoding='utf-8'日志字符格式
        fh = TimedRotatingFileHandler(filename=log_path, when="D", backupCount=15, encoding='utf-8')
        # 设置历史日志文件名称的格式，会自动按照某天生成对应的日志
        fh.suffix = "%Y-%m-%d.log"
        # 设置文件输出的日志等级
        fh.setLevel(level)
        # 设置文件输出的日志格式
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s-%(levelname)s: %(message)s"))
        # 将文件句柄加入日志对象
        mylog.addHandler(fh)
        #返回mylog对像
        return mylog


mylog = Log.getMylog()
# mylog.debug('debug')
# mylog.info('info')
# mylog.warn('warm')
# mylog.error('error')
# mylog.fatal('fatal')











