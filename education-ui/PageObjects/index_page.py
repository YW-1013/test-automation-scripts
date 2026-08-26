import time
from Common.explicit_wait import ExplicitWait
from PageLocators.index_page_locators import IndexPageLocator as loc
from PageLocators.common_locators import CommonLocator as com_loc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from Common.explicit_wait import ExplicitWait

class IndexPage:

        def __init__(self, driver):
            self.driver = driver

        # 获取登录用户名
        def get_login_username(self):
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(loc.user_name))
            return self.driver.find_element(*loc.user_name).text

        # 搜索课程
        def search_course(self, course_title):
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(com_loc.course_name))
            self.driver.find_element(*com_loc.course_name).send_keys(course_title)
            self.driver.find_element(*com_loc.search_button).click()

        # 收藏课程
        def collect_course(self, course_title):
            self.search_course(course_title)
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, f'//text()="{course_title}"')))
            self.driver.find_element(*loc.collect_button).click()

        # 取消收藏课程
        def cancel_collect_course(self, course_title):
            self.search_course(course_title)
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, f'//text()="{course_title}"')))
            self.driver.find_element(*loc.cancel_collect_button).click()

        # 点击导航栏直接跳转
        def click_nav(self, nav_name):
            ExplicitWait.wait_for_element_clickable(self.driver, com_loc.get_nav_btn(nav_name)).click()
            time.sleep(2)
            return self.driver.current_url

        # 点击导航栏二级菜单跳转
        def click_menu(self, nav_name, menu_name):
            chains = ActionChains(self.driver)
            nav_ele = ExplicitWait.wait_for_element_visible(self.driver, com_loc.get_nav_btn(nav_name))
            chains.move_to_element(nav_ele).perform()
            ExplicitWait.wait_for_element_visible(self.driver, com_loc.get_nav_menu(menu_name)).click()
            time.sleep(2)
            return self.driver.current_url.split('?')[0]

        # 通过教师名称搜索
        def search_teacher(self, teacher_name):
            teacher_input = ExplicitWait.wait_for_element_visible(self.driver, com_loc.teacher_name)
            teacher_input.send_keys(teacher_name)
            ExplicitWait.wait_for_element_clickable(self.driver, com_loc.search_button)

        # 选择分页条数，返回items数目
        def get_page_item(self, page_option):
            ExplicitWait.wait_for_element_clickable(self.driver, com_loc.expand_page_options).click()
            ExplicitWait.wait_for_element_clickable(self.driver, com_loc.get_pagination(page_option)).click()
            time.sleep(2)
            return len(self.driver.find_elements(com_loc.all_course))

