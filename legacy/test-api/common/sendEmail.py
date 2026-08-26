import os
import smtplib
from common.getConfig import myCof
from email.mime.text import MIMEText  #导入纯文本格式
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from common.initPath import REPORTDIR

# host = myCof.getValue('email', 'host')
# port = int(myCof.getValue('email', 'port'))
# user = myCof.getValue('email', 'user')
# pwd = myCof.getValue('email', 'pwd')
# to_addr = myCof.getValue('email', 'to_addr')
# #定义纯文本消息 ，From定义发件人, To定义收件人， Subject定义邮件标题
# msg = MIMEText('hello，send by python_test...','plain','utf-8')
# msg['From'] = user
# msg['To'] = to_addr
# msg['Subject'] = '测试邮件发送'
# try:
#     #连接smtp服务对话，创建对像
#     smtp = smtplib.SMTP_SSL(host=host, port=port)
#     #登录服务器
#     smtp.login(user=user, password=pwd)
#     # 发送邮件
#     smtp.sendmail(from_addr=user, to_addrs=to_addr, msg=msg.as_string())
#     # 结束与服务器的对话
#     smtp.quit()
#     print('发送邮件成功')
# except Exception as e:
#     print('发送邮件失败，原因：{}'.format(str(e)))

class SendMail(object):

    def __init__(self):
        """
        初始化文件路径与相关配置
        """
        all_path = []
        #获取测试报告目录下的报告文件名称
        for maindir, subdir, file_list in os.walk(REPORTDIR):
            pass

        #拼接文件绝对路径
        for filename in file_list:
            all_path.append(os.path.join(REPORTDIR, filename))
        self.filename = all_path[0]
        self.host = myCof.get('email', 'host')
        self.port = myCof.get('email', 'port')
        self.user = myCof.get('email', 'user')
        self.pwd = myCof.get('email', 'pwd')
        self.from_addr = myCof.get('email', 'from_addr')
        self.to_addr = myCof.get('email', 'to_addr')



    def get_email_host_smtp(self):
        """
        连接stmp服务器
        :return:
        """
        try:
            self.smtp = smtplib.SMTP_SSL(host=self.host, port=self.port)
            self.smtp.login(user=self.user, password=self.pwd)
            return True, '连接成功'
        except Exception as e:
            return False, '连接邮箱服务器失败，原因：' + str(e)


    def made_msg(self):
        """
        构建一封邮件
        :return:
        """
        # 新增一个多组件邮件
        self.msg = MIMEMultipart()

        with open(self.filename, 'rb') as f:
            content = f.read()
        # 创建文本内容
        text_msg = MIMEText(content, _subtype='html', _charset='utf8')
        # 添加到多组件的邮件中
        self.msg.attach(text_msg)
        # 创建邮件的附件
        report_file = MIMEApplication(content)
        report_file.add_header('Content-Disposition', 'attachment', filename=str.split(self.filename, '\\').pop())

        self.msg.attach(report_file)
        # 主题
        self.msg['subject'] = '自动化测试报告'
        # 发件人
        self.msg['From'] = self.from_addr
        # 收件人
        self.msg['To'] = self.to_addr


    def send_email(self):
        """
        发送邮件
        :return:
        """
        isOK, result = self.get_email_host_smtp()
        if isOK:
            self.made_msg()
            self.smtp.send_message(self.msg, from_addr=self.from_addr, to_addrs=self.to_addr)
        else:
            return isOK, result
        return isOK, '发送邮件成功'


# abc = SendMail()
# abc.send_email()

