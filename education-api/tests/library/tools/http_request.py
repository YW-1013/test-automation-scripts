"""http请求统一入口."""
import json
from urllib import parse
import pytest
import requests
import logging
import simplejson as simplejson
from tests.library.tools.untils import trace_id


@pytest.fixture(scope="session")
def send_request(context):
    """直接发送http请求."""
    def send(method, url, headers=None, body=None, params=None):
        response = _do_request(http_method=method, url=url, custom_header=headers, body=body, params=params)
        context["http_response"] = response
        return response

    return send


@pytest.fixture(scope='session')
def req(login_users, context):
    """直接适配用户token发送请求."""
    def request_with_token(http_method, username, url, body=None, headers={}, params=None):
        token = login_users[username].get('token')
        headers.update({
            'Authorization': token
        })
        response = _do_request(url, http_method, body, headers, params)
        context["http_response"] = response
        return response

    return request_with_token


def _do_request(url, http_method, body, custom_header=None, params=None):
    header = {
        "Content-Type": "application/json",
        'x-apm-traceid': trace_id(),
    }
    if custom_header is not None and custom_header:
        header.update(custom_header)
    if header['Content-Type'] == 'application/x-www-form-urlencoded':
        response = requests.request(
            method=http_method,
            url=url,
            headers=header,
            data=parse.urlencode(body),
            params=params,
            verify=False
        )
    else:
        response = requests.request(
            method=http_method,
            url=url,
            headers=header,
            json=body,
            params=params,
            verify=False
        )
    log_http_info(response)
    return response


@pytest.fixture(scope="session")
def exit_with_http_info():
    """直接退出，并打印请求信息, 不执行后续流程."""
    def out_put(msg, response):
        response_msg = log_http_info(response)
        pytest.exit(f"{msg}\n{response_msg}")

    return out_put


def log_http_info(response):
    request = response.request
    request_body = request.body
    try:
        request_body = json.loads(request_body.decode('utf-8'))
    except:
        pass

    response_body = response.text
    try:
        response_body=json.loads(response_body)
    except:
        pass

    msg = "" +\
        f'{request.method} {request.url}\n' +\
        f'===> request  header: {request.headers}\n' +\
        f'===> request    body: {simplejson.dumps(request_body, indent=4, ensure_ascii=False)}\n' +\
        '################\n' +\
        f'<=== response   code: {response.status_code}\n' +\
        f'<=== response   time: {response.elapsed.total_seconds()}\n' +\
        f'<=== response header: {response.headers}\n' +\
        f'<=== response   body: {simplejson.dumps(response_body, indent=4, ensure_ascii=False)}\n'


    logging.info(msg)
    return msg