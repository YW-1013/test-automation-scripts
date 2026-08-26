from PageLocators.basic_info_page_locators.org_info_page_locators import OrgInfoPageLocator as loc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class OrgInfoPage:
    def __init__(self, driver):
        self.driver = driver

    # 修改组织名称
    def modify_org_name(self, org_name):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.org_name_edit_button))
        self.driver.find_element(*loc.org_name_edit_button).click()
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.org_name_edit_title))
        self.driver.find_element(*loc.org_name_edit_input).send_keys(org_name)
        self.driver.find_element(*loc.org_name_edit_confirm_button).click()

    # 取消修改组织名称
    def cancel_modify_org_name(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.org_name_edit_button))
        self.driver.find_element(*loc.org_name_edit_button).click()
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.org_name_edit_title))
        self.driver.find_element(*loc.org_name_edit_cancel_button).click()

    # 清空组织名称
    def clear_org_name(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.org_name_edit_button))
        self.driver.find_element(*loc.org_name_edit_button).click()
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.org_name_edit_title))
        self.driver.find_element(*loc.org_name_edit_input_clear).click()