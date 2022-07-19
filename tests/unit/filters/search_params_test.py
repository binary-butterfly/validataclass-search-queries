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
    SearchParamIsNone,
    SearchParamIsNotNone,
    SearchParamGreaterThan,
    SearchParamGreaterOrEqual,
    SearchParamLessThan,
    SearchParamLessOrEqual,
    SearchParamSince,
    SearchParamUntil,
)


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


@pytest.mark.parametrize(
    'input_value, expected_param',
    [
        ('', ''),
        ('banana', 'banana'),

        # Ensure special characters (SQL 'LIKE' syntax) are escaped properly
        ('foo%bar_baz', 'foo/%bar/_baz'),
        ('foo/bar\\baz', 'foo//bar\\baz'),
    ]
)
def test_search_param_contains(sqlalchemy_column, input_value, expected_param):
    """ Test the SearchParamContains search parameter. """
    search_filter = SearchParamContains().sqlalchemy_filter(sqlalchemy_column, input_value)
    assert_column_element(search_filter, "unit_test_column LIKE '%' || :unit_test_column_1 || '%' ESCAPE '/'", expected_param)


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
