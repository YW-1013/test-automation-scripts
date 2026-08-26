import pytest

@pytest.fixture
def api_get_live_list(req, option):
    """查询直播列表"""
    def get(username, body={}):
        url = f"{option['api_edu']}/v1/edu/live/list"
        return req('post', username, url, body=body)

    return get


@pytest.fixture
def api_get_mylive_list(req, option):
    """查询我的直播列表"""
    def get(username, body={}):
        url = f"{option['api_edu']}/v1/edu/live/myLive"
        return req('post', username, url, body=body)

    return get


@pytest.fixture
def api_create_live(req, option):
    """创建直播."""
    def post(username, body):
        url = f"{option['api_edu']}/v1/edu/live"
        return req('post', username, url, body=body)

    return post


@pytest.fixture
def api_update_live(req, option):
    """修改直播."""
    def put(username, body):
        url = f"{option['api_edu']}/v1/edu/live"
        return req('put', username, url, body=body)

    return put


@pytest.fixture
def api_delete_live(req, option):
    """删除直播."""
    def delete(username, live_id):
        url = f"{option['api_edu']}/v1/edu/live/{live_id}"
        return req('delete', username, url)

    return delete


@pytest.fixture
def api_cancel_live(req, option):
    """取消直播."""
    def get(username, live_id):
        url = f"{option['api_edu']}/v1/edu/live/cancel"
        return req('get', username, url, params={'id': live_id})

    return get


@pytest.fixture
def api_terminate_live(req, option):
    """结束直播."""
    def get(username, live_id):
        url = f"{option['api_edu']}/v1/edu/live/terminate"
        return req('get', username, url, params={'id': live_id})

    return get


@pytest.fixture
def api_get_live_detail(req, option):
    """查看直播详情."""
    def get(username, params={}):
        url = f"{option['api_edu']}/v1/edu/live/detail"
        return req('get', username, url, params=params)

    return get


@pytest.fixture
def api_get_live_status(req, option):
    """查看直播状态."""
    def get(username, params={}):
        url = f"{option['api_edu']}/v1/edu/live/status"
        return req('get', username, url, params=params)

    return get


@pytest.fixture
def api_create_live_stream(req, option):
    """创建直播流."""
    def get(username, body, params={}):
        url = f"{option['api_edu']}/v1/live/stream/create"
        return req('post', username, url, params=params, body=body)

    return get


@pytest.fixture
def api_get_live_stream(req, option):
    """查询直播流."""
    def get(username, body, params={}):
        url = f"{option['api_edu']}/v1/edu/live/stream"
        return req('post', username, url, params=params, body=body)

    return get


@pytest.fixture
def api_get_live_stream(req, option):
    """直播心跳请求."""
    def get(username, params={}):
        url = f"{option['api_edu']}/v1/edu/live/heart"
        return req('get', username, url, params=params)

    return get


@pytest.fixture
def api_manage_live_list(req, option):
    """管理直播列表."""
    def get(username, body):
        url = f"{option['api_edu']}/v1/edu/live/manage/list"
        return req('post', username, url, body=body)

    return get



@pytest.fixture
def api_switch_live(req, option):
    """修改直播录播开关."""
    def get(username, params):
        url = f"{option['api_edu']}/v1/edu/live/recordSwitch"
        return req('get', username, url, params=params)

    return get
