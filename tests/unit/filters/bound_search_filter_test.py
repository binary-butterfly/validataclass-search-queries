"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import sqlalchemy

from validataclass_search_queries.filters import BoundSearchFilter, SearchParamEquals


def test_bound_search_filter_column_name():
    """ Test column_name property of BoundSearchFilter, both with a named SearchParam and an unnamed one. """
    bound_filter1 = BoundSearchFilter('unit_test_param', SearchParamEquals(), 42)
    assert bound_filter1.column_name == 'unit_test_param'

    bound_filter2 = BoundSearchFilter('unit_test_param', SearchParamEquals('banana'), 42)
    assert bound_filter2.column_name == 'banana'


def test_bound_search_filter_sqlalchemy_filter():
    """ Test that BoundSearchFilter.get_sqlalchemy_filter() returns the correct filter expression. """
    bound_filter = BoundSearchFilter('unit_test_param', SearchParamEquals(), 42)
    filter_expr = bound_filter.get_sqlalchemy_filter(sqlalchemy.column('unit_test_column'))

    assert str(filter_expr) == 'unit_test_column = :unit_test_column_1'
    assert filter_expr.right.value == 42
