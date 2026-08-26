"""
    用于设置存储到context的方法, 方便后续测试数据获取，以及避免直接对context设置数据导致数据错乱.
"""
import pytest

@pytest.fixture
def ctx_auth_set_myinfo(context):
    def ctx(user, data):
        if "myinfo" not in context:
            context["myinfo"] = {}
        context["myinfo"][user] = data

    return ctx


@pytest.fixture
def ctx_auth_get_myinfo(context):
    def ctx(user):
        return context["myinfo"][user]

    return ctx