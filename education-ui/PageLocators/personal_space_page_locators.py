from selenium.webdriver.common.by import By

class SpacePageLocator:

    # 我的收藏
    my_collect = (By.XPATH, '//span[text()="我的收藏"]')
    # 我录制的
    my_record = (By.XPATH, '//span[text()="我录制的"]')
    # 我发布的
    my_publish = (By.XPATH, '//span[text()="我发布的"]')
