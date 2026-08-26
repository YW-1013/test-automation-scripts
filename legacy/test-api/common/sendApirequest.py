


import requests

# # HTTP请求类型
# # get类型
# r = requests.get('https://github.com/timeline.json')
# # post类型
# r = requests.post("http://m.ctrip.com/post")
# # put类型
# r = requests.put("http://m.ctrip.com/put")
# # delete类型
# r = requests.delete("http://m.ctrip.com/delete")
# # head类型
# r = requests.head("http://m.ctrip.com/head")
# # options类型
# r = requests.options("http://m.ctrip.com/get")
#
# # 获取响应内容
# print(r.content) #以字节的方式去显示，中文显示为字符
# print(r.text) #以文本的方式去显示












class SendApirequests(object):

    def __init__(self):
        self.session = requests.session()

    def request_Obj(self, method, url, params=None, data=None, json=None, files=None, headers=None,):
        opetype = str.lower(method)
        if opetype == 'get':
            response = requests.get(url=url, params=params, headers=headers)
        elif opetype == 'post':
            response = requests.post(url=url, json=json, data=data, files=files, headers=headers)
        print('--------------------')
        return response


# api = SendApirequests()
# #
# res = api.request_Obj('post', url='http://your-server.example.com/ota/pkg/package/find-update-info',headers={"Content-Type":"application/json;charset=utf-8"},json={"system":{"id":"W_Whiteboard","sn":"27","version":"0.2.1.8"},"applications":[{"id":"W_Whiteboard","sn": "44","version":"0.2.1.8"},{"id": "W_Launcher","sn":"7","version":"4.0.0.1"}]})
# print(res.text)