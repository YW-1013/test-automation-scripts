import logging

from pytest_bdd import when, parsers


@when(parsers.parse('用户 {user} 登录, {update_key} 是 {update_value}'))
def when_login(user, update_key, update_value, send_request, default_body_auth_login,
               tramsform_auth_login):
    form = default_body_auth_login()
    for key, value in zip(
        update_key.split(','),
        update_value.split(',')
    ):
        form = tramsform_auth_login(form, key, value)

    logging.info(form)
    # response = send_request()

