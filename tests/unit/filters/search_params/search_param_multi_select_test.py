"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from tests.helpers import assert_column_element, UnitTestEnum
from validataclass_search_queries.filters import SearchParamMultiSelect


@pytest.mark.parametrize(
    'input_value_list',
    [
        [],
        [42],
        [1, 2, 3],
        ['foo'],
        ['a', 'c', 'b'],
        [UnitTestEnum.FOO, UnitTestEnum.BAZ],
    ]
)
def test_search_param_multi_select(sqlalchemy_column, input_value_list):
    """ Test the SearchParamMultiSelect search parameter. """
    search_filter = SearchParamMultiSelect().sqlalchemy_filter(sqlalchemy_column, input_value_list)
    assert_column_element(search_filter, 'unit_test_column IN (__[POSTCOMPILE_unit_test_column_1])', input_value_list)


@pytest.mark.parametrize(
    'input_value',
    [
        42,
        'foo',
        UnitTestEnum.FOO,
    ]
)
def test_search_param_multi_select_with_scalars(sqlalchemy_column, input_value):
    """ Test the SearchParamMultiSelect search parameter with a single value instead of a list of values. """
    search_filter = SearchParamMultiSelect().sqlalchemy_filter(sqlalchemy_column, input_value)
    assert_column_element(search_filter, 'unit_test_column IN (__[POSTCOMPILE_unit_test_column_1])', [input_value])
