"""
设置测试环境以及一些基本的参数.
"""
import argparse
import json
import logging
import sys


def create_url(ip_address, code, protocol="http", port=31330, private=0):
    """通过ip直接生成地址,适用于私有化."""
    return {
        "api_auth": f"{protocol}://{ip_address}:{port}/auth",
        "api_edu": f"{protocol}://{ip_address}:{port}/education",
        "api_message": f"{protocol}://{ip_address}:{port}/message",
        "api_tenant": f"{protocol}://{ip_address}:{port}/account",
        "api_record": f"{protocol}://{ip_address}:{port}/media",
        "code": code,
        "private": private
    }


# 测试环境配置
env_api_hosts = {
    # url地址、组织代码、是否私有化
    "rd10": {
        "api_auth": "https://your-server.example.com/auth",      # 账号登录地址
        "api_edu": "http://your-server.example.com",              # 教育
        "api_device": "http://your-server.example.com",            # 集控
        "api_tenant": "https://your-server.example.com/tenant",      # 用户信息
        "api_record": "http://your-server.example.com",    # 录播
        "code": "YOUR_ORG_CODE",
        "private": 0
    },
    '116': create_url("192.168.1.100", "YOUR_ORG_CODE")
}


# 设置接收的命令行参数
option_list = [
    # 参数名称、数据类型、默认、帮助
    ('--env', str, "116", f"测试的环境，支持以下: {list(env_api_hosts.keys())}"),
    ('--host', str, "", "直接传入测试地址,若传入host，则不会使用env中的环境"),
    ('--protocol', str, 'http', "协议类型，配合host使用，默认是http."),
    ('--port', int, 31330, "端口号，配合host使用，默认是30017"),
    ('--code', str, "", "组织号，配合host使用"),
    ('--private', int, 1, '是否是私有化，1:是/0:不是'),
    ('--tags', str, "not bug", "需要执行的用例标签")
]


def pytest_options_parser(parser):
    """设置pytest接收的参数"""
    for item in option_list:
        parser.addoption(item[0],type=item[1], action="store", default=item[2], help=item[3])


def main_options_parser():
    """通过main文件启动，需要设置参数."""
    parser = argparse.ArgumentParser(description='Process some integers.')
    for item in option_list:
        parser.add_argument(item[0], type=item[1], default=item[2], help=item[3])
    args = parser.parse_args()
    options = {}
    for item in option_list:
        option_name = item[0].replace('-', '')
        options[option_name] = eval(f"args.{option_name}")

    return options


def pytest_get_options(request):
    """设置pytest参数逻辑."""
    # 如果有直接传递host进来，则使用host的环境地址
    env = request.config.getoption('env')
    host = request.config.getoption('host')
    if host != "":
        env = "自定义环境"
        ip = host
        protocol = request.config.getoption('protocol')
        port = request.config.getoption('port')
        private = request.config.getoption('private')
        code = request.config.getoption('code')
        if code == "":
            print("请输入组织码, 方式：\n --code=组织码")
            sys.exit(0)
        host_info = create_url(ip, code, protocol=protocol, port=port, private=private)
        host_info["env"] = env
    else:
        if env not in env_api_hosts:
            print(f"没有配置{env}环境，当前已配置的环境：{list(env_api_hosts.keys())}")
        host_info = env_api_hosts.get(env)
        host_info["env"] = env

    logging.info(f"\n{'#'*32}测试环境基本信息{'#'*32}\n" +
                 f"{json.dumps(host_info, indent=4)}"
                 f"\n{'#'*32}#############{'#'*32}\n")

    return host_info
