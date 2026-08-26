from addict import Dict
import pytest


@pytest.fixture(scope='session')
def context():
    """
        用于保存测试过程中生成的数据
    """
    return Dict({})