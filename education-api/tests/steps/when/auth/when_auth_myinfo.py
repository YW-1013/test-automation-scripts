from pytest_bdd import parsers, when


@when(parsers.parse("用户 {user} 查询个人信息"))
def when_get_myinfo(user, api_get_myinfo, ctx_auth_set_myinfo):
    response = api_get_myinfo(user)
    ctx_auth_set_myinfo(user, response)
