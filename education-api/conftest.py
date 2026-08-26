import logging
import os
import re
import pytest
import env
from py.xml import html
from tests.before_and_teardown import execute_setup, execute_teardown

def pytest_html_report_title(report):
    """hook: 定义报告的标题"""
    report.title = "教育平台测试报告"


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    """hook: 解决html报告中文乱码问题，原因是html报告编写进行了转码，这里重新赋值"""
    cells[1] = html.td(report.nodeid, class_="col-name")


def pytest_sessionfinish(session, exitstatus):
    """hook: 测试执行结束时执行的操作"""
    pass


def pytest_bdd_before_scenario(request, feature, scenario):
    """
    hook: 场景测试前置执行步骤.
    """
    scenario_name = scenario.name
    result = re.match('^[\u4E00-\u9FA5A-Za-z0-9_]+$', scenario_name)
    if result is None:
        # 场景名只能包含中英文和下划线，其他字符容易被pytest替换，导致报错时搜索不到场景名
        raise Exception(f'场景名只能包含中英文、数字和下划线, scenario.name: {scenario_name}')
    execute_setup(request, scenario.name, feature.name)


def pytest_bdd_after_scenario(request, feature, scenario):
    """
    hook: 场景测试后置执行步骤.
    """
    execute_teardown(request, scenario.name, feature.name)


def pytest_addoption(parser):
    """设置接收的参数."""
    env.pytest_options_parser(parser)


@pytest.fixture(scope="session",autouse=True)
def option(request):
    """设置pytest接收的命令行参数，并放到option中."""
    return env.pytest_get_options(request)


def find_plugin_paths(file_dir, exclude_plugin_paths=None):
    """
    查找指定路径下所有plugin的方法，方便直接定义了fixture能直接使用
    :param file_dir: 查找的文件目录
    :param exclude_plugin_paths: 不需要导入的目录，例如启动函数、前后置函数
    :return:
    """
    if exclude_plugin_paths is None:
        exclude_plugin_paths = []

    plugin_names = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            file_suffix = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)

            if file_suffix == '.py' and file != '__init__.py':
                pkg_format_path = file_path.split('.py')[0].replace(os.sep, '.')
                if pkg_format_path in exclude_plugin_paths:
                    continue
                plugin_names.append(pkg_format_path)
    return plugin_names


pytest_plugins = find_plugin_paths('tests',  ['tests.test_boot',])
