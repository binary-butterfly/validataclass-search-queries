"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH
All rights reserved.
"""

from typing import Any

import pytest
import sqlalchemy
from sqlalchemy.sql import ColumnElement

from validataclass_search_queries.filters import (
    SearchParamEquals,
    SearchParamContains,
    SearchParamStartsWith,
    SearchParamEndsWith,
    SearchParamBoolean,
    SearchParamIsNone,
    SearchParamIsNotNone,
    SearchParamTernary,
    SearchParamGreaterThan,
    SearchParamGreaterOrEqual,
    SearchParamLessThan,
    SearchParamLessOrEqual,
    SearchParamSince,
    SearchParamUntil,
)

# Test data for SearchParamContains, SearchParamStartsWidth, SearchParamEndsWidth (substring matching search filters)
# (Parameters: input_value, expected_param)
test_data_substring_matches = [
    # Simple string
    ('banana', 'banana'),

    # Ensure special characters (SQL 'LIKE' syntax) are escaped properly
    ('foo%bar_baz', 'foo/%bar/_baz'),
    ('foo/bar\\baz', 'foo//bar\\baz'),
]


def assert_column_element(element: Any, expected_string: str, *expected_params) -> None:
    """ Helper function to check the SQL and bound parameters of a generated ColumnElement. """
    assert isinstance(element, ColumnElement)
    compiled_expr = element.compile()
    assert str(compiled_expr) == expected_string
    assert list(compiled_expr.params.values()) == list(expected_params)


@pytest.fixture
def sqlalchemy_column():
    return sqlalchemy.column('unit_test_column')


def test_search_param_equals(sqlalchemy_column):
    """ Test the SearchParamEquals search parameter. """
    search_filter = SearchParamEquals().sqlalchemy_filter(sqlalchemy_column, 42)
    assert_column_element(search_filter, 'unit_test_column = :unit_test_column_1', 42)


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
