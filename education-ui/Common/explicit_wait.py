from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ExplicitWait:
    @staticmethod
    def wait_for_element_clickable(driver, element):
        try:
            element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(element))
            return element
        except Exception as e:
            raise e

    @staticmethod
    def wait_for_element_visible(driver, element):
        try:
            element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(element))
            return element
        except Exception as e:
            raise e

