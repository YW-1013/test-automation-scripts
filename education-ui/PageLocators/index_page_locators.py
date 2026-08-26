from selenium.webdriver.common.by import By

class IndexPageLocator:

    # 组织名称
    org_name = (By.XPATH, '//div[@class="arco-space-item"]/h5')
    # 组织logo
    org_logo = (By.XPATH, '//div[@class="arco-space-item"]/div')
    # 用户名
    user_name = (By.XPATH, '//ul[@class="right-side"]/li/div/span[1]')

    # 收藏按钮
    collect_button = (By.XPATH, '//span[text()="收藏"]')
    # 取消收藏按钮
    cancel_collect_button = (By.XPATH, '//span[text()="取消收藏"]')




