from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PageLocators.login_page_locators import LoginPageLocator as loc
from Common .explicit_wait import ExplicitWait

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    # 登录操作
    def login(self, username, password):
        # 输入用户名
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.username_input))
        self.driver.find_element(*loc.username_input).send_keys(username)
        # 输入密码
        self.driver.find_element(*loc.password_input).send_keys(password)
        # 点击登录按钮
        self.driver.find_element(*loc.login_button).click()

    # 获取用户不存在、密码错误提示信息
    def get_username_passwd_error(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.username_not_exist_error))
        return self.driver.find_element(*loc.username_not_exist_error).text

    # 获取用户名为空提示信息
    def get_username_null_error(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.username_null_error))
        return self.driver.find_element(*loc.username_null_error).text

    # 获取密码为空提示信息
    def get_password_null_error(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.password_null_error))
        return self.driver.find_element(*loc.password_null_error).text

    # 点击变更明密文输入，返回密码输入框type值
    def change_password_type(self):
        change_type_btn = ExplicitWait.wait_for_element_visible(self.driver, loc.input_suffix_btn)
        change_type_btn.click()
        return ExplicitWait.wait_for_element_visible(self.driver, loc.password_input).get_attribute('type')

