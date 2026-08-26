# import requests
# import json
# url = 'YOUR_FEISHU_WEBHOOK_URL'
#
# # -*- coding: utf-8 -*-
import requests


def push_report(web_hook,message_body):
    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    ChatRob = requests.post(url=web_hook, json=message_body, headers=header)
    opener = ChatRob.json()
    print("opener:{}".format(opener))
    if opener["StatusMessage"] == "success":
        print(u"%s 通知消息发送成功！" % opener)
    else:
        print(u"通知消息发送失败，原因：{}".format(opener))


if __name__ == '__main__':

    message_body = {
        "msg_type": "text",
        "content": {
            "text": "消息推送展示项目：飞书\n" +
                    ">>环境：测试环境 \n" +
                    ">>类型：%s \n" % "消息推送" +
                    ">>测试结果：%s \n" % "通过"
        }

    }
    webhook = 'YOUR_FEISHU_WEBHOOK_URL'
    push_report(webhook,message_body)