import pytest


@pytest.fixture(scope='module')
def test_fixture1():
    print('Run each test')
    return 1


def test_hello_world1(test_fixture1):
    print('function_fixture1')
    assert test_fixture1 == 1


def test_hello_world2(test_fixture1):
    print('function_fixture2')
    assert test_fixture1 == 1


@pytest.mark.skip
def test_hello_world3(test_fixture1):
    print('function_fixture3')
    assert test_fixture1 == 1

