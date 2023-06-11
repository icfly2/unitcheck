# -*- coding: utf-8 -*-

import pytest
from analyser import Analyser


def pytest_addoption(parser):
    group = parser.getgroup('unitcheck', 'Unit check plugin')
    group.addoption('--module', dest='module', help='Module location')


@pytest.fixture(scope='session', autouse=True)
def analyse(request):
    module = request.config.getoption('--module')
    collected_tests = request.config.option.collected_tests

    a = Analyser()
    a.module(module)
    for item in collected_tests:
        a.tests(item.nodeid)
    a.results()


def pytest_configure(config):
    config.addinivalue_line('markers', 'unitcheck: mark the test as a unit check.')


def pytest_collection_modifyitems(config, items):
    config.option.collected_tests = items
    for item in items:
        if 'unitcheck' in item.keywords:
            item.add_marker(pytest.mark.analyse)
