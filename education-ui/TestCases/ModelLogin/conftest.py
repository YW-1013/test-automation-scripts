import pytest
from selenium import webdriver
from PageObjects.login_page import LoginPage
from TestDatas import Comm_Datas as cd

driver = None
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.binary_location = 'C:/Users/Administrator.DESKTOP-C1S5G65/AppData/Local/Google/Chrome/Application/chrome.exe'

@pytest.fixture()
def access_web():
    global driver
    driver = webdriver.Chrome(options)
    driver.maximize_window()
    driver.get(cd.login_url)
    lg = LoginPage(driver)

    yield(driver, lg)

    driver.quit()