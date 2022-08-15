"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from tests.helpers import assert_column_element
from validataclass_search_queries.filters import SearchParamEquals


def test_search_param_equals(sqlalchemy_column):
    """ Test the SearchParamEquals search parameter. """
    search_filter = SearchParamEquals().sqlalchemy_filter(sqlalchemy_column, 42)
    assert_column_element(search_filter, 'unit_test_column = :unit_test_column_1', 42)
