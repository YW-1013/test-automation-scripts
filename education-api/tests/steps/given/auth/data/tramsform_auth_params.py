"""auth请求参数转换."""
import pytest


@pytest.fixture
def update_key():
    return None


@pytest.fixture
def update_value():
    return None


@pytest.fixture
def default_body_auth_login(option):
    """默认的请求body."""
    def get():
        return {
            "authType": "TENANT_USER",
            "clientId": "EDUCATION_CLOUD",
            "tenantCode": option.get('code'),
            "username": "",
            "password": ""
        }

    return get


@pytest.fixture
def tramsform_auth_login():
    def tramsform(form, key, value):
        return form

    return tramsform