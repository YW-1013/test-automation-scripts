
import requests
import json
from common.getConfig import myCof

# # 获取企业微信的参数
# corpid = myCof.get('wechat', 'corpid')
# corpsecret = myCof.get('wechat', 'corpsecret')
# agentid = myCof.get('wechat', 'agentid')
# # 拼接获取token的API
# url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + corpsecret
# # 使用requests请求API，转为JSON格式
# response = requests.get(url)
# res = response.json()
# #获取token打印
# token = res['access_token']
# print(token)
# # 拼接发送消息的api
# url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + token
# # 构建一个消息JSON串
# jsonmsg = {
#                "touser" : "@all",
#                "msgtype" : "text",
#                "agentid" : agentid,
#                "text" : {
#                    "content" : "API接口从无到有"
#                },
#                "safe":0
#             }
# # 将JSON转成str，再转成bytes格式的消息休
# data = (bytes(json.dumps(jsonmsg), 'utf-8'))
# # 使用requests post发送消息
# requests.post(url, data, verify=False)

class SendMsg(object):
    def __init__(self):
        self.corpid = myCof.get('wechat', 'corpid')
        self.corpsecret = myCof.get('wechat', 'corpsecret')
        self.agentid = myCof.get('wechat', 'agentid')


    def getToken(self):
        if self.corpid is None or self.corpsecret is None:
            return False, '企业微信相关信息未配置'
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + self.corpid + '&corpsecret=' + self.corpsecret
        response = requests.get(url)
        res = response.json()
        self.token = res['access_token']
        return True, '企业微信token获取成功'

    def sendMsg(self, msg):
        _isOK, result = self.getToken()
        if _isOK:
            url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.token
            jsonmsg = {
                   "touser" : "@all",
                   "msgtype" : "text",
                   "agentid" : self.agentid,
                   "text" : {
                       "content" : msg
                   },
                   "safe":0
                }
            data = (bytes(json.dumps(jsonmsg), 'utf-8'))
            requests.post(url, data, verify=False)
        else:
            print(result)




# wechatMsg = SendMsg()
# wechatMsg.sendMsg('API接口从无到有')


