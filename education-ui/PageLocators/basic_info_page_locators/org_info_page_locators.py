from selenium.webdriver.common.by import By

class OrgInfoPageLocator:

    # 组织名称
    org_name = (By.XPATH, '//label[text()="组织名称:"]/../following-sibling::div//span')
    # 组织名称修改按钮
    org_name_edit_button = (By.XPATH, '//label[text()="组织名称:"]/../following-sibling::div//button')
    # 组织名称修改标题
    org_name_edit_title = (By.XPATH, '//div[@class="arco-modal-title arco-modal-title-align-center"]')
    # 组织名称修改输入框
    org_name_edit_input = (By.XPATH, '//div[@class="arco-modal"]//input')
    # 组织名称输入框清空按钮
    org_name_edit_input_clear = (By.XPATH, '//div[@class="arco-modal"]//span[@class="arco-icon-hover arco-input-icon-'
                                           'hover arco-input-clear-btn"]')
    # 组织名称修改确定按钮
    org_name_edit_confirm_button = (By.XPATH, '//div[@class="arco-modal-footer"]//button[2]')
    # 组织名称修改取消按钮
    org_name_edit_cancel_button = (By.XPATH, '//div[@class="arco-modal-footer"]//button[1]')
    # 重新上传组织logo
    org_logo_upload_button = (By.XPATH, '//label[text()="组织logo:"]/../following-sibling::div//button')
    # 组织logo提示
    org_logo_tip = (By.XPATH, '//div[@class="tips"]')

    # 组织ID
    org_id = (By.XPATH, '//label[text()="组织ID:"]/../following-sibling::div//span')

    # 登录链接
    login_link = (By.XPATH, '//label[text()="登录链接:"]/../following-sibling::div//span')
    # 登录链接复制按钮
    login_link_copy_button = (By.XPATH, '//label[text()="登录链接:"]/../following-sibling::div//button')
