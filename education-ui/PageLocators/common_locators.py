from selenium.webdriver.common.by import By

class CommonLocator:

    # 导航栏组织名称
    navigation_name = (By.XPATH, '//div[@class="arco-space-item"]/h5')
    # 导航栏按钮
    @staticmethod
    def get_nav_btn(nav_name):
        return (By.XPATH, f'//div[@class="navbar"]//span[text()="{nav_name}"]')

    # 二级菜单
    @staticmethod
    def get_nav_menu(menu_name):
        return (By.XPATH, f'//div[@class="arco-trigger-menu-item" and text()="{menu_name}"]')

    # 开始日期
    start_date = (By.XPATH, '//input[@placeholder="开始日期"]')
    # 结束日期
    end_date = (By.XPATH, '//input[@placeholder="结束日期"]')
    # 教室名称
    room_name = (By.XPATH, '//input[@placeholder="请输入教室名称"]')
    # 课程名称
    course_name = (By.XPATH, '//input[@placeholder="请输入课程名称"]')
    # 视频名称
    video_name = (By.XPATH, '//input[@placeholder="请输入视频名称"]')
    # 清空按钮
    clear_button = (By.XPATH, '//span[@class="arco-icon-hover arco-input-icon-hover arco-input-clear-btn"]')
    # 教师名称
    teacher_name = (By.XPATH, '//input[@placeholder="请输入教师名称"]')
    # 搜索按钮
    search_button = (By.XPATH, '//button[text()=" 搜索 "]')

    # 页码
    @staticmethod
    def get_page_button(page):
        return (By.XPATH, f'//ul[@class="arco-pagination-list"]/li[text()]={page}')
    # 展开分页选项
    expand_page_options = (By.XPATH, '//span[@class="arco-pagination-options"]')
    # 分页按钮
    @staticmethod
    def get_pagination(page_num):
        page_list = ['10 条/页', '20 条/页', '50 条/页', '100 条/页']
        return (By.XPATH, f'//span[text()="{page_list[page_num-1]}"]')

    # 取消删除
    cancel_delete = (By.XPATH, '//button[text()="取消"]')
    # 确认删除
    confirm_delete = (By.XPATH, '//button[text()="确定"]')

    all_course = (By.XPATH, '//div[@class="item"]')

    # 对应课程的编辑按钮
    @staticmethod
    def get_edit_button(course_title):
        return (By.XPATH, f'//span[text()="{course_title}"]/ancestor::tr//span[text()="编辑"]')

    # 对应课程删除按钮
    @staticmethod
    def get_delete_button(course_title):
        return (By.XPATH, f'//span[text()="{course_title}"]/ancestor::tr//span[text()="删除"]')

    # 对应课程视频播放按钮
    @staticmethod
    def course_title_button(course_title):
        return (By.XPATH, f'//span[text()="{course_title}"]/')

    # 对应课程的教师名称
    @staticmethod
    def get_teacher_name(course_title):
        return (By.XPATH, f'//div[text()="{course_title}"]/ancestor::div[@class="item"]/descendant::span[1]')

    # 对应课程的收藏/取消收藏按钮
    @staticmethod
    def get_collect_button(course_title):
        return (By.XPATH, f'//div[text()="{course_title}"]/ancestor::div[@class="item"]/descendant::span[2]')

