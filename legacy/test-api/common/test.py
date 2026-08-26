import requests

headers = {"Content-Type":"application/json;charset=utf-8"}
url = "http://your-server.example.com/ota/pkg/package/find-update-info"
data = {"system": {"id": "W_Whiteboard","sn": "27","version":"0.2.1.8"},
        "applications": [{"id": "W_Whiteboard","sn": "44","version":"0.2.1.8"},{"id": "W_Launcher","sn": "7","version":"4.0.0.1"}]
        }
res = requests.post(url=url,json=data)
print(res.json())