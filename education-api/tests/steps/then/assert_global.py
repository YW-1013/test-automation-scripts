"""适用于全局的断言,例如状态码."""
from pytest_bdd import then, parsers
from tests.steps.then.status_code_assert import status_code_operation_success


@then(parsers.parse("{opration} 操作成功"))
def then_assert_status_code(opration, context):
    expect_status_code = status_code_operation_success.get(opration)
    status_code = context["http_response"].status_code
    assert status_code == expect_status_code, f"期望的响应状态码是：{expect_status_code}, 实际是: {status_code}"
    # 增加对通用响应体校验
    response_json = context["http_response"].json()
    assert "resultCode" in response_json and response_json["resultCode"] == 200
    assert "retCode" in response_json and response_json["retCode"] == 0
