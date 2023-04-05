import pytest


@pytest.fixture()
def test_fixture1():
    print('Run each test')
    return 1


def test_hello_world(test_fixture1):
    print('function_fixture1')
    assert test_fixture1 == 1
