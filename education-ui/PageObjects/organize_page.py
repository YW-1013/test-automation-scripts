import allure

from Common.explicit_wait import ExplicitWait
from PageLocators.organize_page_locators import OrganizePageLocator as loc
from PageLocators.common_locators import CommonLocator as com_loc

class OrganizePage:
    def __init__(self, driver):
        self.driver = driver

    # 修改组织名称
    def edit_organize_name(self, organize_name):
        # 点击修改按钮
        with allure.step('点击修改按钮'):
            edit_organize = ExplicitWait.wait_for_element_clickable(self.driver, loc.edit_organize)
            edit_organize.click()
        # 输入组织名称
        with allure.step('输入组织名称'):
            organize_input = ExplicitWait.wait_for_element_visible(self.driver, loc.organize_input)
            organize_input.send_keys(organize_name)
        # 点击确定
        with allure.step('点击确定'):
            confirm_button = ExplicitWait.wait_for_element_clickable(self.driver, loc.confirm_button)
            confirm_button.click()

    def get_organize_name(self):
        organize_name = ExplicitWait.wait_for_element_visible(self.driver, loc.organize_name)
        return organize_name.text

    def get_navigation_name(self):
        navigation_name = ExplicitWait.wait_for_element_visible(self.driver, com_loc.navigation_name)
        return navigation_name.text

