from pytest_bdd import then, parsers


@then(parsers.parse("{user} 个人信息数据正确"))
def then_assert_myinfo(user, ctx_auth_get_myinfo, login_users):
    login_info = login_users[user]
    info = ctx_auth_get_myinfo(user).json()
    assert "msg" in info and info["msg"] == "响应成功"
    assert "message" in info and info["message"] == "响应成功"
    assert info['data']['userId'] == login_info['user_id']
    assert info['data']["tenantId"] == login_info['detail']["userInfo"]["tenantId"]
