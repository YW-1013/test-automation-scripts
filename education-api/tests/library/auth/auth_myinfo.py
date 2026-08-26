import pytest

@pytest.fixture
def api_get_myinfo(req, option):
    def get(username):
        url = f"{option['api_auth']}/v2/myInfo"
        return req('get', username, url)

    return get
