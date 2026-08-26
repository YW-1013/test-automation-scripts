from selenium.webdriver.common.by import By


class OrganizePageLocator:
    # 组织名称
    organize_name = (By.XPATH, '//label[text()="组织名称:"]/parent::div/following-sibling::div//span')
    # 编辑组织名称按钮
    edit_organize = (By.XPATH, '//label[text()="组织名称:"]/parent::div/following-sibling::div//button')
    # 修改组织名称弹窗标题
    edit_title = (By.XPATH, '//div[@class="arco-modal"]//div[@class="arco-modal-title arco-modal-title-align-center"]')
    # 组织名称输入框
    organize_input = (By.XPATH, '//div[@class="arco-modal"]//div[@class="arco-modal-body"]//input')
    # 清空按钮
    clear_button = (By.XPATH, '//span[@class="arco-icon-hover arco-input-icon-hover arco-input-clear-btn"]')
    # 确定按钮
    confirm_button = (By.XPATH, '//button[text()="确定"]')
    # 取消按钮
    cancel_button = (By.XPATH, '//button[text()="取消"]')