import logging
import pytest


@pytest.fixture()
def  tear_down_feature_测试(option):
    logging.info("测试后置清理")
    logging.info(option)