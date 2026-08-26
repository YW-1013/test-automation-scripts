from selenium.webdriver.common.by import By

class LoginPageLocator:

    # 用户名输入框
    username_input = (By.XPATH, '//input[@placeholder="请输入用户名"]')
    # 密码输入框
    password_input = (By.XPATH, '//input[@placeholder="请输入密码"]')
    # 登录按钮
    login_button = (By.XPATH, '//button[text()="登录"]')
    # 用户名不存在错误提示
    username_not_exist_error = (By.XPATH, '//div[@class="login-form-error-msg"]')
    # 用户名为空错误提示
    username_null_error = (By.XPATH, '//form//div[@id="username"]/div[@role="alert"]')
    # 密码为空错误提示
    password_null_error = (By.XPATH, '//form//div[@id="password"]/div[@role="alert"]')
    # 明文密文切换按钮
    input_suffix_btn = (By.XPATH, '//span[@class="arco-input-suffix"]')