"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from tests.helpers import assert_column_element
from validataclass_search_queries.filters import SearchParamContains, SearchParamStartsWith, SearchParamEndsWith

# Test data for SearchParamContains, SearchParamStartsWidth, SearchParamEndsWidth (substring matching search filters)
# (Parameters: input_value, expected_param)
test_data_substring_matches = [
    # Simple string
    ('banana', 'banana'),

    # Ensure special characters (SQL 'LIKE' syntax) are escaped properly
    ('foo%bar_baz', 'foo/%bar/_baz'),
    ('foo/bar\\baz', 'foo//bar\\baz'),
]


@pytest.mark.parametrize('input_value, expected_param', test_data_substring_matches)
def test_search_param_contains(sqlalchemy_column, input_value, expected_param):
    """ Test the SearchParamContains search parameter. """
    search_filter = SearchParamContains().sqlalchemy_filter(sqlalchemy_column, input_value)
    assert_column_element(search_filter, "unit_test_column LIKE '%' || :unit_test_column_1 || '%' ESCAPE '/'", expected_param)


@pytest.mark.parametrize('input_value, expected_param', test_data_substring_matches)
def test_search_param_starts_with(sqlalchemy_column, input_value, expected_param):
    """ Test the SearchParamStartsWith search parameter. """
    search_filter = SearchParamStartsWith().sqlalchemy_filter(sqlalchemy_column, input_value)
    assert_column_element(search_filter, "unit_test_column LIKE :unit_test_column_1 || '%' ESCAPE '/'", expected_param)


@pytest.mark.parametrize('input_value, expected_param', test_data_substring_matches)
def test_search_param_ends_with(sqlalchemy_column, input_value, expected_param):
    """ Test the SearchParamEndsWith search parameter. """
    search_filter = SearchParamEndsWith().sqlalchemy_filter(sqlalchemy_column, input_value)
    assert_column_element(search_filter, "unit_test_column LIKE '%' || :unit_test_column_1 ESCAPE '/'", expected_param)


@pytest.mark.parametrize('search_param_cls', [SearchParamContains, SearchParamStartsWith, SearchParamEndsWith])
def test_search_param_substring_matching_shortcircuit(sqlalchemy_column, search_param_cls):
    """ Test that SearchParamContains, SearchParamStartsWith and SearchParamEndsWith short-circuit if the value is empty. """
    assert search_param_cls().sqlalchemy_filter(sqlalchemy_column, '') is sqlalchemy_column
