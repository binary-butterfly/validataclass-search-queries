"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest

from tests.helpers import assert_column_element
from validataclass_search_queries.filters import (
    SearchParamBoolean,
    SearchParamIsNone,
    SearchParamIsNotNone,
    SearchParamTernary,
)


@pytest.mark.parametrize(
    'input_value, expected_str',
    [
        (None, 'false'),
        (True, 'true'),
        (False, 'false'),
        (1, 'true'),
        (0, 'false'),
    ]
)
def test_search_param_boolean(sqlalchemy_column, input_value, expected_str):
    """ Test the SearchParamBoolean search parameter. """
    search_filter = SearchParamBoolean().sqlalchemy_filter(sqlalchemy_column, input_value)
    assert_column_element(search_filter, f'unit_test_column IS {expected_str}')


def test_search_param_is_none(sqlalchemy_column):
    """ Test the SearchParamIsNone search parameter. """
    param = SearchParamIsNone()
    assert_column_element(param.sqlalchemy_filter(sqlalchemy_column, True), 'unit_test_column IS NULL')
    assert_column_element(param.sqlalchemy_filter(sqlalchemy_column, False), 'unit_test_column IS NOT NULL')


def test_search_param_is_not_none(sqlalchemy_column):
    """ Test the SearchParamIsNotNone search parameter. """
    param = SearchParamIsNotNone()
    assert_column_element(param.sqlalchemy_filter(sqlalchemy_column, True), 'unit_test_column IS NOT NULL')
    assert_column_element(param.sqlalchemy_filter(sqlalchemy_column, False), 'unit_test_column IS NULL')


def test_search_param_ternary(sqlalchemy_column):
    """ Test the SearchParamTernary search parameter. """
    param = SearchParamTernary('yes', 'no')
    assert_column_element(param.sqlalchemy_filter(sqlalchemy_column, True), 'unit_test_column = :unit_test_column_1', 'yes')
    assert_column_element(param.sqlalchemy_filter(sqlalchemy_column, False), 'unit_test_column = :unit_test_column_1', 'no')
