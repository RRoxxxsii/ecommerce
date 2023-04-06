import pytest


def test_store_category_string(product_category):
    assert product_category.__str__() == 'django'


