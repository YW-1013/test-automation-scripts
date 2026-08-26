import pytest
from TestDatas.Comm_Datas import index_url
from PageObjects.index_page import IndexPage

@pytest.fixture()
@pytest.mark.usefixtures('access_web')
def index_page(access_web):
    access_web.get(index_url)
    index_page = IndexPage(access_web)
    yield index_page