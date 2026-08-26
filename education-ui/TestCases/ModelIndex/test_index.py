import allure
import pytest
from TestDatas.index_datas import nav_click_datas, menu_click_datas

@allure.feature("首页")
@pytest.mark.usefixtures('index_page')
class TestIndex:
    @pytest.mark.parametrize("data", nav_click_datas)
    def test_click_nav(self, data, index_page):
        with allure.step('点击导航栏跳转'):
            url = index_page.click_nav(data["nav_name"])
        with allure.step('校验当前url'):
            assert url == data["url"]

    @pytest.mark.parametrize("data", menu_click_datas)
    def test_click_menu(self, data, index_page):
        with allure.step('点击二级菜单跳转'):
            url = index_page.click_menu(data["nav_name"], data["menu_name"])
        with allure.step('校验当前url'):
            assert url == data["url"]

    # 根据时间筛选
    @pytest.mark.parametrize("data", time_filter_datas)
    def test_time_filter(self, data, index_page):
        with allure.step('时间筛选框输入时间'):
