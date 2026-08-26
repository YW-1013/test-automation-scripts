from pytest_bdd import when, parsers


@when(parsers.parse("用户 {username} 查看直播列表"))
def when_get_live_list(username, api_get_live_list):
    response = api_get_live_list(username)
    pass


@when(parsers.parse("用户 {username} 查看我的直播"))
def when_get_live_list(username, api_get_mylive_list):
    response = api_get_mylive_list(username)
    pass