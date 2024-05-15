"""
validataclass-search-queries
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from sqlalchemy.sql import ColumnElement

from .base_search_param import SearchParam

__all__ = [
    'SearchParamGreaterThan',
    'SearchParamGreaterOrEqual',
    'SearchParamLessThan',
    'SearchParamLessOrEqual',
    'SearchParamSince',
    'SearchParamUntil',
]


class SearchParamGreaterThan(SearchParam):
    """
    Search parameter to filter for values greater than the filter value (`column > value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column > value


class SearchParamGreaterOrEqual(SearchParam):
    """
    Search parameter to filter for values greater than or equal to the filter value (`column >= value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column >= value


class SearchParamLessThan(SearchParam):
    """
    Search parameter to filter for values less than the filter value (`column < value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column < value


class SearchParamLessOrEqual(SearchParam):
    """
    Search parameter to filter for values less than or equal to the filter value (`column <= value`).
    """

    @staticmethod
    def sqlalchemy_filter(column: ColumnElement, value: Any) -> ColumnElement:
        return column <= value


class SearchParamSince(SearchParamGreaterOrEqual):
    """
    Alias for SearchParamGreaterOrEqual. Search parameter to filter for values (e.g. datetimes) since the filter value.
    """
    pass


class SearchParamUntil(SearchParamLessOrEqual):
    """
    Alias for SearchParamLessOrEqual. Search parameter to filter for values (e.g. datetimes) until the filter value.
    """
    pass
