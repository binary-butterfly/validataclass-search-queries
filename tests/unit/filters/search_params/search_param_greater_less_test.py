"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

import pytest

from tests.helpers import assert_column_element
from validataclass_search_queries.filters import (
    SearchParamGreaterThan,
    SearchParamGreaterOrEqual,
    SearchParamLessThan,
    SearchParamLessOrEqual,
    SearchParamSince,
    SearchParamUntil,
)


@pytest.mark.parametrize(
    'search_param_cls, expected_operator',
    [
        (SearchParamGreaterThan, '>'),
        (SearchParamGreaterOrEqual, '>='),
        (SearchParamLessThan, '<'),
        (SearchParamLessOrEqual, '<='),

        # These are aliases for GreaterOrEqual and LessOrEqual
        (SearchParamSince, '>='),
        (SearchParamUntil, '<='),
    ]
)
def test_search_param_greater_less_etc(sqlalchemy_column, search_param_cls, expected_operator):
    """ Collective test for SearchParamGreaterThan, ...GreaterOrEqual, ...LessThan, ...LessOrEqual (and aliases). """
    search_filter = search_param_cls().sqlalchemy_filter(sqlalchemy_column, 42)
    assert_column_element(search_filter, f'unit_test_column {expected_operator} :unit_test_column_1', 42)
