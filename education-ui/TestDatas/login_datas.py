
# 成功登录的账号
success_data = [
    {"user": "YOUR_ACCOUNT", "passwd": "YOUR_PASSWORD", "check": "YOUR_NAME"},
    ]

# 用户不存在、密码错误
wrong_datas = [
    {"user": "wrong_user", "passwd": "badpasswd", "check": "用户不存在"},
    {"user": "YOUR_ACCOUNT", "passwd": "badpasswd", "check": "登录密码错误"},
    ]

# 用户名为空
no_user = [
    {"user": "", "passwd": "badpasswd", "check": "用户名不能为空"}
    ]

# 密码为空
no_passwd = [
    {"user": "wrong_user", "passwd": "", "check": "密码不能为空"}
    ]