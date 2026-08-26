import logging
import sys

import pytest


@pytest.fixture(scope='session')
def users_info(option):
    if option.get('env') in ['rd10']:
        return {
            'admin': ('YOUR_ACCOUNT', "YOUR_ENCRYPTED_PASSWORD")
        }

    # 默认用户 admin / YOUR_PASSWORD（占位，实际密码经加密传入）
    return {
        'admin': ('admin', "YOUR_ENCRYPTED_PASSWORD"),
    }


@pytest.fixture(scope="session", autouse=True)
def login_users(api_login, users_info, exit_with_http_info):
    user_info = {}
    for username, password in users_info.items():
        logging.info(f"{'#' * 32}初始化用户{'#' * 32}")
        response = api_login(password[0], password[1])
        if response.status_code != 200:
            exit_with_http_info(f"用户{username}登陆失败", response)
        response_json = response.json()
        if response_json["resultCode"] != 200:
            exit_with_http_info(f"用户{username}登陆失败", response)
        user_info[username] = {
            'token': response_json['token'],
            'refresh_token': response_json['refreshedToken'],
            'user_id': response_json['data']['userInfo']['userId'],
            'detail': response_json['data']
        }

    return user_info
