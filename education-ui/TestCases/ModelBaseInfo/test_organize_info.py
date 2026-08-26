import pytest
from TestDatas import organize_info_datas as org_info_data
import allure

@allure.feature("组织信息")
@pytest.mark.usefixtures("access_web")
@pytest.mark.usefixtures('organize_info_page')
class TestOrganize:
    @pytest.mark.parametrize("data", org_info_data.success_datas)
    def test_edit_organize_name(self, data, organize_info_page):
        with allure.step('修改组织名称'):
            organize_info_page.edit_organize_name(data)
        with allure.step('校验导航栏组织名称'):
            organize_info_page.get_organize_name()

