"""
定义前置和后置执行流程.
"""
import logging
from _pytest.fixtures import FixtureLookupError


def find_fixture_by_name(request, name):
    """查找fixture是否存在."""
    keys = list(request._fixturemanager._arg2fixturedefs.keys())
    if name in keys:
        return True
    else:
        return False


def _execute_fixture(request, prefix, name, execute_type):
    """
    通过前置+名称，查找具体的fixture，若存在则执行，以满足前置置操作处理
    :param request: pytest request 对象
    :param prefix: 需要执行的fixture 前缀
    :param name: 需要执行的fixture 后缀
    :return:
    """
    fixture_name = f'{prefix}{name}'
    try:
        if find_fixture_by_name(request, fixture_name):
            logging.info(f"存在{execute_type}: {fixture_name}, 执行操作!")
            request.getfixturevalue(fixture_name)
            logging.info(f"{fixture_name}, 执行成功!")
    except FixtureLookupError as e:
        logging.warning(e.msg)


def execute_setup(request, scenario_name, feature_name):
    """
    执行前置操作
    """
    # 先执行单个场景(scenario)的前置操作
    _execute_fixture(request, 'before_scenario_', scenario_name, execute_type="scenario前置操作")
    # 再执行整个功能(feature)的前置操作
    _execute_fixture(request, 'before_feature_', feature_name, execute_type="feature前置操作")


def execute_teardown(request, scenario_name, feature_name):
    """
    执行前置操作
    """
    # 先执行单个场景(scenario)的后置操作
    _execute_fixture(request, 'tear_down_scenario_', scenario_name, execute_type="scenario后置操作")
    # 再执行整个功能(feature)的后置操作
    _execute_fixture(request, 'tear_down_feature_', feature_name, execute_type="feature后置操作")
