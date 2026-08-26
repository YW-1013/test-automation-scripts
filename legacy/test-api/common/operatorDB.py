import pymysql
from common.getConfig import myCof

# host = myCof.getValue('db', 'host')
# port = int(myCof.getValue('db', 'port'))
# user = myCof.getValue('db', 'user')
# pwd = myCof.getValue('db', 'pwd')
# database = myCof.getValue('db', 'database')
# charset = myCof.getValue('db', 'charset')
# try:
#     #连接数据库
#     db = pymysql.connect(host=host, port=port, user=user, password=pwd, database=database, charset=charset)
#     #获取游标
#     cursor = db.cursor()
#     #执行SQL
#     cursor.execute("select * from Student where SName = '林小六';")
#     #获取查询结果
#     result = cursor.fetchall()
#     #打印查询结果
#     print(result)
#     print('执行成功')
# except Exception as e:
#     print('连接失败，原因：{}'.format(str(e)))
"""
封装mysql操作
"""
class OpeartorDB(object):
    def __init__(self):
        """
        初始化方法，习惯性留着
        """
        pass

    def connectDB(self):
        """
        连接数据库
        :return: 返回成功失败，原因
        """
        host = myCof.getValue('db', 'host')
        port = myCof.getValue('db', 'port')
        user = myCof.getValue('db', 'user')
        pwd = myCof.getValue('db', 'pwd')
        database = myCof.getValue('db', 'database')
        charset = myCof.getValue('db', 'charset')
        try:
            self.db = pymysql.connect(host=host, port=int(port), user=user, password=pwd, database=database, charset=charset)
            return True, '连接数据成功'
        except Exception as e:
            return False, '连接数据失败【' + str(e) + '】'


    def closeDB(self):
        """
        关闭数据连接，不关闭会导致数据连接数不能释放，影响数据库性能
        :return:
        """
        self.db.close()

    def excetSql(self, enpsql):
        """
        执行sql方法，
        :param enpsql: 传入的sql语句
        :return: 返回成功与执行结果 或 失败与失败原因
        """
        isOK, result = self.connectDB()
        if isOK is False:
            return isOK, result
        try:
            cursor = self.db.cursor()
            cursor.execute(enpsql)
            res = cursor.fetchone()     #为了自动化测试的速度，一般场景所以只取一条数据
            if res is not None and 'select' in enpsql.lower():
                des = cursor.description[0]
                result = dict(zip(des, res))
            elif res is None and ('insert' in enpsql.lower() or 'update' in enpsql.lower()):
                self.db.commit()
                result = ''
            cursor.close()
            self.closeDB()
            return True, result
        except Exception as e:
            return False, 'SQL执行失败,原因：[' + str(e) + ']'





# sql = 'select * from Student'
# oper = OpeartorDB()
# isOK, result = oper.excetSql(sql)
# print(result)


