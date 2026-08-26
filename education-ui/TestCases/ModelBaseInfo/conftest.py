import pytest
from TestDatas.Comm_Datas import organize_info_url
from PageObjects.organize_page import OrganizePage

@pytest.fixture()
@pytest.mark.usefixtures('access_web')
def organize_info_page(access_web):
    access_web.get(organize_info_url)
    organize_page = OrganizePage(access_web)
    yield organize_page