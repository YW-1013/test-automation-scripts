import sys

import pytest


@pytest.fixture(scope="session")
def api_login(option, send_request):
    def request(username, password, code='default', auth_type='TENANT_USER', client_id="EDUCATION_CLOUD"):
        url = f"{option['api_auth']}/user/login"
        if code == "default":
            code = option['code']
        payload = {
            "authType": auth_type,
            "clientId": client_id,
            "tenantCode": code,
            "username": username,
            "password": password
        }
        return send_request("POST", url, body=payload)

    return request
