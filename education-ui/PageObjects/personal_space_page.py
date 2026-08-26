from PageLocators.personal_space_page_locators import SpacePageLocator as loc
from PageLocators.common_locators import CommonLocator as com_loc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class PersonalSpacePage:
    def __init__(self, driver):
        self.driver = driver

    # 点击我的收藏
    def click_my_collect(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.my_collect))
        self.driver.find_element(*loc.my_collect).click()

    # 搜索课程
    def search_course(self, course_title):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(com_loc.course_name))
        self.driver.find_element(*com_loc.course_name).send_keys(course_title)
        self.driver.find_element(*com_loc.search_button).click()

