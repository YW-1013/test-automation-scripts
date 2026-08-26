from selenium.webdriver.common.by import By

class AreaManagePageLocator:

    # 新增教室按钮
    add_classroom_button = (By.XPATH, '//button[text()=" 新增教室 "]')
    # 导出按钮
    export_button = (By.XPATH, '//button[text()=" 导出 "]')
    # 对应教室的所属区域
    @staticmethod
    def get_area_name(room_name):
        return (By.XPATH, f'//span[text()="{room_name}"]/ancestor::tr/td[1]/span')
    # 对应教室的编辑按钮
    @staticmethod
    def get_edit_button(room_name):
        return (By.XPATH, f'//span[text()="{room_name}"]/ancestor::tr//button[text()=" 编辑 "]')
    # 对应教室的删除按钮
    @staticmethod
    def get_delete_button(room_name):
        return (By.XPATH, f'//span[text()="{room_name}"]/ancestor::tr//button[text()=" 删除 "]')
    # 对应教室的关联设备
    @staticmethod
    def get_device_button(room_name):
        return (By.XPATH, f'//span[text()="{room_name}"]/ancestor::tr//span[@class="active-color"]')

    # 新增一行
    add_button = (By.XPATH, '//button/span[text()=" 新建教室 “]')

    # 复制上一行
    copy_button = (By.XPATH, '//button/span[text()="" 复制上一行 ]')