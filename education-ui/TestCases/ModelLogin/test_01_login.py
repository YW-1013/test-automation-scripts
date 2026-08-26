
import allure
from TestDatas import login_datas as ld
from PageObjects.index_page import IndexPage
from PageObjects.login_page import LoginPage
import pytest

@allure.feature("登录功能")
@pytest.mark.usefixtures("access_web")
class TestLogin:

    # 成功登录
    @allure.title("登录成功")
    @pytest.mark.parametrize("data", ld.success_data)
    def test_login_success(self, access_web, data):
        with allure.step('登录账号'):
            access_web[1].login(data["user"], data["passwd"])
        with allure.step('校验用户名'):
            assert data["check"] == IndexPage(access_web[0]).get_login_username()

    # 用户不存在、密码错误
    @allure.title("用户不存在或密码错误")
    @pytest.mark.parametrize("data", ld.wrong_datas)
    def test_login_fail(self, access_web, data):
        with allure.step('登录账号'):
            access_web[1].login(data["user"], data["passwd"])
        with allure.step('校验报错内容'):
            assert LoginPage(access_web[0]).get_username_passwd_error() == data["check"]

    # 用户名为空
    @allure.title("用户名为空")
    @pytest.mark.parametrize("data", ld.no_user)
    def test_login_no_user(self, access_web, data):
        with allure.step('登录账号'):
            access_web[1].login(data["user"], data["passwd"])
        with allure.step('校验报错内容'):
            assert LoginPage(access_web[0]).get_username_null_error() == data["check"]

    # 密码为空
    @allure.title("密码为空")
    @pytest.mark.parametrize("data", ld.no_passwd)
    def test_login_no_passwd(self, access_web, data):
        with allure.step('登录账号'):
            access_web[1].login(data["user"], data["passwd"])
        with allure.step('校验报错内容'):
            assert LoginPage(access_web[0]).get_password_null_error() == data["check"]

    # 切换明密文
    @allure.title('密码输入框切换明密文')
    def test_change_password_type(self, access_web):
        with allure.step('点击切换为明文'):
            passwd_type = access_web[1].change_password_type()
        with allure.step('检查password_input type属性'):
            assert passwd_type == 'text'
        with allure.step('点击切换为密文'):
            passwd_type = access_web[1].change_password_type()
        with allure.step('检查password_input type属性'):
            assert passwd_type == 'password'


